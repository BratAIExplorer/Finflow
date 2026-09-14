"""Write the board to the Desktop every refresh (local Windows environment).

  board_latest.csv / .xlsx   - current snapshot, overwritten (Dad opens this)
  history.csv / .xlsx        - one row per stock per refresh, appended forever
  news_history.csv           - news items, appended, deduped by id

Gracefully disabled when running on headless VPS/Docker or when no desktop exists.
"""
import csv
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pandas as pd

IST = timezone(timedelta(hours=5, minutes=30))


def _desktop():
    """The real Windows Desktop, even when OneDrive has redirected it. Returns None if not available."""
    if os.getenv("ENABLE_DESKTOP_EXPORT", "true").lower() in ("false", "0", "no"):
        return None
    try:
        import winreg
        key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as k:
            p = Path(winreg.QueryValueEx(k, "Desktop")[0])
        if p.exists():
            return p
    except Exception:
        pass
    one = Path.home() / "OneDrive" / "Desktop"
    if one.exists():
        return one
    d = Path.home() / "Desktop"
    return d if d.exists() else None


SNAP_COLS = ["symbol", "name", "trend_word", "price_num", "chg_num", "rsi_num",
             "macd_hist", "held", "qty", "buy_price", "pnl_rupees", "pnl_pct", "account"]
HIST_COLS = ["timestamp_ist"] + SNAP_COLS + ["trend_score"]
NEWS_COLS = ["timestamp_ist", "symbol", "name", "head", "src", "time", "cls", "important", "id"]


def _row(stock, now):
    return {
        "timestamp_ist": now,
        "symbol": stock["symbol"], "name": stock["name"],
        "trend_word": stock.get("trend_word", ""),
        "price_num": stock.get("price_num", ""),
        "chg_num": stock.get("chg_num", ""),
        "rsi_num": stock.get("rsi_num", ""),
        "macd_hist": stock.get("macd_hist", ""),
        "held": stock.get("held", False),
        "qty": stock.get("qty", ""),
        "buy_price": stock.get("avg", ""),
        "pnl_rupees": stock.get("pnl", ""),
        "pnl_pct": stock.get("pnlpct", ""),
        "account": stock.get("acct", ""),
        "trend_score": stock.get("trend_score", ""),
    }


def write(stocks, news):
    desk = _desktop()
    if not desk:
        return ""
    out_dir = desk / "MarketBoard"
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        now = datetime.now(IST).strftime("%Y-%m-%d %H:%M")

        rows = [_row(s, now) for s in stocks]

        # 1. latest snapshot (overwrite)
        if rows:
            snap = pd.DataFrame(rows)[["timestamp_ist"] + SNAP_COLS + ["trend_score"]]
            snap.to_csv(out_dir / "board_latest.csv", index=False)
            try:
                snap.to_excel(out_dir / "board_latest.xlsx", index=False)
            except Exception:
                pass

        # 2. history (append)
        if rows:
            hist = out_dir / "history.csv"
            new_file = not hist.exists()
            with hist.open("a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=HIST_COLS)
                if new_file:
                    w.writeheader()
                w.writerows(rows)
            try:
                pd.read_csv(hist).to_excel(out_dir / "history.xlsx", index=False)
            except Exception:
                pass

        # 3. news history (append; news items are already deduped upstream)
        if news:
            nf = out_dir / "news_history.csv"
            new_file = not nf.exists()
            with nf.open("a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=NEWS_COLS)
                if new_file:
                    w.writeheader()
                for n in news:
                    w.writerow({"timestamp_ist": now, **{k: n.get(k, "") for k in NEWS_COLS[1:]}})

        return str(out_dir)
    except Exception as e:
        print(f"[export.py] skipped desktop export: {e}")
        return ""
