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
    plugin_name = Column(String) # e.g., binance, custom
    is_active = Column(Boolean, default=True)
    credentials_encrypted = Column(JSON)
    
    # Configuration for the no-code engine
    config = Column(JSON) # URL, Mapping, etc.
    
    last_synced = Column(DateTime)
    user = relationship("User", back_populates="plugins")

class CurrencyRate(Base):
    __tablename__ = "currency_rates"
    id = Column(Integer, primary_key=True)
    from_currency = Column(String)
    to_currency = Column(String)
    rate = Column(Float)
    updated_at = Column(DateTime, default=func.now())
