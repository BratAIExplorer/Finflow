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

    def __init__(self, credentials: dict):
        super().__init__(credentials)
        self._access_token: Optional[str] = None
        self._token_date: Optional[date] = None

    def _session_is_fresh(self) -> bool:
        # mStock tokens expire at midnight of the day they were issued
        return self._access_token is not None and self._token_date == datetime.now().date()

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

        self._access_token = token
        self._token_date = datetime.now().date()

    def fetch_holdings(self) -> list[RawHolding]:
        self.ensure_session()
        api_key = self.credentials["api_key"]
        headers = {
            "X-Mirae-Version": "1",
            "Authorization": f"Bearer {self._access_token}",
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
            "Authorization": f"Bearer {self._access_token}",
            "X-PrivateKey": api_key,
        }
        try:
            with httpx.Client(timeout=15) as client:
                resp = client.get(FUNDS_URL, headers=headers)
                resp.raise_for_status()
                payload = resp.json()
        except httpx.HTTPError as e:
            raise BrokerConnectionError(f"mStock funds fetch failed: {e}") from e

        data = payload.get("data", {})
        # The key we found earlier is AVAILABLE_BALANCE
        balance_str = data.get("AVAILABLE_BALANCE", "0")
        try:
            return float(balance_str)
        except ValueError:
            return 0.0
