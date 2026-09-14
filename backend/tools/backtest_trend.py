"""Offline backtest: how accurate is pricing.classify_trend() historically? Also
tests two candidate improvements raised after the first (coin-flip) result —
a 200-day moving average regime filter, and relative momentum vs. Nifty 50 —
using the exact same no-lookahead, direction-only methodology.

Why this exists: the live trend_snapshots table (backend/jobs/trend_snapshot.py)
answers "was this call right?" but only after waiting 1/7/30 real days per
snapshot — weeks before there's enough data to trust. This script answers the
same question in one run using 2 years of Yahoo daily history already on hand,
with the exact same rule table and the exact same direction-only grading logic
already live in grade_pending_snapshots().

Honesty rule (same principle used in TradingBot/strategies/factor_backtest.py):
every day's RSI/MACD/ADX value must only use data up to and including that day
— never a future close. pandas .rolling()/.ewm() are strictly backward-looking
by construction, so computing the full indicator series once over the whole
history and reading off day t's value is equivalent to (but far faster than)
recomputing from scratch at every t — there is no lookahead here.

The RSI/MACD math below intentionally mirrors backend/pricing.py's
compute_rsi/compute_macd_hist (which only return the latest value, not a full
series) rather than refactoring those tested, live functions —
test_backtest_matches_live_pricing_functions in
backend/tests/test_backtest_trend.py cross-checks the two never drift apart.

ADX has no live counterpart in pricing.py — this file is its only
implementation (ported from C:/Antigravity/TradingBot/regime_monitor.py's
_calculate_adx(), same standard Wilder formula). It stays backtest-only
because the backtest below found no accuracy benefit from an ADX filter (see
CURRENT_STATUS.md) — nothing in production needs it yet.

Usage:
    python -m backend.tools.backtest_trend                      # sample NIFTY universe
    python -m backend.tools.backtest_trend RELIANCE TCS HDFCBANK # specific symbols
"""
from __future__ import annotations

import sys
from dataclasses import dataclass

import pandas as pd

from .. import pricing

# A representative slice of liquid, well-covered NSE large/mid caps — not the
# user's actual portfolio (this script runs standalone, no DB dependency), but
# enough to see whether the rule table has any edge at all across sectors.
DEFAULT_UNIVERSE = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "HINDUNILVR",
    "SBIN", "BHARTIARTL", "ITC", "KOTAKBANK", "LT", "AXISBANK",
    "MARUTI", "TITAN", "SUNPHARMA", "TATAMOTORS",
]

WINDOWS = (1, 7, 30)  # trading days


def rsi_series(closes: pd.Series, period: int = 14) -> pd.Series:
    delta = closes.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.where(loss != 0, 100.0)  # matches compute_rsi: zero losses -> 100


def macd_hist_series(closes: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.Series:
    ema_fast = closes.ewm(span=fast, adjust=False).mean()
    ema_slow = closes.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line - signal_line


def adx_series(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = df["High"], df["Low"], df["Close"]
    tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    dm_plus = high.diff()
    dm_minus = -low.diff()
    dm_plus[dm_plus < 0] = 0
    dm_minus[dm_minus < 0] = 0
    tr_smooth = tr.rolling(period).mean()
    di_plus = 100 * dm_plus.rolling(period).mean() / tr_smooth
    di_minus = 100 * dm_minus.rolling(period).mean() / tr_smooth
    dx = 100 * (di_plus - di_minus).abs() / (di_plus + di_minus)
    return dx.rolling(period).mean()


@dataclass
class BacktestRow:
    symbol: str
    label: str
    direction: str
    adx: float | None


def _grade_future(closes: pd.Series, i: int, n: int, price_t: float, direction: str) -> dict:
    """Shared by every backtest variant below: hit_Nd for each window, or None
    if the window runs past the end of the available data."""
    out = {}
    for w in WINDOWS:
        if i + w >= n:
            out[f"hit_{w}d"] = None
            continue
        price_future = closes.iloc[i + w]
        hit = price_future > price_t if direction == "up" else price_future < price_t
        out[f"hit_{w}d"] = bool(hit)  # native bool, not numpy.bool_ — object-dtype columns of
        # numpy bools silently produce wrong .mean() results under groupby (verified: gives
        # ~0.01 instead of ~0.45 on real data). Native Python bool avoids the landmine.
    return out


def backtest_symbol(df: pd.DataFrame, symbol: str, adx_gate: float | None = None,
                     require_sma200_alignment: bool = False) -> list[dict]:
    """One row per trading day with enough lookback: the label classify_trend()
    would have given that day, plus whether price direction matched it at each
    window.
    adx_gate: if set, only rows with ADX >= this are graded (tested — no help).
    require_sma200_alignment: if True, only grade a Bullish call when price is
    already above its 200-day average (Bearish: below) — the idea being RSI/MACD
    shouldn't be trusted against the stock's own primary trend."""
    closes = df["Close"]
    rsi = rsi_series(closes)
    macd = macd_hist_series(closes)
    adx = adx_series(df)
    sma200 = closes.rolling(200).mean()

    rows = []
    n = len(df)
    for i in range(35, n):  # 35 = enough bars for RSI+MACD+ADX to be defined
        trend = pricing.classify_trend(
            rsi.iloc[i] if pd.notna(rsi.iloc[i]) else None,
            macd.iloc[i] if pd.notna(macd.iloc[i]) else None,
        )
        if trend["direction"] == "flat":
            continue
        if adx_gate is not None and (pd.isna(adx.iloc[i]) or adx.iloc[i] < adx_gate):
            continue

        price_t = closes.iloc[i]
        if require_sma200_alignment:
            if pd.isna(sma200.iloc[i]):
                continue
            aligned = (trend["direction"] == "up" and price_t > sma200.iloc[i]) or \
                      (trend["direction"] == "down" and price_t < sma200.iloc[i])
            if not aligned:
                continue

        row = {"symbol": symbol, "label": trend["label"], "direction": trend["direction"], "adx": adx.iloc[i]}
        row.update(_grade_future(closes, i, n, price_t, trend["direction"]))
        rows.append(row)
    return rows


def fetch_index_history(symbol: str = "^NSEI", period: str = "2y") -> pd.DataFrame:
    """Nifty 50 index history — not a tradable stock, so pricing.py's
    NSE/.NS-suffix logic doesn't apply; fetched directly via yfinance."""
    import yfinance as yf
    df = yf.Ticker(symbol).history(period=period, interval="1d")
    if df.empty:
        raise ValueError(f"No index history found for {symbol}")
    return df


def backtest_momentum(df: pd.DataFrame, nifty_closes: pd.Series, symbol: str,
                       lookback: int = 126, deadband_pct: float = 1.0) -> list[dict]:
    """Independent signal, not a filter on classify_trend: has this stock
    outperformed Nifty over the trailing `lookback` trading days (~6 months at
    126)? Label Outperform/Underperform, then check the same direction-only
    question as backtest_symbol — does relative momentum predict the stock's
    own future price direction? deadband_pct: skip days where the relative
    momentum is smaller than this, to avoid grading noise near zero as a call.
    """
    closes = df["Close"]
    # Align stock and index on date so momentum is compared same-day-to-same-day —
    # timezone-naive because yfinance sometimes returns tz-aware indexes for one
    # and not the other depending on symbol/exchange.
    idx = closes.index.tz_localize(None) if closes.index.tz is not None else closes.index
    nidx = nifty_closes.index.tz_localize(None) if nifty_closes.index.tz is not None else nifty_closes.index
    closes = pd.Series(closes.values, index=idx)
    nifty = pd.Series(nifty_closes.values, index=nidx).reindex(idx, method="ffill")

    stock_mom = closes / closes.shift(lookback) - 1
    nifty_mom = nifty / nifty.shift(lookback) - 1
    relative_mom = (stock_mom - nifty_mom) * 100  # percentage points

    rows = []
    n = len(closes)
    for i in range(lookback + 1, n):
        rel = relative_mom.iloc[i]
        if pd.isna(rel) or abs(rel) < deadband_pct:
            continue
        direction = "up" if rel > 0 else "down"
        label = "Outperform" if rel > 0 else "Underperform"
        price_t = closes.iloc[i]
        row = {"symbol": symbol, "label": label, "direction": direction, "relative_momentum_pp": round(float(rel), 1)}
        row.update(_grade_future(closes, i, n, price_t, direction))
        rows.append(row)
    return rows


def summarize(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    out = []
    for label, group in df.groupby("label"):
        entry = {"label": label, "n": len(group)}
        for w in WINDOWS:
            col = f"hit_{w}d"
            graded = group[col].dropna()
            # .astype(bool) belt-and-suspenders: forces a clean numeric mean
            # regardless of whether the column ended up object-dtype.
            entry[f"hit_rate_{w}d"] = round(100 * graded.astype(bool).mean(), 1) if len(graded) else None
            entry[f"n_{w}d"] = len(graded)
        out.append(entry)
    return pd.DataFrame(out).sort_values("label")


def run(symbols: list[str], adx_gate: float | None = None,
        require_sma200_alignment: bool = False) -> pd.DataFrame:
    all_rows = []
    for symbol in symbols:
        try:
            df = pricing.fetch_daily_history(symbol, "NSE", period="2y")
        except ValueError as e:
            print(f"  skipping {symbol}: {e}", file=sys.stderr)
            continue
        all_rows.extend(backtest_symbol(df, symbol, adx_gate=adx_gate,
                                         require_sma200_alignment=require_sma200_alignment))
    return summarize(all_rows)


def run_momentum(symbols: list[str], lookback: int = 126) -> pd.DataFrame:
    nifty_df = fetch_index_history()
    nifty_closes = nifty_df["Close"]
    all_rows = []
    for symbol in symbols:
        try:
            df = pricing.fetch_daily_history(symbol, "NSE", period="2y")
        except ValueError as e:
            print(f"  skipping {symbol}: {e}", file=sys.stderr)
            continue
        all_rows.extend(backtest_momentum(df, nifty_closes, symbol, lookback=lookback))
    return summarize(all_rows)


if __name__ == "__main__":
    symbols = sys.argv[1:] or DEFAULT_UNIVERSE
    pd.set_option("display.width", 120)

    print(f"Backtesting classify_trend() over 2y history, {len(symbols)} symbols...\n")

    print("=== UNGATED (current live rule table) ===")
    print(run(symbols).to_string(index=False))

    print("\n=== ADX >= 20 GATE (only grade calls made during an actual trend) ===")
    print(run(symbols, adx_gate=20).to_string(index=False))

    print("\n=== 200-DMA ALIGNMENT FILTER (only trust Bullish above / Bearish below 200 DMA) ===")
    print(run(symbols, require_sma200_alignment=True).to_string(index=False))

    print("\n=== RELATIVE MOMENTUM vs NIFTY 50 (independent signal, 6-month lookback) ===")
    print(run_momentum(symbols).to_string(index=False))
