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
from datetime import datetime, date, timedelta
from typing import Optional

import httpx
import pyotp

from .base import BrokerConnector, RawHolding, BrokerConnectionError

BASE_URL = "https://api.mstock.trade"
LOGIN_URL = f"{BASE_URL}/openapi/typea/connect/login"
VERIFY_TOTP_URL = f"{BASE_URL}/openapi/typea/session/verifytotp"
HOLDINGS_URL = f"{BASE_URL}/openapi/typeb/portfolio/holdings"
FUNDS_URL = f"{BASE_URL}/openapi/typea/user/fundsummary"
TRADES_URL = f"{BASE_URL}/openapi/typea/trades"

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

    def _fetch_trade_dates(self) -> dict[str, date]:
        """Queries mStock's /trades endpoint to auto-populate acquisition dates.
        Reconciles executions chronologically via FIFO so that the earliest active purchase
        lot determines first_buy_date.
        
        Silently returns {} on failure so holding synchronization is never disrupted.
        """
        api_key = self.credentials.get("api_key")
        access_token = self.session_state.get("access_token")
        if not api_key or not access_token:
            return {}

        today = datetime.now().date()
        from_date = (today - timedelta(days=365)).isoformat()
        to_date = today.isoformat()

        headers = {
            "X-Mirae-Version": "1",
            "Authorization": f"token {api_key}:{access_token}",
        }

        try:
            with httpx.Client(timeout=15) as client:
                resp = client.get(
                    TRADES_URL,
                    headers=headers,
                    params={"fromdate": from_date, "todate": to_date},
                )
                if resp.status_code != 200:
                    return {}
                payload = resp.json()
                trades_data = payload.get("data", [])
                return self._calculate_first_buy_dates(trades_data)
        except Exception:
            return {}

    @staticmethod
    def _calculate_first_buy_dates(trades_data: list[dict]) -> dict[str, date]:
        """Groups trades by symbol, sorts chronologically, executes FIFO deduction
        for sells, and returns {symbol: earliest_active_buy_date}."""
        trades_by_sym: dict[str, list[dict]] = {}
        for item in trades_data:
            sym = (item.get("tradingsymbol") or item.get("symbol") or item.get("SYMBOL") or "").strip().upper()
            if not sym:
                continue
            ts_str = (
                item.get("order_timestamp")
                or item.get("exchange_timestamp")
                or item.get("ORDER_DATE_TIME")
                or ""
            )
            d = None
            for fmt in ("%Y-%m-%d %H:%M:%S", "%d-%m-%Y %H:%M:%S", "%Y-%m-%d", "%d-%m-%Y"):
                try:
                    d = datetime.strptime(ts_str.strip(), fmt).date()
                    break
                except (ValueError, AttributeError):
                    continue
            if not d:
                continue

            action = (item.get("transaction_type") or item.get("BUY_SELL") or "BUY").strip().upper()
            qty = float(item.get("quantity") or item.get("QUANTITY") or 0)

            trades_by_sym.setdefault(sym, []).append({
                "action": action,
                "qty": qty,
                "date": d,
                "ts_raw": ts_str,
            })

        result: dict[str, date] = {}
        for sym, sym_trades in trades_by_sym.items():
            sym_trades.sort(key=lambda x: (x["date"], x["ts_raw"]))
            buy_lots: list[dict] = []
            for t in sym_trades:
                if t["action"] in ("BUY", "B"):
                    buy_lots.append({"qty": t["qty"], "date": t["date"]})
                elif t["action"] in ("SELL", "S"):
                    qty_to_sell = t["qty"]
                    for lot in buy_lots:
                        if lot["qty"] <= 0:
                            continue
                        if lot["qty"] >= qty_to_sell:
                            lot["qty"] -= qty_to_sell
                            qty_to_sell = 0
                            break
                        else:
                            qty_to_sell -= lot["qty"]
                            lot["qty"] = 0

            active_lots = [lot for lot in buy_lots if lot["qty"] > 0]
            if active_lots:
                result[sym] = active_lots[0]["date"]

        return result

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

        trade_dates = self._fetch_trade_dates()

        rows = payload.get("data", [])
        holdings = []
        for row in rows:
            qty = float(row.get("quantity", 0) or 0)
            if qty <= 0:
                continue  # fully sold / zero-quantity rows aren't a current holding
            sym = row["tradingsymbol"]
            norm_sym = sym.strip().upper()
            holdings.append(
                RawHolding(
                    symbol=sym,
                    exchange=row.get("exchange", "NSE"),
                    quantity=qty,
                    avg_buy_price=float(row.get("averageprice", 0) or 0),
                    isin=row.get("isin"),
                    currency="INR",
                    first_buy_date=trade_dates.get(norm_sym),
                )
            )
        return holdings

    def fetch_funds(self) -> float:
        self.ensure_session()
        api_key = self.credentials["api_key"]
        headers = {
            "X-Mirae-Version": "1",
            "Authorization": f"token {api_key}:{self.session_state['access_token']}",
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
