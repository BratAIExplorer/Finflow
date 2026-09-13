from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..models import User, UserPlugin, Holding
from ..crypto_utils import encrypt_credentials, decrypt_credentials
from ..brokers.base import BrokerConnectionError
from ..brokers.mstock import MStockConnector
from ..brokers.zerodha import ZerodhaConnector
from .. import pricing
from ..plain_flags import build_flags
from .auth import get_current_user

router = APIRouter(prefix="/holdings", tags=["holdings"])

SUPPORTED_BROKERS = {"mstock", "zerodha"}


def _make_connector(plugin: UserPlugin):
    creds = decrypt_credentials(plugin.credentials_encrypted)
    if plugin.plugin_name == "mstock":
        return MStockConnector(creds)
    if plugin.plugin_name == "zerodha":
        return ZerodhaConnector(creds, session_state=plugin.config or {})
    raise HTTPException(status_code=400, detail=f"Unsupported broker: {plugin.plugin_name}")


# ---------- connecting an account ----------

class PluginCreate(BaseModel):
    plugin_name: str          # "mstock" or "zerodha"
    label: str                # e.g. "Dad's mStock", "Mom's Zerodha" — how it's shown in the UI
    credentials: dict         # see brokers/mstock.py or brokers/zerodha.py for the expected shape


@router.post("/accounts")
def add_broker_account(body: PluginCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if body.plugin_name not in SUPPORTED_BROKERS:
        raise HTTPException(status_code=400, detail=f"Unsupported broker. Use one of: {sorted(SUPPORTED_BROKERS)}")

    plugin = UserPlugin(
        user_id=current_user.id,
        plugin_name=body.plugin_name,
        label=body.label,
        credentials_encrypted=encrypt_credentials(body.credentials),
        config={},
    )
    db.add(plugin)
    db.commit()
    db.refresh(plugin)
    return {"id": plugin.id, "plugin_name": plugin.plugin_name, "label": plugin.label}


@router.get("/accounts")
def list_broker_accounts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plugins = db.query(UserPlugin).filter(UserPlugin.user_id == current_user.id).all()
    return [
        {
            "id": p.id,
            "plugin_name": p.plugin_name,
            "label": p.label,
            "last_synced": p.last_synced,
            "last_sync_error": p.last_sync_error,
        }
        for p in plugins
    ]


class PluginUpdate(BaseModel):
    label: Optional[str] = None          # rename the account
    credentials: Optional[dict] = None   # replace credentials (e.g. Dad changed his password)


@router.patch("/accounts/{plugin_id}")
def update_broker_account(plugin_id: str, body: PluginUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plugin = _get_owned_plugin(db, plugin_id, current_user)
    if body.label is not None:
        plugin.label = body.label
    if body.credentials is not None:
        plugin.credentials_encrypted = encrypt_credentials(body.credentials)
        plugin.config = {}            # force a fresh login on next sync
        plugin.last_sync_error = None
    db.commit()
    db.refresh(plugin)
    return {"id": plugin.id, "plugin_name": plugin.plugin_name, "label": plugin.label}


@router.delete("/accounts/{plugin_id}")
def delete_broker_account(plugin_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plugin = _get_owned_plugin(db, plugin_id, current_user)
    db.query(Holding).filter(Holding.plugin_id == plugin.id).delete()
    db.delete(plugin)
    db.commit()
    return {"deleted": plugin_id}


# ---------- Zerodha's one-click daily refresh ----------

@router.get("/accounts/{plugin_id}/zerodha-login-url")
def zerodha_login_url(plugin_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plugin = _get_owned_plugin(db, plugin_id, current_user, expect_broker="zerodha")
    connector = _make_connector(plugin)
    return {"login_url": connector.login_url()}


@router.get("/accounts/{plugin_id}/zerodha-callback")
def zerodha_callback(plugin_id: str, request_token: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Zerodha redirects the browser here (as this account's registered redirect_url)
    with ?request_token=... after the person logs in. Completes the daily session
    and immediately syncs holdings so the one click does the whole job."""
    plugin = _get_owned_plugin(db, plugin_id, current_user, expect_broker="zerodha")
    connector = _make_connector(plugin)
    try:
        connector.complete_login(request_token)
    except BrokerConnectionError as e:
        raise HTTPException(status_code=400, detail=str(e))

    plugin.config = connector.session_state
    db.commit()
    return _run_sync(plugin, connector, db)


# ---------- syncing holdings ----------

@router.post("/accounts/{plugin_id}/sync")
def sync_account(plugin_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plugin = _get_owned_plugin(db, plugin_id, current_user)
    connector = _make_connector(plugin)
    return _run_sync(plugin, connector, db)


def _run_sync(plugin: UserPlugin, connector, db: Session):
    try:
        raw_holdings = connector.fetch_holdings()
        
        # Try fetching cash balance if the broker supports it
        cash = 0.0
        if hasattr(connector, 'fetch_funds'):
            cash = connector.fetch_funds()
            
        new_cfg = dict(plugin.config or {})
        new_cfg["cash_balance"] = cash
        plugin.config = new_cfg
        
    except BrokerConnectionError as e:
        plugin.last_sync_error = str(e)
        db.commit()
        raise HTTPException(status_code=400, detail=str(e))

    synced, price_failures = 0, []
    for raw in raw_holdings:
        holding = (
            db.query(Holding)
            .filter(Holding.plugin_id == plugin.id, Holding.symbol == raw.symbol, Holding.exchange == raw.exchange)
            .first()
        )
        if holding is None:
            holding = Holding(plugin_id=plugin.id, user_id=plugin.user_id, symbol=raw.symbol, exchange=raw.exchange)
            db.add(holding)

        holding.quantity = raw.quantity
        holding.avg_buy_price = raw.avg_buy_price
        holding.isin = raw.isin
        holding.currency = raw.currency
        if raw.first_buy_date:
            holding.first_buy_date = raw.first_buy_date

        try:
            signals = pricing.compute_signals(raw.symbol, raw.exchange)
            holding.last_price = signals.last_price
            holding.last_price_at = datetime.utcnow()
            holding.week52_high = signals.week52_high
            holding.week52_low = signals.week52_low
            holding.rsi_14 = signals.rsi_14
            holding.macd_hist = signals.macd_hist
        except ValueError as e:
            price_failures.append({"symbol": raw.symbol, "reason": str(e)})

        # Company classification — cheap to skip once we have it, since it
        # rarely changes and Yahoo's .info call is the slow part of a sync.
        if holding.company_name is None or holding.sector is None or holding.cap_tier is None:
            meta = pricing.fetch_company_meta(raw.symbol, raw.exchange)
            holding.company_name = holding.company_name or meta.company_name
            holding.sector = holding.sector or meta.sector
            holding.cap_tier = holding.cap_tier or meta.cap_tier

        synced += 1

    plugin.last_synced = datetime.utcnow()
    plugin.last_sync_error = None
    db.commit()

    return {"synced": synced, "price_failures": price_failures}


def _get_owned_plugin(db: Session, plugin_id: str, current_user: User, expect_broker: Optional[str] = None) -> UserPlugin:
    plugin = db.query(UserPlugin).filter(UserPlugin.id == plugin_id, UserPlugin.user_id == current_user.id).first()
    if not plugin:
        raise HTTPException(status_code=404, detail="Broker account not found")
    if expect_broker and plugin.plugin_name != expect_broker:
        raise HTTPException(status_code=400, detail=f"This endpoint is for {expect_broker} accounts only")
    return plugin


# ---------- reading the dashboard ----------

@router.get("/cash")
def get_cash_balance(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plugins = db.query(UserPlugin).filter(UserPlugin.user_id == current_user.id).all()
    total_cash = 0.0
    for p in plugins:
        if p.config and isinstance(p.config, dict):
            total_cash += float(p.config.get("cash_balance", 0.0))
    return {"cash_balance": total_cash}

@router.get("/")
def list_holdings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    plugins = {p.id: p for p in db.query(UserPlugin).filter(UserPlugin.user_id == current_user.id).all()}
    holdings = db.query(Holding).filter(Holding.user_id == current_user.id).all()

    out = []
    for h in holdings:
        plugin = plugins.get(h.plugin_id)
        trend = pricing.classify_trend(h.rsi_14, h.macd_hist)
        flags = []
        if h.last_price is not None and h.week52_high is not None and h.week52_low is not None:
            flags = build_flags(h.last_price, h.avg_buy_price, h.week52_high, h.week52_low, h.first_buy_date)

        gain_loss = None
        gain_loss_pct = None
        if h.last_price is not None:
            gain_loss = round((h.last_price - h.avg_buy_price) * h.quantity, 2)
            if h.avg_buy_price > 0:
                gain_loss_pct = round((h.last_price - h.avg_buy_price) / h.avg_buy_price * 100, 2)

        days_held = (date.today() - h.first_buy_date).days if h.first_buy_date else None

        out.append({
            "id": h.id,
            "account_label": plugin.label if plugin else None,
            "broker": plugin.plugin_name if plugin else None,
            "symbol": h.symbol,
            "exchange": h.exchange,
            "company_name": h.company_name,
            "sector": h.sector,
            "cap_tier": h.cap_tier,
            "quantity": h.quantity,
            "avg_buy_price": h.avg_buy_price,
            "last_price": h.last_price,
            "last_price_at": h.last_price_at,
            "week52_high": h.week52_high,
            "week52_low": h.week52_low,
            "rsi_14": h.rsi_14,
            "macd_hist": h.macd_hist,
            "trend": trend,
            "gain_loss": gain_loss,
            "gain_loss_pct": gain_loss_pct,
            "first_buy_date": h.first_buy_date.isoformat() if h.first_buy_date else None,
            "days_held": days_held,
            "flags": [f.__dict__ for f in flags],
        })
    return out


class PositionUpdate(BaseModel):
    # ISO date "YYYY-MM-DD", or null to clear it. Brokers don't supply the
    # purchase date, so the user sets it here to activate the holding-period
    # / long-term-tax flags.
    first_buy_date: Optional[str] = None


@router.patch("/positions/{holding_id}")
def update_position(holding_id: str, body: PositionUpdate,
                    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    holding = (
        db.query(Holding)
        .filter(Holding.id == holding_id, Holding.user_id == current_user.id)
        .first()
    )
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")

    if body.first_buy_date is None:
        holding.first_buy_date = None
    else:
        try:
            parsed = date.fromisoformat(body.first_buy_date)
        except ValueError:
            raise HTTPException(status_code=422, detail="first_buy_date must be YYYY-MM-DD")
        if parsed > date.today():
            raise HTTPException(status_code=422, detail="first_buy_date cannot be in the future")
        holding.first_buy_date = parsed

    db.commit()
    return {"id": holding.id, "first_buy_date": holding.first_buy_date.isoformat() if holding.first_buy_date else None}
