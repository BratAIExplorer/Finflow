"""
mStock (Mirae Asset) connector — Trading API is free, but the access token
still expires daily ("valid till 12:00 AM of generated day" per mStock's docs).
Unlike Zerodha, mStock's login accepts a TOTP code directly over the API
(no browser redirect), so this connector can regenerate its own session with
no human involved, as long as TOTP is enabled on the account and its secret
is stored (encrypted) in UserPlugin.credentials_encrypted.

credentials dict shape:
    {
        "api_key": "...",        # from mstock.com/trading-api
        "username": "...",       # mStock client ID
        "password": "...",
        "totp_secret": "...",    # the base32 secret shown when enabling TOTP — NOT a one-time code
    }

⚠ CONFIRM-BEFORE-LIVE: the exact field names in the /session/verifytotp response
(access_token vs enctoken vs something else) are not fully documented publicly
as of this build — the parsing below tries the field names mStock's own docs
use elsewhere (access_token) with a fallback list. First real login must be
checked against the actual JSON returned (see backend/tests/test_mstock_connector.py
for how to do that safely) before this touches a real account.
"""
import binascii
from datetime import datetime, date
from typing import Optional

import httpx
import pyotp

from .base import BrokerConnector, RawHolding, BrokerConnectionError

BASE_URL = "https://api.mstock.trade"
LOGIN_URL = f"{BASE_URL}/openapi/typea/connect/login"
VERIFY_TOTP_URL = f"{BASE_URL}/openapi/typea/session/verifytotp"
HOLDINGS_URL = f"{BASE_URL}/openapi/typeb/portfolio/holdings"
FUNDS_URL = f"{BASE_URL}/openapi/typea/user/fundsummary"

# Response JSON may use any of these keys for the session token depending on
# API version/typeA vs typeB quirks — first match wins.
_TOKEN_FIELD_CANDIDATES = ("access_token", "enctoken", "jwtToken", "token")


class MStockConnector(BrokerConnector):
    broker_name = "mstock"

    def __init__(self, credentials: dict, session_state: Optional[dict] = None):
        """session_state is UserPlugin.config — where the daily access_token lives,
        same pattern as ZerodhaConnector. Pass the current value in; after
        ensure_session() the caller must persist self.session_state back to
        UserPlugin.config, or this re-authenticates via TOTP on every sync."""
        super().__init__(credentials)
        self.session_state = dict(session_state or {})

    def _session_is_fresh(self) -> bool:
        # mStock tokens expire at midnight of the day they were issued
        token = self.session_state.get("access_token")
        token_date = self.session_state.get("access_token_date")
        if not token or not token_date:
            return False
        return token_date == datetime.now().date().isoformat()

    def ensure_session(self) -> None:
        if self._session_is_fresh():
            return

        api_key = self.credentials.get("api_key")
        username = self.credentials.get("username")
        password = self.credentials.get("password")
        totp_secret = self.credentials.get("totp_secret")
        if not all([api_key, username, password, totp_secret]):
            raise BrokerConnectionError(
                "mStock credentials incomplete — need api_key, username, password, totp_secret."
            )

        headers = {"X-Mirae-Version": "1", "Content-Type": "application/x-www-form-urlencoded"}

        try:
            with httpx.Client(timeout=15) as client:
                clean_totp_secret = totp_secret.strip().replace(" ", "").replace("-", "").upper()
                try:
                    totp_code = pyotp.TOTP(clean_totp_secret).now()
                except binascii.Error:
                    raise BrokerConnectionError(
                        "totp_secret isn't valid base32 (letters A-Z and digits 2-7 only). "
                        "Re-check the value shown on mStock's TOTP setup page."
                    )
                
                # mStock often returns 502 Bad Gateway on /verifytotp if /login wasn't called first
                login_resp = client.post(
                    LOGIN_URL,
                    headers=headers,
                    data={"username": username, "password": password},
                )
                login_resp.raise_for_status()

                verify_resp = client.post(
                    VERIFY_TOTP_URL,
                    headers=headers,
                    data={"api_key": api_key, "totp": totp_code},
                )
                verify_resp.raise_for_status()
                payload = verify_resp.json()
        except httpx.HTTPError as e:
            raise BrokerConnectionError(f"mStock login failed: {e}") from e

        data = payload.get("data", payload)  # some mStock responses nest under "data"
        token = next((data[k] for k in _TOKEN_FIELD_CANDIDATES if data.get(k)), None)
        if not token:
            raise BrokerConnectionError(
                f"mStock login succeeded but no recognizable token field in response: {list(data.keys())}"
            )

        self.session_state = {
            "access_token": token,
            "access_token_date": datetime.now().date().isoformat(),
        }

    def fetch_holdings(self) -> list[RawHolding]:
        self.ensure_session()
        api_key = self.credentials["api_key"]
        headers = {
            "X-Mirae-Version": "1",
            "Authorization": f"Bearer {self.session_state['access_token']}",
            "X-PrivateKey": api_key,
        }
        try:
            with httpx.Client(timeout=15) as client:
                resp = client.get(HOLDINGS_URL, headers=headers)
                resp.raise_for_status()
                payload = resp.json()
        except httpx.HTTPError as e:
            raise BrokerConnectionError(f"mStock holdings fetch failed: {e}") from e

        rows = payload.get("data", [])
        holdings = []
        for row in rows:
            qty = float(row.get("quantity", 0) or 0)
            if qty <= 0:
                continue  # fully sold / zero-quantity rows aren't a current holding
            holdings.append(
                RawHolding(
                    symbol=row["tradingsymbol"],
                    exchange=row.get("exchange", "NSE"),
                    quantity=qty,
                    avg_buy_price=float(row.get("averageprice", 0) or 0),
                    isin=row.get("isin"),
                    currency="INR",
                    first_buy_date=None,  # mStock's holdings API doesn't return this — left for the user to see as "date unknown"
                )
            )
        return holdings

    def fetch_funds(self) -> float:
        self.ensure_session()
        api_key = self.credentials["api_key"]
        headers = {
            "X-Mirae-Version": "1",
            "Authorization": f"token {api_key}:{self.session_state['access_token']}",
            "X-PrivateKey": api_key,
        }
        try:
            with httpx.Client(timeout=15) as client:
                resp = client.get(FUNDS_URL, headers=headers)
                resp.raise_for_status()
                payload = resp.json()
        except httpx.HTTPError as e:
            raise BrokerConnectionError(f"mStock funds fetch failed: {e}") from e

        data = payload.get("data", [])
        # Confirmed shape (live payload, Sep 2026): a list with one dict per
        # trading segment (e.g. SEG "CAPITAL", possibly others like commodity/
        # F&O) — sum AVAILABLE_BALANCE across segments for total cash.
        if isinstance(data, dict):
            data = [data]  # tolerate a single-object response too
        total = 0.0
        for segment in data:
            if not isinstance(segment, dict):
                continue
            try:
                total += float(segment.get("AVAILABLE_BALANCE") or 0)
            except (ValueError, TypeError):
                continue
        return total
