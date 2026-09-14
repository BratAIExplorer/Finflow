"""Trend-accuracy tracking: record each trend call for every held stock, then
grade older calls against what the price actually did.

record_snapshot() is called both by the daily scheduled job (below) and by
the manual "sync now" route (routers/holdings.py) — every sync or scheduled
refresh writes a row, so intraday trend flips are captured too, not just the
once-a-day scheduled snapshot. All of it reuses
pricing.compute_signals()/classify_trend() — the exact calculation the
dashboard already uses; this module only adds the write-to-history +
grading step, no new price/indicator logic.
"""
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from .. import pricing
from ..models import Holding, TrendSnapshot

logger = logging.getLogger(__name__)

_WINDOWS = (1, 7, 30)  # days


def record_snapshot(db: Session, holding: Holding, signals: pricing.PriceSignals) -> TrendSnapshot:
    """Build (and add, uncommitted) one TrendSnapshot row from already-computed
    signals. Shared by the daily job and the manual "sync now" route so both
    write history the same way — holding.id must already be flushed/assigned
    before calling this."""
    trend = pricing.classify_trend(signals.rsi_14, signals.macd_hist)
    snap = TrendSnapshot(
        holding_id=holding.id,
        symbol=holding.symbol,
        exchange=holding.exchange,
        captured_at=datetime.utcnow(),
        price_at_capture=signals.last_price,
        rsi_14=signals.rsi_14,
        macd_hist=signals.macd_hist,
        trend_label=trend["label"],
        direction=trend["direction"],
    )
    db.add(snap)
    return snap


def snapshot_all_holdings(db: Session) -> int:
    """Insert one TrendSnapshot per Holding using today's signals. Returns the
    count written. Best-effort per holding — a Yahoo failure for one symbol
    (delisted, wrong suffix) must not stop the rest from being recorded."""
    written = 0
    for holding in db.query(Holding).all():
        try:
            signals = pricing.compute_signals(holding.symbol, holding.exchange)
        except ValueError as e:
            logger.warning("trend snapshot skipped for %s: %s", holding.symbol, e)
            continue

        record_snapshot(db, holding, signals)
        written += 1

    db.commit()
    return written


def grade_pending_snapshots(db: Session) -> int:
    """For every snapshot with a due, ungraded window, grade it against the
    actual close on/after the window's due trading date. Returns the count of
    (snapshot, window) pairs graded.

    Grades against a specific historical close, not "today's price" — grading
    by calendar days against the most recent live price is wrong on a
    weekend/holiday: on a Saturday, compute_signals() returns Friday's close,
    so a snapshot captured that same Friday would get graded one calendar day
    later against the identical price it started from, scoring a false miss
    on every single "up" call regardless of merit. Fixed by looking up the
    close on the first trading day at/after the due date instead.
    """
    graded = 0
    # Only rows still missing at least one grade: hit_30d is the longest
    # window, so once it's set nothing is left to do for that row — without
    # this filter every fully-graded snapshot gets re-fetched from Yahoo
    # forever, and the job gets slower every day it runs.
    pending = (
        db.query(TrendSnapshot)
        .filter(TrendSnapshot.direction != "flat")
        .filter(TrendSnapshot.hit_30d.is_(None))
        .all()
    )

    history_cache: dict[tuple[str, str], object] = {}

    for snap in pending:
        due_windows = [
            days for days in _WINDOWS
            if getattr(snap, f"hit_{days}d") is None
            and datetime.utcnow() >= snap.captured_at + timedelta(days=days)
        ]
        if not due_windows:
            continue

        key = (snap.symbol, snap.exchange)
        if key not in history_cache:
            try:
                history_cache[key] = pricing.fetch_daily_history(snap.symbol, snap.exchange, period="2y")
            except ValueError as e:
                logger.warning("grading skipped for %s: %s", snap.symbol, e)
                history_cache[key] = None
        df = history_cache[key]
        if df is None:
            continue

        idx = df.index.tz_localize(None) if df.index.tz is not None else df.index
        for days in due_windows:
            target_date = (snap.captured_at + timedelta(days=days)).date()
            on_or_after = df.loc[idx.date >= target_date]
            if on_or_after.empty:
                continue  # due date is beyond the fetched history window; leave pending
            price_at_target = float(on_or_after["Close"].iloc[0])
            hit = price_at_target > snap.price_at_capture if snap.direction == "up" else price_at_target < snap.price_at_capture
            setattr(snap, f"price_{days}d", price_at_target)
            setattr(snap, f"hit_{days}d", bool(hit))
            graded += 1

    db.commit()
    return graded
