"""
Offline tests for the broker-holdings feature — no real broker credentials or
network calls. Covers: RSI/MACD math, the trend rule table, the plain-language
flags, the crypto round-trip, and each connector's JSON-parsing logic (mocked
HTTP responses shaped like the brokers' documented schemas).

Run with: pytest backend/tests/test_holdings.py -v
"""
import os
import json
from datetime import date, timedelta

import pandas as pd
import pytest
from cryptography.fernet import Fernet

os.environ.setdefault("APP_ENCRYPTION_KEY", Fernet.generate_key().decode())

from backend import pricing
from backend import plain_flags
from backend import crypto_utils
from backend.brokers.base import RawHolding


# ---------- pricing.py ----------

def test_rsi_all_gains_is_high():
    closes = pd.Series([100 + i for i in range(30)], dtype=float)  # strictly rising
    rsi = pricing.compute_rsi(closes)
    assert rsi is not None and rsi > 90


def test_rsi_all_losses_is_low():
    closes = pd.Series([200 - i for i in range(30)], dtype=float)  # strictly falling
    rsi = pricing.compute_rsi(closes)
    assert rsi is not None and rsi < 10


def test_rsi_too_short_returns_none():
    closes = pd.Series([100, 101, 102], dtype=float)
    assert pricing.compute_rsi(closes, period=14) is None


def test_macd_hist_positive_on_uptrend():
    closes = pd.Series([100 + i * 0.8 for i in range(60)], dtype=float)
    hist = pricing.compute_macd_hist(closes)
    assert hist is not None and hist > 0


def test_macd_hist_negative_on_downtrend():
    closes = pd.Series([200 - i * 0.8 for i in range(60)], dtype=float)
    hist = pricing.compute_macd_hist(closes)
    assert hist is not None and hist < 0


@pytest.mark.parametrize("rsi,macd,expected_label", [
    (70, 1.0, "Very Bullish"),
    (57, 0.0, "Bullish"),
    (50, 0.05, "Bullish"),   # any positive MACD alone triggers Bullish per the rule table
    (50, 0.0, "Neutral"),
    (43, -0.1, "Bearish"),
    (35, -1.0, "Very Bearish"),
])
def test_classify_trend_rule_table(rsi, macd, expected_label):
    result = pricing.classify_trend(rsi, macd)
    assert result["label"] == expected_label


def test_classify_trend_handles_missing_data():
    result = pricing.classify_trend(None, None)
    assert result["label"] == "Unknown"


# ---------- plain_flags.py ----------

def test_long_term_flag_over_one_year():
    flag = plain_flags.holding_period_flag(date.today() - timedelta(days=400))
    assert flag.code == "long_term"


def test_short_term_flag_under_one_year():
    flag = plain_flags.holding_period_flag(date.today() - timedelta(days=100))
    assert flag.code == "short_term"


def test_near_high_flag():
    flag = plain_flags.price_position_flag(last_price=98, avg_buy_price=80, week52_high=100, week52_low=60)
    assert flag.code == "near_high"


def test_below_cost_flag():
    flag = plain_flags.price_position_flag(last_price=60, avg_buy_price=100, week52_high=120, week52_low=55)
    assert flag.code == "below_cost"


def test_no_flag_in_the_middle():
    flag = plain_flags.price_position_flag(last_price=90, avg_buy_price=85, week52_high=120, week52_low=60)
    assert flag is None


# ---------- crypto_utils.py ----------

def test_credentials_round_trip():
    original = {"api_key": "abc123", "username": "dad@example.com", "totp_secret": "JBSWY3DPEHPK3PXP"}
    encrypted = crypto_utils.encrypt_credentials(original)
    assert encrypted != json.dumps(original)  # actually encrypted, not just re-serialized
    assert crypto_utils.decrypt_credentials(encrypted) == original


# ---------- mstock connector parsing (mocked HTTP) ----------

class _FakeResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

    def json(self):
        return self._json


class _FakeClient:
    """Stands in for httpx.Client — records calls, returns queued fake responses."""
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def post(self, url, headers=None, data=None):
        self.calls.append(("POST", url, data))
        return self._responses.pop(0)

    def get(self, url, headers=None):
        self.calls.append(("GET", url, headers))
        return self._responses.pop(0)


def test_mstock_fetch_holdings_parses_and_filters_zero_qty(monkeypatch):
    from backend.brokers import mstock

    login_resp = _FakeResponse({"data": {}})
    totp_resp = _FakeResponse({"data": {"access_token": "fake-jwt"}})
    holdings_resp = _FakeResponse({
        "data": [
            {"tradingsymbol": "HDFCBANK", "exchange": "NSE", "quantity": 120, "averageprice": 1485.0, "isin": "INE001"},
            {"tradingsymbol": "SOLDOUT", "exchange": "NSE", "quantity": 0, "averageprice": 50.0},
        ]
    })
    fake_client = _FakeClient([login_resp, totp_resp, holdings_resp])
    monkeypatch.setattr(mstock.httpx, "Client", lambda timeout=15: fake_client)
    monkeypatch.setattr(mstock.pyotp, "TOTP", lambda secret: type("T", (), {"now": lambda self: "111111"})())

    connector = mstock.MStockConnector({
        "api_key": "k", "username": "u", "password": "p", "totp_secret": "s",
    })
    holdings = connector.fetch_holdings()

    assert len(holdings) == 1
    assert holdings[0] == RawHolding(
        symbol="HDFCBANK", exchange="NSE", quantity=120.0, avg_buy_price=1485.0,
        currency="INR", isin="INE001", first_buy_date=None,
    )
    # session_state now holds the token — this is what the router persists to
    # UserPlugin.config so the next sync doesn't re-authenticate via TOTP.
    assert connector.session_state["access_token"] == "fake-jwt"


def test_mstock_fetch_funds_sums_segments_from_list_response(monkeypatch):
    """Confirmed live shape (Sep 2026): 'data' is a list of per-segment dicts,
    not a single dict — fetch_funds must sum AVAILABLE_BALANCE across them."""
    from datetime import datetime
    from backend.brokers import mstock

    funds_resp = _FakeResponse({
        "data": [
            {"SEG": "CAPITAL", "AVAILABLE_BALANCE": "246967.77"},
            {"SEG": "COMMODITY", "AVAILABLE_BALANCE": "1000.00"},
        ]
    })
    fake_client = _FakeClient([funds_resp])
    monkeypatch.setattr(mstock.httpx, "Client", lambda timeout=15: fake_client)

    connector = mstock.MStockConnector(
        {"api_key": "k", "username": "u", "password": "p", "totp_secret": "s"},
        session_state={"access_token": "cached-jwt", "access_token_date": datetime.now().date().isoformat()},
    )
    assert connector.fetch_funds() == pytest.approx(247967.77)


def test_mstock_skips_totp_when_session_state_is_fresh(monkeypatch):
    from datetime import datetime
    from backend.brokers import mstock

    holdings_resp = _FakeResponse({"data": []})
    fake_client = _FakeClient([holdings_resp])  # only the holdings call — no login/totp call queued
    monkeypatch.setattr(mstock.httpx, "Client", lambda timeout=15: fake_client)

    connector = mstock.MStockConnector(
        {"api_key": "k", "username": "u", "password": "p", "totp_secret": "s"},
        session_state={"access_token": "cached-jwt", "access_token_date": datetime.now().date().isoformat()},
    )
    connector.fetch_holdings()  # would raise IndexError popping an empty response queue if it re-authenticated

    assert connector.session_state["access_token"] == "cached-jwt"


def test_zerodha_fetch_holdings_requires_session_first():
    from backend.brokers.zerodha import ZerodhaConnector
    from backend.brokers.base import BrokerConnectionError

    connector = ZerodhaConnector({"api_key": "k", "api_secret": "s", "redirect_url": "r"})
    with pytest.raises(BrokerConnectionError):
        connector.fetch_holdings()  # no access_token yet — must fail loudly, not silently return []


def test_zerodha_fetch_holdings_parses_with_valid_session(monkeypatch):
    from backend.brokers import zerodha

    holdings_resp = _FakeResponse({
        "data": [
            {"tradingsymbol": "TATAMOTORS", "exchange": "NSE", "quantity": 300, "average_price": 612.0, "isin": "INE002"},
        ]
    })
    fake_client = _FakeClient([holdings_resp])
    monkeypatch.setattr(zerodha.httpx, "Client", lambda timeout=15: fake_client)

    from datetime import datetime
    connector = zerodha.ZerodhaConnector(
        {"api_key": "k", "api_secret": "s", "redirect_url": "r"},
        session_state={"access_token": "tok", "access_token_date": datetime.now().date().isoformat()},
    )
    holdings = connector.fetch_holdings()
    assert holdings[0].symbol == "TATAMOTORS"
    assert holdings[0].quantity == 300.0
