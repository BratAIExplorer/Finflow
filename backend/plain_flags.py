"""
Plain-language, rule-based flags for the dashboard's "What to know" chip —
distinct from pricing.classify_trend()'s technical Bullish/Bearish label.
These are fixed if/else rules on numbers already on screen (price position,
holding period). None of this is investment advice; it exists so a
non-technical reader doesn't have to do the arithmetic themselves.
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional

LONG_TERM_DAYS = 365  # India: LTCG tax rate applies to equities held > 1 year


@dataclass
class PlainFlag:
    code: str        # stable key for the frontend to pick an icon/color by
    text: str


def holding_period_flag(first_buy_date: Optional[date]) -> Optional[PlainFlag]:
    if first_buy_date is None:
        return None
    held_days = (date.today() - first_buy_date).days
    if held_days >= LONG_TERM_DAYS:
        return PlainFlag("long_term", "✓ Long-term (>1yr, lower tax)")
    return PlainFlag("short_term", "Holding under 1 yr — selling now is taxed higher")


def price_position_flag(last_price: float, avg_buy_price: float, week52_high: float, week52_low: float) -> Optional[PlainFlag]:
    if avg_buy_price <= 0:
        return None
    change_pct = (last_price - avg_buy_price) / avg_buy_price * 100
    near_high = week52_high > 0 and last_price >= week52_high * 0.97

    if near_high:
        return PlainFlag("near_high", "⚠ Near 52-wk high — worth a look")
    if change_pct <= -15:
        return PlainFlag("below_cost", "▼ Well below buy price")
    return None


def build_flags(last_price: float, avg_buy_price: float, week52_high: float,
                 week52_low: float, first_buy_date: Optional[date]) -> list[PlainFlag]:
    flags = []
    hp = holding_period_flag(first_buy_date)
    if hp:
        flags.append(hp)
    pp = price_position_flag(last_price, avg_buy_price, week52_high, week52_low)
    if pp:
        flags.append(pp)
    return flags
