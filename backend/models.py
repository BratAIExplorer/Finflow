from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, JSON, Date, Table
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

# Many-to-many relationship for family sharing
family_sharing_table = Table(
    'family_sharing',
    Base.metadata,
    Column('id', String, primary_key=True, default=lambda: str(uuid.uuid4())),
    Column('sharer_id', String, ForeignKey('users.id')),
    Column('recipient_id', String, ForeignKey('users.id')),
    Column('can_view_networth', Boolean, default=True),
    Column('can_view_holdings', Boolean, default=False),
    Column('shared_at', DateTime, default=func.now())
)

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    preferences = relationship("UserPreferences", back_populates="user", uselist=False)
    assets = relationship("ManualAsset", back_populates="user")
    debts = relationship("Debt", back_populates="user")
    plugins = relationship("UserPlugin", back_populates="user")

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    base_currency = Column(String, default="MYR")  # Priority: MYR, INR
    theme = Column(String, default="dark")
    lakhs_crores_format = Column(Boolean, default=True) # For INR

    user = relationship("User", back_populates="preferences")

class ManualAsset(Base):
    __tablename__ = "manual_assets"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    category = Column(String) # bank, property, insurance, etc.
    name = Column(String)
    institution = Column(String)
    value = Column(Float)
    currency = Column(String)

    # Specific fields stored as JSON for flexibility
    details = Column(JSON) # e.g., policy_number, maturity_date for insurance

    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    user = relationship("User", back_populates="assets")

class Debt(Base):
    __tablename__ = "debts"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    debt_type = Column(String) # loan, credit_card
    name = Column(String)
    outstanding_balance = Column(Float)
    currency = Column(String)
    interest_rate = Column(Float)
    monthly_payment = Column(Float)
    due_date = Column(Integer) # Day of month

    user = relationship("User", back_populates="debts")

class UserPlugin(Base):
    __tablename__ = "user_plugins"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    plugin_name = Column(String) # e.g., binance, mstock, zerodha, custom
    label = Column(String, nullable=True) # display name, e.g. "Dad's Zerodha" — lets one user hold two accounts of the same broker
    is_active = Column(Boolean, default=True)
    credentials_encrypted = Column(JSON)

    # Configuration for the no-code engine
    config = Column(JSON) # URL, Mapping, etc.

    last_synced = Column(DateTime)
    last_sync_error = Column(String, nullable=True)
    user = relationship("User", back_populates="plugins")
    holdings = relationship("Holding", back_populates="plugin")

class Holding(Base):
    """A single broker-synced stock position, one row per (plugin, symbol).
    Read-only mirror of a broker's holdings API — never used to place trades."""
    __tablename__ = "holdings"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plugin_id = Column(String, ForeignKey("user_plugins.id"))
    user_id = Column(String, ForeignKey("users.id"))  # denormalized for simpler queries

    symbol = Column(String)          # e.g. "HDFCBANK"
    exchange = Column(String)        # e.g. "NSE", "BSE"
    isin = Column(String, nullable=True)
    quantity = Column(Float)
    avg_buy_price = Column(Float)
    currency = Column(String, default="INR")
    first_buy_date = Column(Date, nullable=True)  # user-entered; brokers don't supply it. Drives holding-period / tax flags.

    # Company classification, refreshed on each sync from the free public feed (Yahoo).
    # Best-effort: any of these can stay null if Yahoo has no data for the symbol.
    company_name = Column(String, nullable=True)   # e.g. "HDFC Bank Limited"
    sector = Column(String, nullable=True)         # e.g. "Financial Services"
    cap_tier = Column(String, nullable=True)       # "Large" | "Mid" | "Small" | "Penny"

    # Latest price snapshot, refreshed on each sync (free public feed, not the broker's paid feed)
    last_price = Column(Float, nullable=True)
    last_price_at = Column(DateTime, nullable=True)
    week52_high = Column(Float, nullable=True)
    week52_low = Column(Float, nullable=True)
    rsi_14 = Column(Float, nullable=True)
    macd_hist = Column(Float, nullable=True)  # MACD line minus signal line; sign+magnitude drives the trend label

    plugin = relationship("UserPlugin", back_populates="holdings")


class TrendSnapshot(Base):
    """One recorded trend call for a holding, taken by the daily end-of-day job
    (backend/jobs/trend_snapshot.py). Exists so we can later check whether a
    Bullish/Bearish label actually predicted the price move, instead of only
    ever seeing the latest label like Holding does."""
    __tablename__ = "trend_snapshots"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    holding_id = Column(String, ForeignKey("holdings.id"))
    symbol = Column(String)    # denormalized, same reasoning as Holding.user_id
    exchange = Column(String)  # survives the holding row being deleted/re-created on re-sync

    captured_at = Column(DateTime, default=func.now())
    price_at_capture = Column(Float)
    rsi_14 = Column(Float, nullable=True)
    macd_hist = Column(Float, nullable=True)
    trend_label = Column(String)     # "Very Bullish" | "Bullish" | "Neutral" | "Bearish" | "Very Bearish" | "Unknown"
    direction = Column(String)       # "up" | "down" | "flat", from classify_trend()

    # Graded by grade_pending_snapshots() once each window has elapsed.
    # hit_* is null = pending, true/false once graded. "flat" (Neutral) snapshots
    # are never graded — there's no direction to check against.
    price_1d = Column(Float, nullable=True)
    hit_1d = Column(Boolean, nullable=True)
    price_7d = Column(Float, nullable=True)
    hit_7d = Column(Boolean, nullable=True)
    price_30d = Column(Float, nullable=True)
    hit_30d = Column(Boolean, nullable=True)
