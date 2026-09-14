"""Daily trend-accuracy tracking: record each day's trend call for every held
stock, then grade older calls against what the price actually did.

Both functions reuse pricing.compute_signals()/classify_trend() — the exact
same calculation the manual "sync now" button and the dashboard already use
(see routers/holdings.py). This module only adds the write-to-history +
grading step; it introduces no new price/indicator logic.
"""
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from .. import pricing
from ..models import Holding, TrendSnapshot

logger = logging.getLogger(__name__)

_WINDOWS = (1, 7, 30)  # days


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

        trend = pricing.classify_trend(signals.rsi_14, signals.macd_hist)
        db.add(TrendSnapshot(
            holding_id=holding.id,
            symbol=holding.symbol,
            exchange=holding.exchange,
            captured_at=datetime.utcnow(),
            price_at_capture=signals.last_price,
            rsi_14=signals.rsi_14,
            macd_hist=signals.macd_hist,
            trend_label=trend["label"],
            direction=trend["direction"],
        ))
        written += 1

    db.commit()
    return written


def grade_pending_snapshots(db: Session) -> int:
    """For every snapshot with a due, ungraded window, fetch the current price
    and record whether the call's direction was correct. Returns the count of
    (snapshot, window) pairs graded."""
    graded = 0
    pending = db.query(TrendSnapshot).filter(TrendSnapshot.direction != "flat").all()

    for snap in pending:
        try:
            # ponytail: grades against *today's* price, not the exact close on the
            # window's due date. Fine since this job runs daily (at most ~1 day of
            # drift); revisit with fetch_daily_history date-lookup if the job ever
            # runs less often than the shortest window (1 day).
            current_price = pricing.compute_signals(snap.symbol, snap.exchange).last_price
        except ValueError as e:
            logger.warning("grading skipped for %s: %s", snap.symbol, e)
            continue
        if current_price is None:
            continue

        hit = current_price > snap.price_at_capture if snap.direction == "up" else current_price < snap.price_at_capture

        for days in _WINDOWS:
            hit_col = f"hit_{days}d"
            if getattr(snap, hit_col) is not None:
                continue  # already graded
            if datetime.utcnow() < snap.captured_at + timedelta(days=days):
                continue  # window hasn't elapsed yet
            setattr(snap, f"price_{days}d", current_price)
            setattr(snap, hit_col, hit)
            graded += 1

    db.commit()
    return graded
