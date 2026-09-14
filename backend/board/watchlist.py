"""Read / write the watchlist file (my_stocks.txt). One line: SYMBOL | Company name.
Thread-safe for concurrent access in web environment.
"""
import threading
from pathlib import Path

FILE = Path(__file__).with_name("my_stocks.txt")
_lock = threading.Lock()


def load():
    with _lock:
        rows = []
        if not FILE.exists():
            return rows
        for line in FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "|" in line:
                sym, name = line.split("|", 1)
            else:
                sym, name = line, line
            rows.append({"symbol": sym.strip().upper(), "name": name.strip()})
        return rows


def _write_locked(rows):
    header = ("# Dad's watchlist. One per line:  NSE_SYMBOL | Full company name "
              "(used for news search)\n"
              '# Edit here or from the "My Stocks" box in the dashboard.\n\n')
    body = "\n".join(f"{r['symbol']:<10} | {r['name']}" for r in rows)
    FILE.write_text(header + body + "\n", encoding="utf-8")


def add(symbol: str, name: str = ""):
    symbol = symbol.strip().upper()
    if not symbol:
        return
    with _lock:
        rows = []
        if FILE.exists():
            for line in FILE.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "|" in line:
                    sym, nm = line.split("|", 1)
                else:
                    sym, nm = line, line
                rows.append({"symbol": sym.strip().upper(), "name": nm.strip()})
        if any(r["symbol"] == symbol for r in rows):
            return
        rows.append({"symbol": symbol, "name": (name or symbol).strip()})
        _write_locked(rows)


def remove(symbol: str):
    symbol = symbol.strip().upper()
    with _lock:
        rows = []
        if FILE.exists():
            for line in FILE.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "|" in line:
                    sym, nm = line.split("|", 1)
                else:
                    sym, nm = line, line
                rows.append({"symbol": sym.strip().upper(), "name": nm.strip()})
        rows = [r for r in rows if r["symbol"] != symbol]
        _write_locked(rows)
