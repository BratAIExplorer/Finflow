"""
Shared contract every broker connector implements. This is the "no-code plugin"
interface FinFlow's PROJECT.md already describes — mStock and Zerodha are the
first two concrete connectors; a third broker means a new file here, not a
rewrite of the sync logic in routers/holdings.py.

Every connector is READ-ONLY by contract: fetch_holdings() must never call an
order-placement endpoint, even if the broker's API technically allows it.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class RawHolding:
    """What a broker connector hands back for one stock position, before any
    price/RSI/MACD enrichment (that happens later, from a separate free price feed)."""
    symbol: str
    exchange: str
    quantity: float
    avg_buy_price: float
    currency: str = "INR"
    isin: Optional[str] = None
    first_buy_date: Optional[date] = None  # not all brokers return this — see connector docstring


class BrokerConnectionError(Exception):
    """Raised for anything that stops a sync: expired session, bad credentials,
    network failure. Callers should log this to UserPlugin.last_sync_error and
    keep the last-known-good holdings on screen rather than blanking the dashboard."""


class BrokerConnector(ABC):
    """One instance = one broker ACCOUNT (not one broker). Two Zerodha logins
    are two BrokerConnector instances with different credentials, so their
    holdings stay attributable to the right person."""

    broker_name: str = "unknown"

    def __init__(self, credentials: dict):
        self.credentials = credentials

    @abstractmethod
    def ensure_session(self) -> None:
        """Make sure we have a valid, non-expired session token, refreshing it
        if the connector's broker supports that without human input (mStock via
        TOTP). Raise BrokerConnectionError if a human step is required and hasn't
        happened yet (Zerodha's daily browser login)."""
        raise NotImplementedError

    @abstractmethod
    def fetch_holdings(self) -> list[RawHolding]:
        """Return every current stock position. Must call ensure_session() first."""
        raise NotImplementedError
