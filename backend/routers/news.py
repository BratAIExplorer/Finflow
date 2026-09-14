"""Company news per holding, ported from Deepaks-Bots/news.py (Google News RSS).

No local dedup/seen-tracking here — unlike the bot's notification poller, this
is a stateless GET for a UI tab, so every call just returns the current top
headlines per holding.
"""
import hashlib
import urllib.parse
from datetime import datetime, timedelta, timezone

import feedparser
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Holding, User
from .auth import get_current_user

router = APIRouter(prefix="/news", tags=["news"])

IST = timezone(timedelta(hours=5, minutes=30))

MATERIAL = ("order", "wins", "awarded", "contract", "results", "profit", "loss",
            "dividend", "bonus", "split", "pledge", "qip", "fund rais", "acquisition",
            "acquire", "merger", "resign", "downgrade", "upgrade", "block deal",
            "bulk deal", "stake", "buyback", "board meeting")

POS = ("wins", "order", "awarded", "contract", "profit", "up ", "surge", "jump",
       "record", "beat", "upgrade", "buyback", "bonus")
NEG = ("loss", "pledge", "resign", "downgrade", "fall", "drop", "probe", "fraud",
       "penalty", "decline", "cut")


def _sentiment(title: str) -> str:
    t = title.lower()
    if any(w in t for w in NEG):
        return "neg"
    if any(w in t for w in POS):
        return "pos"
    return "neu"


def _pub(entry) -> str:
    try:
        st = entry.published_parsed
        return datetime(*st[:6], tzinfo=timezone.utc).astimezone(IST).strftime("%d %b %H:%M")
    except Exception:
        return datetime.now(IST).strftime("%d %b %H:%M")


def _fetch_one(name: str, symbol: str) -> list[dict]:
    q = urllib.parse.quote(f'"{name}" when:2d')
    url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
    out = []
    try:
        feed = feedparser.parse(url)
    except Exception:
        return out
    for e in feed.entries[:8]:
        title = e.get("title", "").strip()
        if not title:
            continue
        src = ""
        if " - " in title:
            title, src = title.rsplit(" - ", 1)
        uid = hashlib.sha1(f"{symbol}|{title}".encode()).hexdigest()
        low = title.lower()
        out.append({
            "id": uid, "symbol": symbol, "name": name, "headline": title.strip(),
            "source": src.strip() or "Google News",
            "time": _pub(e), "sentiment": _sentiment(title),
            "important": any(w in low for w in MATERIAL),
        })
    return out


@router.get("/")
def list_news(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    holdings = db.query(Holding).filter(Holding.user_id == current_user.id).all()
    seen_symbols: set[str] = set()
    stocks = []
    for h in holdings:
        if h.symbol in seen_symbols:
            continue
        seen_symbols.add(h.symbol)
        stocks.append({"name": h.company_name or h.symbol, "symbol": h.symbol})

    items = []
    for s in stocks:
        items.extend(_fetch_one(s["name"], s["symbol"]))

    items.sort(key=lambda x: x["time"], reverse=True)
    return items[:60]
