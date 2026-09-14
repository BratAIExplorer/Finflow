"""Offline tests for the daily trend-accuracy job (backend/jobs/trend_snapshot.py).
No real Yahoo calls — pricing.compute_signals is monkeypatched throughout.

Run with: pytest backend/tests/test_trend_snapshot.py -v
"""
import os
from datetime import datetime, timedelta

from cryptography.fernet import Fernet

os.environ.setdefault("APP_ENCRYPTION_KEY", Fernet.generate_key().decode())

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from backend import pricing
from backend.models import Base, Holding, TrendSnapshot
from backend.jobs.trend_snapshot import snapshot_all_holdings, grade_pending_snapshots


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

def test_grade_pending_marks_hit_for_correct_up_call(monkeypatch, db):
    holding = _add_holding(db)
    snap = TrendSnapshot(
        holding_id=holding.id, symbol=holding.symbol, exchange=holding.exchange,
        captured_at=datetime.utcnow() - timedelta(days=8),
        price_at_capture=1000.0, rsi_14=65.0, macd_hist=0.8,
        trend_label="Very Bullish", direction="up",
    )
    db.add(snap)
    db.commit()

    monkeypatch.setattr(pricing, "compute_signals", lambda symbol, exchange: pricing.PriceSignals(
        last_price=1100.0, week52_high=1300.0, week52_low=900.0, rsi_14=65.0, macd_hist=0.8,
    ))

    graded = grade_pending_snapshots(db)

    db.refresh(snap)
    assert graded == 2  # 1d and 7d windows are due at 8 days out; 30d is not
    assert snap.hit_1d is True
    assert snap.hit_7d is True
    assert snap.hit_30d is None  # still pending


def test_grade_pending_marks_miss_when_price_moved_wrong_way(monkeypatch, db):
    holding = _add_holding(db)
    snap = TrendSnapshot(
        holding_id=holding.id, symbol=holding.symbol, exchange=holding.exchange,
        captured_at=datetime.utcnow() - timedelta(days=2),
        price_at_capture=1000.0, rsi_14=65.0, macd_hist=0.8,
        trend_label="Bullish", direction="up",
    )
    db.add(snap)
    db.commit()

    monkeypatch.setattr(pricing, "compute_signals", lambda symbol, exchange: pricing.PriceSignals(
        last_price=900.0, week52_high=1300.0, week52_low=900.0, rsi_14=40.0, macd_hist=-0.2,
    ))

    grade_pending_snapshots(db)

    db.refresh(snap)
    assert snap.hit_1d is False
    assert snap.hit_7d is None  # window not due yet


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
    monkeypatch.setattr(pricing, "compute_signals", lambda symbol, exchange: called.append(1) or pricing.PriceSignals(
        last_price=1000.0, week52_high=1300.0, week52_low=900.0, rsi_14=50.0, macd_hist=0.0,
    ))

    grade_pending_snapshots(db)

    assert called == []  # never priced — flat snapshots are excluded up front
    db.refresh(snap)
    assert snap.hit_1d is None
