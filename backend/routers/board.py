"""FastAPI Router for Deepak's Market Board.

Serves the migrated dashboard endpoints:
- GET /board/: returns current cached snapshot immediately
- POST /board/refresh: forces refresh of technical signals and news
- POST /board/add: adds a symbol to the watchlist and refreshes
- POST /board/remove: removes a symbol from the watchlist and refreshes
"""
import threading
import time
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..board import data, export, news, watchlist
from ..models import User
from .auth import get_current_user

router = APIRouter(prefix="/board", tags=["board"])

IST = timezone(timedelta(hours=5, minutes=30))

SNAP = {
    "ts": "not yet",
    "stocks": [],
    "news": [],
    "prices_ok": False,
    "news_ok": False,
    "out_dir": "",
}
_lock = threading.Lock()
_last_news = 0.0


def market_open(now=None):
    now = now or datetime.now(IST)
    if now.weekday() >= 5:
        return False
    mins = now.hour * 60 + now.minute
    return 9 * 60 + 15 <= mins <= 15 * 60 + 30


def refresh_board(force_news: bool = False) -> dict:
    global _last_news
    stocks = watchlist.load()
    rows, prices_ok = data.fetch(stocks)

    do_news = force_news or (time.time() - _last_news > 3300)  # ~55 min
    if do_news:
        items, news_ok = news.fetch(stocks)
        _last_news = time.time()
    else:
        with _lock:
            items, news_ok = [], SNAP["news_ok"]

    out_dir = export.write(rows, items)

    with _lock:
        SNAP["ts"] = datetime.now(IST).strftime("%d %b %Y  %I:%M %p")
        SNAP["stocks"] = rows
        SNAP["prices_ok"] = prices_ok
        SNAP["out_dir"] = out_dir
        if do_news:
            SNAP["news"] = (items + SNAP["news"])[:40]
            SNAP["news_ok"] = news_ok
        return dict(SNAP)


def get_snap() -> dict:
    with _lock:
        if SNAP["ts"] != "not yet":
            return dict(SNAP)
    return refresh_board(force_news=True)


class AddStockRequest(BaseModel):
    symbol: str
    name: str = ""


class RemoveStockRequest(BaseModel):
    symbol: str


@router.get("/")
def get_board(current_user: User = Depends(get_current_user)):
    return get_snap()


@router.post("/refresh")
def refresh(current_user: User = Depends(get_current_user)):
    return refresh_board(force_news=True)


@router.post("/add")
def add_stock(req: AddStockRequest, current_user: User = Depends(get_current_user)):
    watchlist.add(req.symbol, req.name)
    return refresh_board(force_news=False)


@router.post("/remove")
def remove_stock(req: RemoveStockRequest, current_user: User = Depends(get_current_user)):
    watchlist.remove(req.symbol)
    return refresh_board(force_news=False)
