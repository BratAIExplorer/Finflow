#!/usr/bin/env python3
"""mStock Trade-Matching Sync Engine.

Reconciles mStock portfolio holdings with historical trade records using
FIFO (First-In, First-Out) lot matching to automatically determine exact
acquisition/purchase timestamps.

Supports:
1. Live mStock Trading API integration (/portfolio/holdings and /trades).
2. Offline / Mock simulation mode (--mock) for safe testing without credentials.
3. Direct CSV export for Maybe Finance (auto-populating "held — set date").
4. Structured JSON export for Finflow / automated wealth trackers.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import io
import json
import os
import sys
from typing import List, Dict, Optional, Tuple
import urllib.parse
import urllib.request
import urllib.error


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class Holding:
    """Represents an open position in mStock."""
    symbol: str
    name: str
    quantity: float
    average_price: float
    last_price: float = 0.0
    isin: str = ""


@dataclass
class Trade:
    """Represents an executed trade from mStock trade history."""
    symbol: str
    transaction_type: str  # "BUY" or "SELL"
    quantity: float
    price: float
    timestamp: str  # YYYY-MM-DD HH:MM:SS
    order_id: str = ""


@dataclass
class MatchedLot:
    """Represents an active holding lot with verified purchase date and cost."""
    symbol: str
    name: str
    quantity: float
    purchase_price: float
    purchase_date: str  # YYYY-MM-DD HH:MM:SS or YYYY-MM-DD
    is_estimated: bool = False
    note: str = ""


# ---------------------------------------------------------------------------
# FIFO Reconciliation Engine
# ---------------------------------------------------------------------------

class FIFOLotMatcher:
    """Matches aggregate holdings to historical trade executions using FIFO."""

    @staticmethod
    def _normalize_symbol(symbol: str) -> str:
        return (symbol or "").strip().upper()

    @classmethod
    def match(
        cls,
        holdings: List[Holding],
        trades: List[Trade],
        default_date: Optional[str] = None,
    ) -> List[MatchedLot]:
        """Reconcile holdings against trades and return individual dated lots.

        Args:
            holdings: Current open positions from broker.
            trades: Historical BUY and SELL executions.
            default_date: Fallback date string if trades predate the query window.
        """
        # Group trades by normalized symbol
        trades_by_symbol: Dict[str, List[Trade]] = {}
        for trade in trades:
            sym = cls._normalize_symbol(trade.symbol)
            trades_by_symbol.setdefault(sym, []).append(trade)

        # Sort each symbol's trades chronologically
        for sym in trades_by_symbol:
            trades_by_symbol[sym].sort(key=lambda t: t.timestamp)

        matched_lots: List[MatchedLot] = []

        for holding in holdings:
            sym = cls._normalize_symbol(holding.symbol)
            holding_qty = holding.quantity
            sym_trades = trades_by_symbol.get(sym, [])

            if holding_qty <= 0:
                continue

            # Track open buy lots: list of dicts {"qty", "price", "timestamp", "order_id"}
            buy_lots: List[Dict] = []

            for trade in sym_trades:
                action = trade.transaction_type.strip().upper()
                if action in ("BUY", "B"):
                    buy_lots.append({
                        "qty": trade.quantity,
                        "price": trade.price,
                        "timestamp": trade.timestamp,
                        "order_id": trade.order_id,
                    })
                elif action in ("SELL", "S"):
                    # FIFO: deplete oldest buy lots first
                    qty_to_sell = trade.quantity
                    for lot in buy_lots:
                        if lot["qty"] <= 0:
                            continue
                        if lot["qty"] >= qty_to_sell:
                            lot["qty"] -= qty_to_sell
                            qty_to_sell = 0
                            break
                        else:
                            qty_to_sell -= lot["qty"]
                            lot["qty"] = 0

            # Filter lots that still have remaining shares
            active_lots = [lot for lot in buy_lots if lot["qty"] > 0]
            total_active_qty = sum(lot["qty"] for lot in active_lots)

            if total_active_qty >= holding_qty:
                # We have sufficient buy trades. Take the most recent open lots
                # that add up to the current holding_qty.
                qty_needed = holding_qty
                selected_lots = []
                for lot in reversed(active_lots):
                    if qty_needed <= 0:
                        break
                    take_qty = min(lot["qty"], qty_needed)
                    selected_lots.append(
                        MatchedLot(
                            symbol=holding.symbol,
                            name=holding.name,
                            quantity=take_qty,
                            purchase_price=lot["price"],
                            purchase_date=lot["timestamp"],
                            is_estimated=False,
                            note=f"Verified trade ID: {lot['order_id']}" if lot["order_id"] else "Verified mStock execution",
                        )
                    )
                    qty_needed -= take_qty

                # Restore chronological order
                matched_lots.extend(reversed(selected_lots))

            else:
                # Trade history only covers a subset of current holding
                # (e.g., initial purchase occurred before the API's query window).
                for lot in active_lots:
                    matched_lots.append(
                        MatchedLot(
                            symbol=holding.symbol,
                            name=holding.name,
                            quantity=lot["qty"],
                            purchase_price=lot["price"],
                            purchase_date=lot["timestamp"],
                            is_estimated=False,
                            note=f"Verified trade ID: {lot['order_id']}" if lot["order_id"] else "Verified mStock execution",
                        )
                    )

                missing_qty = holding_qty - total_active_qty
                fallback_date = default_date or datetime.now().strftime("%Y-01-01 09:15:00")
                matched_lots.append(
                    MatchedLot(
                        symbol=holding.symbol,
                        name=holding.name,
                        quantity=round(missing_qty, 4),
                        purchase_price=holding.average_price,
                        purchase_date=fallback_date,
                        is_estimated=True,
                        note="Acquired before API query window; estimated using broker average price.",
                    )
                )

        return matched_lots


# ---------------------------------------------------------------------------
# mStock API Client
# ---------------------------------------------------------------------------

class MStockClient:
    """Client for querying mStock Trading REST API."""

    BASE_URL = "https://api.mstock.trade/openapi/typea"

    def __init__(self, api_key: str, access_token: str, timeout: int = 15):
        self.api_key = api_key
        self.access_token = access_token
        self.timeout = timeout
        self.headers = {
            "X-Mirae-Version": "1",
            "Authorization": f"token {api_key}:{access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def fetch_holdings(self) -> List[Holding]:
        """Fetch all current delivery equity holdings."""
        url = f"{self.BASE_URL}/portfolio/holdings"
        req = urllib.request.Request(url, headers=self.headers, method="GET")

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8") if e.fp else str(e)
            raise RuntimeError(f"mStock Holdings API error (HTTP {e.code}): {err_msg}")

        holdings = []
        for item in data.get("data") or []:
            sym = item.get("tradingsymbol") or item.get("symbol") or ""
            holdings.append(
                Holding(
                    symbol=sym,
                    name=item.get("name") or sym,
                    quantity=float(item.get("quantity", 0) or 0),
                    average_price=float(item.get("average_price", 0) or item.get("price", 0) or 0),
                    last_price=float(item.get("last_price", 0) or 0),
                    isin=item.get("isin", ""),
                )
            )
        return holdings

    def fetch_trades(self, from_date: str, to_date: str) -> List[Trade]:
        """Fetch executed trades within the given date window (YYYY-MM-DD)."""
        url = f"{self.BASE_URL}/trades"
        payload = urllib.parse.urlencode({"fromdate": from_date, "todate": to_date}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=self.headers, method="GET")

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8") if e.fp else str(e)
            raise RuntimeError(f"mStock Trades API error (HTTP {e.code}): {err_msg}")

        trades = []
        for item in data.get("data") or []:
            sym = item.get("tradingsymbol") or item.get("symbol") or item.get("SYMBOL") or ""
            ts = (
                item.get("order_timestamp")
                or item.get("exchange_timestamp")
                or item.get("ORDER_DATE_TIME")
                or ""
            )
            norm_ts = cls_parse_timestamp(ts)

            trades.append(
                Trade(
                    symbol=sym,
                    transaction_type=item.get("transaction_type") or item.get("BUY_SELL") or "BUY",
                    quantity=float(item.get("quantity") or item.get("QUANTITY") or 0),
                    price=float(item.get("average_price") or item.get("price") or item.get("PRICE") or 0),
                    timestamp=norm_ts,
                    order_id=str(item.get("order_id") or item.get("ORDER_NUMBER") or ""),
                )
            )
        return trades


def cls_parse_timestamp(raw_ts: str) -> str:
    """Normalize various date formats returned by broker APIs."""
    if not raw_ts:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    raw_ts = raw_ts.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%d-%m-%Y %H:%M:%S", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            dt = datetime.strptime(raw_ts, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    return raw_ts


# ---------------------------------------------------------------------------
# Mock Data Generator (Matches user's real scenario: APOLLO 101 shares)
# ---------------------------------------------------------------------------

def get_mock_data() -> Tuple[List[Holding], List[Trade]]:
    """Returns sample holdings matching user's real-world scenario (APOLLO 101 shares)."""
    holdings = [
        Holding(
            symbol="APOLLO",
            name="Apollo Micro Systems Limited",
            quantity=101.0,
            average_price=120.50,
            last_price=135.20,
            isin="INE713T01028",
        ),
        Holding(
            symbol="BANK OF MAHARASHTRA",
            name="Bank of Maharashtra",
            quantity=10.0,
            average_price=30.00,
            last_price=84.70,
            isin="INE457A01014",
        ),
        Holding(
            symbol="IDEA",
            name="Vodafone Idea Limited",
            quantity=4.0,
            average_price=6.98,
            last_price=7.20,
            isin="INE488V01015",
        ),
    ]

    # Trades simulated across multiple dates to test FIFO aggregation:
    trades = [
        # Apollo bought in two tranches (50 on March 15, 51 on August 20)
        Trade(
            symbol="APOLLO",
            transaction_type="BUY",
            quantity=50.0,
            price=112.50,
            timestamp="2024-03-15 10:14:22",
            order_id="11000000301045",
        ),
        Trade(
            symbol="APOLLO",
            transaction_type="BUY",
            quantity=51.0,
            price=128.34,
            timestamp="2024-08-20 14:25:10",
            order_id="11000000452091",
        ),
        # Bank of Maharashtra single purchase
        Trade(
            symbol="BANK OF MAHARASHTRA",
            transaction_type="BUY",
            quantity=10.0,
            price=30.00,
            timestamp="2024-01-10 11:05:30",
            order_id="11000000210080",
        ),
        # Vodafone Idea: bought 5 shares, sold 1 share -> 4 remaining
        Trade(
            symbol="IDEA",
            transaction_type="BUY",
            quantity=5.0,
            price=6.95,
            timestamp="2024-06-10 12:43:56",
            order_id="21612506101398",
        ),
        Trade(
            symbol="IDEA",
            transaction_type="SELL",
            quantity=1.0,
            price=7.10,
            timestamp="2024-07-02 13:08:42",
            order_id="21612506101476",
        ),
    ]
    return holdings, trades


# ---------------------------------------------------------------------------
# Exporters
# ---------------------------------------------------------------------------

def export_maybe_csv(
    lots: List[MatchedLot],
    account_name: str = "Kiran",
    currency: str = "INR",
) -> str:
    """Export reconciled lots in standard Maybe Finance CSV format.

    Columns: Date, Account, Symbol, Name, Type, Quantity, Price, Currency, Notes
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Account", "Symbol", "Name", "Type", "Quantity", "Price", "Currency", "Notes"])

    for lot in lots:
        writer.writerow([
            lot.purchase_date,
            account_name,
            lot.symbol,
            lot.name,
            "Buy",
            lot.quantity,
            round(lot.purchase_price, 2),
            currency,
            lot.note,
        ])
    return output.getvalue()


def export_json(lots: List[MatchedLot]) -> str:
    """Export reconciled lots in structured JSON format for Finflow."""
    return json.dumps([asdict(lot) for lot in lots], indent=2)


# ---------------------------------------------------------------------------
# CLI Command Runner
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="mStock Trade-Matching Sync Script: Reconciles holdings with trades to auto-populate acquisition dates."
    )
    parser.add_argument("--api-key", help="mStock API Key (or env MSTOCK_API_KEY)")
    parser.add_argument("--access-token", help="mStock Access Token (or env MSTOCK_ACCESS_TOKEN)")
    parser.add_argument("--from-date", help="Trade history start date (YYYY-MM-DD). Default: 1 year ago.")
    parser.add_argument("--to-date", help="Trade history end date (YYYY-MM-DD). Default: today.")
    parser.add_argument("--account", default="Kiran", help="Account name for Maybe Finance (default: Kiran)")
    parser.add_argument("--currency", default="INR", help="Currency code (default: INR)")
    parser.add_argument(
        "--format",
        choices=["maybe-csv", "json", "summary"],
        default="maybe-csv",
        help="Export format (default: maybe-csv)",
    )
    parser.add_argument("--out", help="Output file path (default: print to stdout)")
    parser.add_argument("--mock", action="store_true", help="Run with mock data (offline test mode)")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    # Dates
    today = datetime.now().date()
    to_date = args.to_date or today.strftime("%Y-%m-%d")
    from_date = args.from_date or (today - timedelta(days=365)).strftime("%Y-%m-%d")

    if args.mock:
        print("[INFO] Running in MOCK mode with sample mStock portfolio...", file=sys.stderr)
        holdings, trades = get_mock_data()
    else:
        api_key = args.api_key or os.environ.get("MSTOCK_API_KEY")
        access_token = args.access_token or os.environ.get("MSTOCK_ACCESS_TOKEN")

        if not api_key or not access_token:
            print(
                "[ERROR] Missing credentials! Provide --api-key and --access-token, "
                "or set MSTOCK_API_KEY / MSTOCK_ACCESS_TOKEN, or use --mock for offline test.",
                file=sys.stderr,
            )
            return 1

        client = MStockClient(api_key, access_token)
        print(f"[INFO] Fetching mStock holdings...", file=sys.stderr)
        holdings = client.fetch_holdings()
        print(f"[INFO] Fetching mStock trades ({from_date} to {to_date})...", file=sys.stderr)
        trades = client.fetch_trades(from_date, to_date)

    print(f"[INFO] Reconciling {len(holdings)} holdings against {len(trades)} executed trades...", file=sys.stderr)
    matcher = FIFOLotMatcher()
    matched_lots = matcher.match(holdings, trades, default_date=from_date)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    # Format output
    if args.format == "maybe-csv":
        content = export_maybe_csv(matched_lots, account_name=args.account, currency=args.currency)
    elif args.format == "json":
        content = export_json(matched_lots)
    else:
        # Summary format
        lines = ["=== RECONCILED HOLDINGS ==="]
        for lot in matched_lots:
            status = "[ESTIMATED]" if lot.is_estimated else "[VERIFIED]"
            lines.append(
                f"{status} | {lot.symbol} ({lot.name}): {lot.quantity} shares @ {args.currency} {lot.purchase_price} | Date: {lot.purchase_date} [{lot.note}]"
            )
        content = "\n".join(lines)

    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[SUCCESS] Exported reconciled data to {args.out}", file=sys.stderr)
    else:
        print(content)

    return 0


if __name__ == "__main__":
    sys.exit(main())
