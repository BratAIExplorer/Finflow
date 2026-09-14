"""Hermetic unit tests for Deepak's Market Board backend.

Covers:
- Watchlist management (thread-safe load, add, remove)
- Technical calculations (RSI, MACD, Verdict, verbal descriptors)
- News parsing (keyword tagging, sentiment, deduplication)
- FastAPI /board endpoints (GET, POST /refresh, POST /add, POST /remove)

Run with: pytest backend/tests/test_board.py -v
"""
import sqlite3
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from backend.board import data, news, watchlist
from backend.main import app
from backend.routers.auth import get_current_user
from backend.models import User


# ---------- Watchlist Tests ----------

def test_watchlist_add_and_remove(tmp_path, monkeypatch):
    test_file = tmp_path / "test_stocks.txt"
    monkeypatch.setattr(watchlist, "FILE", test_file)

    assert watchlist.load() == []

    watchlist.add("TATAPOWER", "Tata Power")
    watchlist.add("RELIANCE", "Reliance Industries")
    rows = watchlist.load()
    assert len(rows) == 2
    assert rows[0] == {"symbol": "TATAPOWER", "name": "Tata Power"}
    assert rows[1] == {"symbol": "RELIANCE", "name": "Reliance Industries"}

    # Duplicate add is ignored
    watchlist.add("TATAPOWER", "Tata Power Again")
    assert len(watchlist.load()) == 2

    # Remove symbol
    watchlist.remove("TATAPOWER")
    rows = watchlist.load()
    assert len(rows) == 1
    assert rows[0]["symbol"] == "RELIANCE"


# ---------- Data / Technicals Tests ----------

def test_data_rsi_calculation():
    # 40 days of rising prices -> high RSI
    closes = pd.Series([100 + i * 2 for i in range(40)], dtype=float)
    rsi_series = data._rsi(closes)
    rsi_val = round(float(rsi_series.iloc[-1]))
    assert rsi_val >= 90

    # 40 days of falling prices -> low RSI
    closes_fall = pd.Series([200 - i * 2 for i in range(40)], dtype=float)
    rsi_val_fall = round(float(data._rsi(closes_fall).iloc[-1]))
    assert rsi_val_fall <= 10


def test_data_rsi_word_descriptors():
    assert data._rsi_word(None)[0] == "Waiting for data"
    assert data._rsi_word(25)[0] == "Oversold — looks cheap"
    assert data._rsi_word(40)[0] == "Weak"
    assert data._rsi_word(50)[0] == "Neutral"
    assert data._rsi_word(65)[0] == "Getting expensive"
    assert data._rsi_word(75)[0] == "Overbought"


def test_data_macd_word_descriptors():
    assert data._macd_word(None, None)[0] == "Waiting for data"
    assert data._macd_word(0.0, 0.0)[0] == "Flat"
    assert data._macd_word(1.5, 1.0)[0] == "Rising — momentum up"
    assert data._macd_word(1.0, 1.5)[0] == "Positive"
    assert data._macd_word(-1.5, -1.0)[0] == "Falling — momentum down"
    assert data._macd_word(-1.0, -1.5)[0] == "Negative"


def test_data_one_calculation():
    # Construct a synthetic 60-day dataframe
    dates = pd.date_range("2026-01-01", periods=60)
    prices = [100.0 + i for i in range(60)]
    df = pd.DataFrame({"Close": prices}, index=dates)

    res = data._one("TESTSYM", "Test Company", df)
    assert res["symbol"] == "TESTSYM"
    assert res["name"] == "Test Company"
    assert res["price"] == f"₹{prices[-1]:,.2f}"
    assert res["dir"] == "up"
    assert res["verdict"]["big"] in ("Very Bullish", "Bullish")


def test_data_fetch_empty():
    rows, ok = data.fetch([])
    assert rows == []
    assert ok is True


def test_data_fetch_mocked(monkeypatch):
    dates = pd.date_range("2026-01-01", periods=60)
    prices = [100.0 + i for i in range(60)]
    fake_df = pd.DataFrame({"Close": prices}, index=dates)

    def mock_download(tickers, **kwargs):
        if len(tickers) == 1:
            return fake_df
        # MultiIndex for multiple tickers
        tuples = [(t, "Close") for t in tickers]
        cols = pd.MultiIndex.from_tuples(tuples)
        data_matrix = {c: prices for c in cols}
        return pd.DataFrame(data_matrix, index=dates)

    monkeypatch.setattr(data.yf, "download", mock_download)

    stocks = [{"symbol": "AAA", "name": "Triple A"}]
    rows, ok = data.fetch(stocks)
    assert len(rows) == 1
    assert rows[0]["symbol"] == "AAA"
    assert rows[0]["price"] == f"₹{prices[-1]:,.2f}"
    assert ok is True


# ---------- News Tests ----------

def test_news_sentiment():
    assert news._sentiment("Company reports record profit and dividend") == "pos"
    assert news._sentiment("Managing director resigns amid probe and loss") == "neg"
    assert news._sentiment("Company to hold meeting on upcoming initiatives") == "neu"


def test_news_material_keywords():
    low_order = "wins massive multi-crore defense order".lower()
    low_normal = "launches new website design".lower()
    assert any(w in low_order for w in news.MATERIAL) is True
    assert any(w in low_normal for w in news.MATERIAL) is False


def test_news_fetch_mocked(tmp_path, monkeypatch):
    test_db = tmp_path / "test_seen.sqlite"
    monkeypatch.setattr(news, "DB", test_db)

    fake_entry = {
        "title": "Tata Power wins Rs 1200 cr order - Economic Times",
        "published_parsed": (2026, 9, 14, 6, 30, 0, 0, 0, 0),
    }

    def mock_parse(url):
        return MagicMock(entries=[fake_entry])

    monkeypatch.setattr(news.feedparser, "parse", mock_parse)

    stocks = [{"symbol": "TATAPOWER", "name": "Tata Power"}]
    items, ok = news.fetch(stocks)
    assert len(items) == 1
    assert items[0]["symbol"] == "TATAPOWER"
    assert items[0]["important"] is True
    assert items[0]["cls"] == "pos"
    assert items[0]["source"] == "Economic Times"
    assert ok is True

    # Second fetch should deduplicate and return empty
    items2, ok2 = news.fetch(stocks)
    assert items2 == []


# ---------- Router Tests ----------

@pytest.fixture
def client():
    # Override auth to return a mock user
    mock_user = User(id="test-user-id", email="dad@example.com")
    app.dependency_overrides[get_current_user] = lambda: mock_user
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_current_user, None)


def test_board_router_get_and_refresh(client, monkeypatch):
    # Mock data.fetch and news.fetch to avoid network
    fake_rows = [{
        "symbol": "DEMO", "name": "Demo Co", "price": "₹100.00", "chg": "+1.0%",
        "dir": "up", "rsi": 55, "rsiW": ["Neutral", "mid"],
        "macdW": ["Positive", "good"],
        "verdict": {"key": "v-bull", "big": "Bullish", "sub": "▲ going up"},
        "held": False, "price_num": 100.0, "chg_num": 1.0, "rsi_num": 55,
        "macd_hist": 0.1, "trend_word": "Bullish", "trend_score": 1,
    }]
    fake_news = [{
        "id": "abc1", "symbol": "DEMO", "name": "Demo Co", "head": "Demo profit surge",
        "source": "ET", "time": "14 Sep 12:00", "cls": "pos", "important": True,
    }]

    from backend.routers import board
    monkeypatch.setattr(board.data, "fetch", lambda stocks: (fake_rows, True))
    monkeypatch.setattr(board.news, "fetch", lambda stocks: (fake_news, True))
    monkeypatch.setattr(board.export, "write", lambda rows, news_items: "/mock/desktop/MarketBoard")

    # GET /board/
    res = client.get("/board/")
    assert res.status_code == 200
    data_json = res.json()
    assert "stocks" in data_json
    assert "news" in data_json
    assert "ts" in data_json
    assert data_json["prices_ok"] is True

    # POST /board/refresh
    res_refresh = client.post("/board/refresh")
    assert res_refresh.status_code == 200
    assert res_refresh.json()["prices_ok"] is True


def test_board_router_add_and_remove(client, tmp_path, monkeypatch):
    from backend.routers import board

    test_file = tmp_path / "test_stocks.txt"
    test_file.write_text("DEMO | Demo Co\n", encoding="utf-8")
    monkeypatch.setattr(board.watchlist, "FILE", test_file)
    monkeypatch.setattr(board.data, "fetch", lambda stocks: ([], True))
    monkeypatch.setattr(board.news, "fetch", lambda stocks: ([], True))
    monkeypatch.setattr(board.export, "write", lambda rows, news_items: "")

    # Add stock
    res_add = client.post("/board/add", json={"symbol": "NEWSTOCK", "name": "New Stock Ltd"})
    assert res_add.status_code == 200
    symbols = [s["symbol"] for s in board.watchlist.load()]
    assert "NEWSTOCK" in symbols

    # Remove stock
    res_remove = client.post("/board/remove", json={"symbol": "NEWSTOCK"})
    assert res_remove.status_code == 200
    symbols_after = [s["symbol"] for s in board.watchlist.load()]
    assert "NEWSTOCK" not in symbols_after
