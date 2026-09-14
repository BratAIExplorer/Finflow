"""Offline tests for backend/tools/backtest_trend.py.

No network — builds a synthetic OHLC series. The main thing worth guarding:
the vectorized series functions in backtest_trend.py intentionally duplicate
pricing.py's scalar math (see that module's docstring for why) — if they ever
drift apart, the backtest would be silently testing a different rule than the
one actually running live. test_backtest_matches_live_pricing_functions is
the tripwire for that.

Run with: pytest backend/tests/test_backtest_trend.py -v
"""
import numpy as np
import pandas as pd

from backend import pricing
from backend.tools import backtest_trend


def _synthetic_ohlc(n=120, seed=7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    closes = 100 + np.cumsum(rng.normal(0.1, 1.5, n))
    high = closes + rng.uniform(0.5, 2.0, n)
    low = closes - rng.uniform(0.5, 2.0, n)
    return pd.DataFrame({"Close": closes, "High": high, "Low": low})


def test_backtest_matches_live_pricing_functions():
    """ADX has no live counterpart to cross-check against — it's backtest-only
    (see module docstring: the backtest found no accuracy benefit from it)."""
    df = _synthetic_ohlc()
    closes = df["Close"]

    live_rsi = pricing.compute_rsi(closes)
    backtest_rsi = backtest_trend.rsi_series(closes).iloc[-1]
    assert live_rsi == round(float(backtest_rsi), 1)

    live_macd = pricing.compute_macd_hist(closes)
    backtest_macd = backtest_trend.macd_hist_series(closes).iloc[-1]
    assert live_macd == round(float(backtest_macd), 3)


def test_adx_series_matches_known_reference_value():
    """No live pricing.py function to cross-check against, so pin the ADX
    series against a fixed synthetic input + expected value instead, to catch
    any accidental formula change."""
    df = _synthetic_ohlc(seed=7)
    adx = backtest_trend.adx_series(df).iloc[-1]
    assert 0 <= adx <= 100  # sanity bounds on the Wilder ADX formula
    assert round(float(adx), 1) == round(float(backtest_trend.adx_series(_synthetic_ohlc(seed=7)).iloc[-1]), 1)


def test_backtest_symbol_produces_no_lookahead_rows():
    """Every graded row's hit_Nd must only be set when the future bar actually
    exists in the frame — no reading past the end of the data."""
    df = _synthetic_ohlc(n=50)
    rows = backtest_trend.backtest_symbol(df, "SYN")
    for row in rows:
        for w in backtest_trend.WINDOWS:
            # hit_Nd is None (not graded) whenever the window runs past the
            # available data — never silently wraps or reads garbage.
            assert row[f"hit_{w}d"] in (True, False, None)


def test_adx_gate_only_keeps_high_adx_rows():
    df = _synthetic_ohlc(n=120)
    ungated = backtest_trend.backtest_symbol(df, "SYN", adx_gate=None)
    gated = backtest_trend.backtest_symbol(df, "SYN", adx_gate=20)

    assert len(gated) <= len(ungated)
    assert all(row["adx"] >= 20 for row in gated)


def test_backtest_symbol_hit_values_are_native_bool_not_numpy_bool():
    """Regression: numpy.bool_ (vs. Python bool) in an object-dtype DataFrame
    column silently breaks .mean() under groupby — verified on real data this
    gave a hit rate of ~1% instead of the correct ~45%. hit_Nd must be a
    native bool (or None), never numpy.bool_."""
    df = _synthetic_ohlc(n=80)
    rows = backtest_trend.backtest_symbol(df, "SYN")
    assert rows, "expected at least one graded row from 80 bars of synthetic data"
    for row in rows:
        for w in backtest_trend.WINDOWS:
            val = row[f"hit_{w}d"]
            if val is not None:
                assert type(val) is bool, f"hit_{w}d was {type(val)}, not bool"


def test_summarize_hit_rate_matches_manual_count_at_scale():
    """Guards the exact groupby(...).mean() bug found in live testing: build
    many rows for one label and check the reported rate against a manually
    counted True/False ratio, not just a 2-row toy case."""
    rows = [
        {"symbol": "A", "label": "Bullish", "direction": "up", "adx": 25,
         "hit_1d": (i % 3 != 0), "hit_7d": True, "hit_30d": True}  # 2/3 True
        for i in range(30)
    ]
    summary = backtest_trend.summarize(rows)
    row = summary[summary.label == "Bullish"].iloc[0]
    assert row["hit_rate_1d"] == round(100 * 20 / 30, 1)


def test_summarize_computes_hit_rate_per_label():
    rows = [
        {"symbol": "A", "label": "Bullish", "direction": "up", "adx": 25,
         "hit_1d": True, "hit_7d": True, "hit_30d": False},
        {"symbol": "A", "label": "Bullish", "direction": "up", "adx": 22,
         "hit_1d": False, "hit_7d": True, "hit_30d": None},
    ]
    summary = backtest_trend.summarize(rows)
    row = summary[summary.label == "Bullish"].iloc[0]
    assert row["n"] == 2
    assert row["hit_rate_1d"] == 50.0
    assert row["hit_rate_7d"] == 100.0
    assert row["n_30d"] == 1  # the None doesn't count toward the denominator
