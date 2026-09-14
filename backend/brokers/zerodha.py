"""
Zerodha (Kite Connect) connector — free "Personal" API plan.

Free plan covers holdings/positions/funds (what this connector uses). It does
NOT cover Kite's own real-time WebSocket/historical-candle feed — that needs
the paid ₹500/month Connect plan, which this build deliberately avoids by
getting prices/RSI/MACD from a separate free source instead (see pricing.py).

Zerodha's session flow is browser-redirect based BY DESIGN (their security
model, not a missing feature) — there is no API-only login like mStock's TOTP
path. So this connector cannot refresh itself; it needs a once-a-day "one-click"
step from a human:

    1. GET  login_url(plugin)              -> a Zerodha login URL to open
    2. (person logs into Zerodha in their browser, gets redirected back with
       ?request_token=... in the URL)
    3. POST complete_login(plugin, request_token) -> exchanges it for a
       day-valid access_token, stored in UserPlugin.config (not the encrypted
       credentials — it's a short-lived token, not a long-term secret)

fetch_holdings() raises BrokerConnectionError telling the caller to redo step 1
if no fresh access_token is on file for today.

credentials dict shape:
    {
        "api_key": "...",       # from a Kite Connect app registered per Zerodha login
        "api_secret": "...",
        "redirect_url": "...",  # must match what's registered on the Kite Connect app
    }
"""
import hashlib
from datetime import datetime, date
from typing import Optional

import httpx

from .base import BrokerConnector, RawHolding, BrokerConnectionError

BASE_URL = "https://api.kite.trade"
LOGIN_BASE = "https://kite.zerodha.com/connect/login"


class ZerodhaConnector(BrokerConnector):
    broker_name = "zerodha"

    def __init__(self, credentials: dict, session_state: Optional[dict] = None):
        """session_state is UserPlugin.config — where the daily access_token lives.
        Pass the current value in; after complete_login() the caller must persist
        self.session_state back to UserPlugin.config."""
        super().__init__(credentials)
        self.session_state = dict(session_state or {})

    def login_url(self) -> str:
        api_key = self.credentials["api_key"]
        return f"{LOGIN_BASE}?api_key={api_key}&v=3"

    def complete_login(self, request_token: str) -> None:
        """Call this once, right after the person's browser redirects back with
        ?request_token=... . Stores the resulting access_token in self.session_state
        — the caller (routers/holdings.py) is responsible for saving that to the DB."""
        api_key = self.credentials["api_key"]
        api_secret = self.credentials["api_secret"]
        checksum = hashlib.sha256(f"{api_key}{request_token}{api_secret}".encode()).hexdigest()

        try:
            with httpx.Client(timeout=15) as client:
                resp = client.post(
                    f"{BASE_URL}/session/token",
                    data={"api_key": api_key, "request_token": request_token, "checksum": checksum},
                )
                resp.raise_for_status()
                payload = resp.json()
        except httpx.HTTPError as e:
            raise BrokerConnectionError(f"Zerodha login exchange failed: {e}") from e

        data = payload.get("data", payload)
        access_token = data.get("access_token")
        if not access_token:
            raise BrokerConnectionError(f"Zerodha login exchange returned no access_token: {data}")

        self.session_state = {
            "access_token": access_token,
            "access_token_date": datetime.now().date().isoformat(),
        }

    def _session_is_fresh(self) -> bool:
        token = self.session_state.get("access_token")
        token_date = self.session_state.get("access_token_date")
        if not token or not token_date:
            return False
        # Kite access tokens expire once a day; treat "issued today" as fresh.
        return token_date == datetime.now().date().isoformat()

    def ensure_session(self) -> None:
        if not self._session_is_fresh():
            raise BrokerConnectionError(
                "No valid Zerodha session for today — send the person to login_url(), "
                "then call complete_login() with the request_token from the redirect."
            )

    def fetch_holdings(self) -> list[RawHolding]:
        self.ensure_session()
        api_key = self.credentials["api_key"]
        access_token = self.session_state["access_token"]
        headers = {"Authorization": f"token {api_key}:{access_token}"}

        try:
            with httpx.Client(timeout=15) as client:
                resp = client.get(f"{BASE_URL}/portfolio/holdings", headers=headers)
                resp.raise_for_status()
                payload = resp.json()
        except httpx.HTTPError as e:
            raise BrokerConnectionError(f"Zerodha holdings fetch failed: {e}") from e

        rows = payload.get("data", [])
        holdings = []
        for row in rows:
            qty = float(row.get("quantity", 0) or 0)
            if qty <= 0:
                continue
            holdings.append(
                RawHolding(
                    symbol=row["tradingsymbol"],
                    exchange=row.get("exchange", "NSE"),
                    quantity=qty,
                    avg_buy_price=float(row.get("average_price", 0) or 0),
                    isin=row.get("isin"),
                    currency="INR",
                    first_buy_date=None,  # Kite's holdings endpoint doesn't return an original buy date
                )
            )
        return holdings
