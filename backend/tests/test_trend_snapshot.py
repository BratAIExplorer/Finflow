"""Offline tests for the daily trend-accuracy job (backend/jobs/trend_snapshot.py).
No real Yahoo calls — pricing.compute_signals is monkeypatched throughout.

Run with: pytest backend/tests/test_trend_snapshot.py -v
"""
import os
from datetime import datetime, timedelta

from cryptography.fernet import Fernet

os.environ.setdefault("APP_ENCRYPTION_KEY", Fernet.generate_key().decode())

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from backend import pricing
from backend.models import Base, Holding, TrendSnapshot
from backend.jobs.trend_snapshot import snapshot_all_holdings, grade_pending_snapshots, record_snapshot


def _history_df(price_by_date: dict) -> pd.DataFrame:
    """A minimal fetch_daily_history-shaped frame: DatetimeIndex -> Close."""
    dates = sorted(price_by_date)
    return pd.DataFrame({"Close": [price_by_date[d] for d in dates]}, index=pd.DatetimeIndex(dates))


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def _add_holding(db, symbol="HDFCBANK", exchange="NSE"):
    h = Holding(plugin_id="p1", user_id="u1", symbol=symbol, exchange=exchange,
                quantity=10, avg_buy_price=1000.0)
    db.add(h)
    db.commit()
    return h


# ---------- snapshot_all_holdings ----------

def test_snapshot_writes_one_row_per_holding(monkeypatch, db):
    _add_holding(db)
    monkeypatch.setattr(pricing, "compute_signals", lambda symbol, exchange: pricing.PriceSignals(
        last_price=1200.0, week52_high=1300.0, week52_low=900.0, rsi_14=65.0, macd_hist=0.8,
    ))

    written = snapshot_all_holdings(db)

    assert written == 1
    snap = db.query(TrendSnapshot).one()
    assert snap.trend_label == "Very Bullish"
    assert snap.direction == "up"
    assert snap.price_at_capture == 1200.0


def test_snapshot_skips_holding_on_missing_price_data(monkeypatch, db):
    _add_holding(db, symbol="DELISTED")

    def _raise(symbol, exchange):
        raise ValueError("No price history found for DELISTED.NS")
    monkeypatch.setattr(pricing, "compute_signals", _raise)

    written = snapshot_all_holdings(db)

    assert written == 0
    assert db.query(TrendSnapshot).count() == 0


# ---------- grade_pending_snapshots ----------

def test_grade_pending_uses_the_due_dates_own_close_not_todays_price(monkeypatch, db):
    """The real bug: grading against 'today's price' for every window is wrong
    whenever the price moved between the due date and today. Here the 7-day
    price (990) is a genuine miss for an "up" call, but the price 'today'
    (1200) would make it look like a hit if graded against the wrong date —
    exactly what the old (fetch_daily_history-less) implementation did."""
    holding = _add_holding(db)
    captured_at = datetime.utcnow() - timedelta(days=8)
    snap = TrendSnapshot(
        holding_id=holding.id, symbol=holding.symbol, exchange=holding.exchange,
        captured_at=captured_at, price_at_capture=1000.0,
        rsi_14=65.0, macd_hist=0.8, trend_label="Very Bullish", direction="up",
    )
    db.add(snap)
    db.commit()

    history = _history_df({
        captured_at: 1000.0,
        captured_at + timedelta(days=1): 1010.0,   # 1d-out price: a real hit
        captured_at + timedelta(days=7): 990.0,    # 7d-out price: a real miss
        datetime.utcnow(): 1200.0,                 # "today": would wrongly look like a hit for both
    })
    monkeypatch.setattr(pricing, "fetch_daily_history", lambda symbol, exchange, period="2y": history)

    graded = grade_pending_snapshots(db)

    db.refresh(snap)
    assert graded == 2  # 1d and 7d due at 8 days out; 30d is not
    assert snap.hit_1d is True   # graded against 1010, correctly a hit
    assert snap.hit_7d is False  # graded against 990, correctly a miss -- not today's 1200
    assert snap.hit_30d is None  # still pending


def test_grade_pending_finds_next_trading_day_when_due_date_has_no_bar(monkeypatch, db):
    """Weekend/holiday case: the due calendar date itself has no trading bar
    (e.g. it's a Saturday). Must fall through to the next available trading
    day's close, not silently compare a stale price to itself."""
    holding = _add_holding(db)
    captured_at = datetime.utcnow() - timedelta(days=2)
    snap = TrendSnapshot(
        holding_id=holding.id, symbol=holding.symbol, exchange=holding.exchange,
        captured_at=captured_at, price_at_capture=1000.0,
        rsi_14=65.0, macd_hist=0.8, trend_label="Bullish", direction="up",
    )
    db.add(snap)
    db.commit()

    due_date = captured_at + timedelta(days=1)  # the 1d window's due calendar date
    history = _history_df({
        captured_at: 1000.0,
        due_date + timedelta(days=1): 1050.0,  # due_date itself has NO bar; next trading day does
    })
    monkeypatch.setattr(pricing, "fetch_daily_history", lambda symbol, exchange, period="2y": history)

    grade_pending_snapshots(db)

    db.refresh(snap)
    assert snap.hit_1d is True     # found via the next available trading day (1050 > 1000)
    assert snap.price_1d == 1050.0


def test_grade_pending_skips_fully_graded_snapshots_without_refetching(monkeypatch, db):
    """Once hit_30d is set there's nothing left to grade for that row — it
    must not even show up in the query, let alone trigger a Yahoo refetch.
    Without this, the job re-prices every historical snapshot forever."""
    holding = _add_holding(db)
    snap = TrendSnapshot(
        holding_id=holding.id, symbol=holding.symbol, exchange=holding.exchange,
        captured_at=datetime.utcnow() - timedelta(days=40), price_at_capture=1000.0,
        trend_label="Bullish", direction="up",
        hit_1d=True, price_1d=1010.0, hit_7d=True, price_7d=1020.0,
        hit_30d=True, price_30d=1030.0,
    )
    db.add(snap)
    db.commit()

    calls = []
    def _tracked_fetch(symbol, exchange, period="2y"):
        calls.append(symbol)
        raise AssertionError("should never be called for a fully-graded snapshot")
    monkeypatch.setattr(pricing, "fetch_daily_history", _tracked_fetch)

    graded = grade_pending_snapshots(db)

    assert graded == 0
    assert calls == []


def test_grade_pending_leaves_window_pending_when_not_due_yet(monkeypatch, db):
    holding = _add_holding(db)
    captured_at = datetime.utcnow() - timedelta(days=2)
    snap = TrendSnapshot(
        holding_id=holding.id, symbol=holding.symbol, exchange=holding.exchange,
        captured_at=captured_at, price_at_capture=1000.0,
        trend_label="Bullish", direction="up",
    )
    db.add(snap)
    db.commit()

    history = _history_df({captured_at: 1000.0, captured_at + timedelta(days=1): 900.0})
    monkeypatch.setattr(pricing, "fetch_daily_history", lambda symbol, exchange, period="2y": history)

    grade_pending_snapshots(db)

    db.refresh(snap)
    assert snap.hit_1d is False  # 900 < 1000, correctly a miss for an "up" call
    assert snap.hit_7d is None   # window not due yet at 2 days out


# ---------- record_snapshot (used by manual "sync now", not just the daily job) ----------

def test_record_snapshot_works_for_a_brand_new_holding_before_commit(db):
    """Mirrors routers/holdings.py's sync path: a new Holding is db.add()-ed,
    flushed (to get its id), then record_snapshot is called immediately —
    proving a manual sync writes history too, not just the scheduled job."""
    holding = Holding(plugin_id="p1", user_id="u1", symbol="TCS", exchange="NSE",
                       quantity=5, avg_buy_price=3000.0)
    db.add(holding)
    db.flush()
    assert holding.id is not None  # sanity: flush assigned the uuid default

    signals = pricing.PriceSignals(last_price=3200.0, week52_high=3300.0,
                                    week52_low=2800.0, rsi_14=58.0, macd_hist=0.3)
    record_snapshot(db, holding, signals)
    db.commit()

    snap = db.query(TrendSnapshot).filter(TrendSnapshot.holding_id == holding.id).one()
    assert snap.trend_label == "Bullish"
    assert snap.price_at_capture == 3200.0


def test_multiple_syncs_same_day_write_multiple_rows(db):
    """Per user decision: refreshing more than once a day should capture each
    call, not just one-per-day — so intraday trend flips aren't lost."""
    holding = _add_holding(db)
    signals_a = pricing.PriceSignals(last_price=1000.0, week52_high=1100.0,
                                      week52_low=900.0, rsi_14=62.0, macd_hist=0.6)
    signals_b = pricing.PriceSignals(last_price=980.0, week52_high=1100.0,
                                      week52_low=900.0, rsi_14=38.0, macd_hist=-0.6)
    record_snapshot(db, holding, signals_a)
    record_snapshot(db, holding, signals_b)
    db.commit()

    snaps = db.query(TrendSnapshot).filter(TrendSnapshot.holding_id == holding.id).all()
    assert len(snaps) == 2
    assert {s.trend_label for s in snaps} == {"Very Bullish", "Very Bearish"}


def test_grade_pending_ignores_neutral_snapshots(monkeypatch, db):
    holding = _add_holding(db)
    snap = TrendSnapshot(
        holding_id=holding.id, symbol=holding.symbol, exchange=holding.exchange,
        captured_at=datetime.utcnow() - timedelta(days=8),
        price_at_capture=1000.0, rsi_14=50.0, macd_hist=0.0,
        trend_label="Neutral", direction="flat",
    )
    db.add(snap)
    db.commit()

    called = []
    def _tracked_fetch(symbol, exchange, period="2y"):
        called.append(1)
        raise AssertionError("flat/Neutral snapshots must never be priced")
    monkeypatch.setattr(pricing, "fetch_daily_history", _tracked_fetch)

    grade_pending_snapshots(db)

    assert called == []  # never priced — flat snapshots are excluded up front
    db.refresh(snap)
    assert snap.hit_1d is None
