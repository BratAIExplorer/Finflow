# 🏦 Personal Wealth Hub v2.0 - ENHANCED ARCHITECTURE

## 🎯 Game-Changing Features

1. ✅ **Full Debt Tracking** - Loans, credit cards, mortgages with payment schedules
2. ✅ **Insurance Assets** - Life, health, vehicle policies with cash values
3. ✅ **Multi-Currency** - MYR, INR, USD, SGD with real-time conversion
4. ✅ **Premium Design** - Better than Kubera/Wealthica/Public.com
5. 🚀 **CUSTOM API PLUGIN SYSTEM** - Users add ANY broker/bank API they want!

---

## 📊 ENHANCED DATABASE SCHEMA

### 1. Manual Assets (Insurance, Property, Vehicles)

```sql
CREATE TABLE manual_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    
    -- Classification
    category VARCHAR(50) NOT NULL, 
    -- 'bank', 'property', 'insurance', 'epf', 'ppf', 'pension', 
    -- 'vehicle', 'jewelry', 'art', 'collectibles', 'business', 'other'
    
    subcategory VARCHAR(50),
    -- Insurance: 'term_life', 'whole_life', 'endowment', 'ulip', 'health', 'vehicle_insurance'
    -- Property: 'residential', 'commercial', 'land', 'reit'
    
    -- Basic Info
    name VARCHAR(255) NOT NULL,
    institution VARCHAR(255),
    account_number VARCHAR(100),
    
    -- Valuation
    value NUMERIC(24, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    value_in_base_currency NUMERIC(24, 2),
    
    -- INSURANCE-SPECIFIC FIELDS
    policy_number VARCHAR(100),
    policy_type VARCHAR(50),
    coverage_amount NUMERIC(24, 2),        -- Death benefit / Sum assured
    cash_value NUMERIC(24, 2),             -- Surrender value (investment policies)
    premium_amount NUMERIC(24, 2),
    premium_frequency VARCHAR(20),         -- 'monthly', 'quarterly', 'annual'
    premium_currency VARCHAR(3),
    policy_start_date DATE,
    policy_maturity_date DATE,
    beneficiary VARCHAR(255),
    
    -- PROPERTY-SPECIFIC FIELDS
    property_type VARCHAR(50),
    property_address TEXT,
    purchase_price NUMERIC(24, 2),
    purchase_date DATE,
    current_valuation NUMERIC(24, 2),
    rental_income_monthly NUMERIC(24, 2),
    rental_currency VARCHAR(3),
    
    -- VEHICLE-SPECIFIC
    vehicle_type VARCHAR(50),
    vehicle_make VARCHAR(100),
    vehicle_model VARCHAR(100),
    vehicle_year INTEGER,
    
    -- Metadata
    notes TEXT,
    tags TEXT[],
    attachments JSONB,                      -- Documents, photos
    last_updated TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_manual_assets_user_category ON manual_assets(user_id, category);
CREATE INDEX idx_manual_assets_currency ON manual_assets(currency);
```

---

### 2. Debts & Liabilities (Loans, Credit Cards, Mortgages)

```sql
CREATE TABLE debts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    
    -- Classification
    debt_type VARCHAR(50) NOT NULL,
    -- 'credit_card', 'personal_loan', 'home_loan', 'car_loan', 
    -- 'student_loan', 'business_loan', 'mortgage', 'line_of_credit', 'other'
    
    -- Basic Info
    name VARCHAR(255) NOT NULL,
    institution VARCHAR(255),
    account_number VARCHAR(100),
    
    -- Outstanding Balance
    outstanding_balance NUMERIC(24, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    outstanding_in_base_currency NUMERIC(24, 2),
    
    -- Loan Details
    original_loan_amount NUMERIC(24, 2),
    interest_rate NUMERIC(5, 2),           -- APR (e.g., 3.85%)
    interest_type VARCHAR(20),             -- 'fixed', 'variable', 'zero'
    
    -- Repayment Schedule
    monthly_payment NUMERIC(24, 2),
    minimum_payment NUMERIC(24, 2),        -- For credit cards
    next_payment_date DATE,
    loan_start_date DATE,
    loan_end_date DATE,
    
    -- CREDIT CARD SPECIFIC
    credit_limit NUMERIC(24, 2),
    available_credit NUMERIC(24, 2),       -- Calculated: limit - balance
    statement_date INTEGER,                -- Day of month (1-31)
    due_date INTEGER,                      -- Day of month (1-31)
    rewards_points NUMERIC(12, 2),         -- Current rewards balance
    annual_fee NUMERIC(10, 2),
    
    -- Tracking
    is_active BOOLEAN DEFAULT true,
    autopay_enabled BOOLEAN DEFAULT false,
    notes TEXT,
    tags TEXT[],
    last_updated TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_debts_user ON debts(user_id);
CREATE INDEX idx_debts_type ON debts(user_id, debt_type);
```

---

### 3. Debt Payment History

```sql
CREATE TABLE debt_payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    debt_id UUID REFERENCES debts(id) ON DELETE CASCADE,
    
    payment_date DATE NOT NULL,
    payment_amount NUMERIC(24, 2) NOT NULL,
    principal_amount NUMERIC(24, 2),
    interest_amount NUMERIC(24, 2),
    fees_amount NUMERIC(24, 2),
    remaining_balance NUMERIC(24, 2),
    
    payment_method VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_debt_payments_debt ON debt_payments(debt_id, payment_date);
```

---

### 4. Currency Rates (Real-Time Conversion)

```sql
CREATE TABLE currency_rates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    base_currency VARCHAR(3) NOT NULL,     -- 'USD'
    target_currency VARCHAR(3) NOT NULL,   -- 'MYR', 'INR', 'SGD'
    exchange_rate NUMERIC(12, 6) NOT NULL, -- e.g., 4.725000 USD→MYR
    
    rate_date DATE NOT NULL,
    source VARCHAR(50) DEFAULT 'exchangerate-api',
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(base_currency, target_currency, rate_date)
);

CREATE INDEX idx_currency_rates_lookup 
    ON currency_rates(base_currency, target_currency, rate_date DESC);
```

---

### 5. User Preferences (Multi-Currency)

```sql
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) UNIQUE,
    
    -- CURRENCY SETTINGS
    base_currency VARCHAR(3) DEFAULT 'USD',
    -- User's preferred display currency (all values converted to this)
    
    secondary_currencies TEXT[],
    -- ['MYR', 'INR'] - Show breakdown in these currencies too
    
    -- DISPLAY SETTINGS
    theme VARCHAR(20) DEFAULT 'light',
    number_format VARCHAR(20) DEFAULT 'en-US',  -- '1,234.56' vs '1.234,56'
    hide_zero_balances BOOLEAN DEFAULT false,
    
    -- NOTIFICATIONS
    email_weekly_summary BOOLEAN DEFAULT true,
    email_debt_reminders BOOLEAN DEFAULT true,  -- 5 days before due
    email_large_transactions BOOLEAN DEFAULT true,
    email_currency_alerts BOOLEAN DEFAULT false, -- When rates fluctuate >5%
    
    -- PRIVACY
    show_actual_values BOOLEAN DEFAULT true,     -- If false, show percentages only
    
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 💱 MULTI-CURRENCY SYSTEM

### Supported Currencies

```python
SUPPORTED_CURRENCIES = {
    "MYR": {
        "name": "Malaysian Ringgit",
        "symbol": "RM",
        "flag": "🇲🇾",
        "decimal_places": 2,
        "format": "RM {amount:,.2f}"
    },
    "INR": {
        "name": "Indian Rupee",
        "symbol": "₹",
        "flag": "🇮🇳",
        "decimal_places": 2,
        "format": "₹{amount:,.2f}",
        "lakhs_crores": true  # Display in lakhs/crores
    },
    "USD": {
        "name": "US Dollar",
        "symbol": "$",
        "flag": "🇺🇸",
        "decimal_places": 2,
        "format": "${amount:,.2f}"
    },
    "SGD": {
        "name": "Singapore Dollar",
        "symbol": "S$",
        "flag": "🇸🇬",
        "decimal_places": 2,
        "format": "S${amount:,.2f}"
    }
}
```

### Currency Service (Auto-Convert on Save)

```python
class CurrencyService:
    """
    Real-time currency conversion with caching
    """
    
    async def get_rate(self, from_curr: str, to_curr: str) -> float:
        """Get latest exchange rate with 24h cache"""
        if from_curr == to_curr:
            return 1.0
        
        # Check cache (Redis)
        cached = await redis.get(f"fx:{from_curr}:{to_curr}")
        if cached:
            return float(cached)
        
        # Fetch from API
        rate = await self._fetch_rate(from_curr, to_curr)
        
        # Cache for 24 hours
        await redis.setex(f"fx:{from_curr}:{to_curr}", 86400, rate)
        
        return rate
    
    async def convert(
        self, 
        amount: float, 
        from_curr: str, 
        to_curr: str
    ) -> float:
        """Convert amount between currencies"""
        rate = await self.get_rate(from_curr, to_curr)
        return amount * rate
    
    async def format_currency(
        self, 
        amount: float, 
        currency: str,
        use_lakhs_crores: bool = False
    ) -> str:
        """Format with currency symbol and locale"""
        config = SUPPORTED_CURRENCIES[currency]
        
        # Special formatting for INR (lakhs/crores)
        if currency == "INR" and use_lakhs_crores:
            if amount >= 10_000_000:  # 1 crore
                return f"₹{amount/10_000_000:.2f} Cr"
            elif amount >= 100_000:   # 1 lakh
                return f"₹{amount/100_000:.2f} L"
        
        return config["format"].format(amount=amount)
```

### Exchange Rate Providers

**Primary**: ExchangeRate-API (free 1,500 req/month)  
**Fallback**: Fixer.io / CurrencyAPI.com

```python
async def _fetch_rate(self, from_curr: str, to_curr: str) -> float:
    """Fetch from multiple providers with fallback"""
    providers = [
        ("https://api.exchangerate-api.com/v4/latest/", "free"),
        ("https://api.exchangerate.host/latest", "fallback_1"),
        ("https://api.currencyapi.com/v3/latest", "fallback_2")
    ]
    
    for url, provider in providers:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{url}{from_curr}")
                data = resp.json()
                return data["rates"][to_curr]
        except Exception as e:
            logger.warning(f"Provider {provider} failed: {e}")
            continue
    
    # Final fallback: last known rate from DB
    return await self._get_last_known_rate(from_curr, to_curr)
```

---

## 🔌 CUSTOM API PLUGIN SYSTEM (Game Changer!)

### Architecture Overview

```
┌─────────────────────────────────────────────────┐
│         Plugin/Connector Marketplace             │
│  • Built-in: Binance, Zerodha, IBKR, etc.      │
│  • Community: User-contributed connectors        │
│  • Premium: Paid APIs (Plaid, Yodlee)           │
│  • Custom: User-created DIY integrations        │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│          Plugin Engine (FastAPI)                 │
│  • Plugin Registry                               │
│  • Sandboxed Execution                          │
│  • Rate Limiting                                 │
│  • Error Handling                                │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│         Individual Plugin Instances              │
│  User1: [Binance, Custom Bank X, Plaid]        │
│  User2: [Zerodha, IBKR, Custom Crypto Y]       │
└──────────────────────────────────────────────────┘
```

### Plugin Database Schema

```sql
-- Plugin Registry (Available Connectors)
CREATE TABLE plugin_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Plugin Identity
    plugin_name VARCHAR(100) UNIQUE NOT NULL,   -- 'binance', 'zerodha', 'custom_bank_api'
    display_name VARCHAR(255),                  -- 'Binance Exchange'
    category VARCHAR(50),                        -- 'crypto', 'stocks', 'bank', 'custom'
    
    -- Plugin Type
    plugin_type VARCHAR(50) NOT NULL,
    -- 'builtin' - Pre-built by us
    -- 'community' - User-contributed
    -- 'premium' - Paid third-party (Plaid, Yodlee)
    -- 'custom' - User's own API integration
    
    -- Metadata
    description TEXT,
    logo_url VARCHAR(500),
    supported_countries TEXT[],                  -- ['MY', 'SG', 'IN', 'US']
    supported_asset_types TEXT[],                -- ['crypto', 'stocks', 'bonds']
    
    -- Pricing
    is_free BOOLEAN DEFAULT true,
    pricing_tier VARCHAR(50),                    -- 'free', 'premium', 'enterprise'
    monthly_cost NUMERIC(10, 2),
    
    -- Plugin Code/Config
    plugin_code TEXT,                            -- Python code or config JSON
    plugin_config_schema JSONB,                  -- Required fields for setup
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    requires_approval BOOLEAN DEFAULT false,     -- Community plugins need review
    
    -- Stats
    install_count INTEGER DEFAULT 0,
    rating NUMERIC(3, 2),                        -- 4.85
    
    created_by UUID REFERENCES users(id),        -- NULL for built-in
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User's Installed Plugins
CREATE TABLE user_plugins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    plugin_id UUID REFERENCES plugin_registry(id),
    
    -- Configuration
    custom_name VARCHAR(255),                    -- User's nickname for this connection
    credentials_encrypted JSONB,                 -- API keys, tokens (encrypted)
    config JSONB,                                -- User-specific settings
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    last_synced_at TIMESTAMP,
    last_sync_status VARCHAR(50),                -- 'success', 'failed', 'pending'
    last_error TEXT,
    
    -- Sync Settings
    auto_sync_enabled BOOLEAN DEFAULT true,
    sync_frequency_minutes INTEGER DEFAULT 60,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_plugins_user ON user_plugins(user_id);
```

---

### Plugin Interface (Standardized)

Every plugin must implement this interface:

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from datetime import datetime

class BasePlugin(ABC):
    """
    Base class for all broker/bank plugins
    """
    
    def __init__(self, credentials: Dict[str, str], config: Dict[str, Any]):
        self.credentials = credentials
        self.config = config
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if credentials are valid"""
        pass
    
    @abstractmethod
    async def get_balances(self) -> List[Dict]:
        """
        Return list of account balances
        
        Returns:
            [
                {
                    "asset_symbol": "BTC",
                    "asset_name": "Bitcoin",
                    "asset_type": "crypto",
                    "quantity": 0.5,
                    "current_price": 45000.00,
                    "current_value": 22500.00,
                    "currency": "USD",
                    "cost_basis": 20000.00,
                    "pnl": 2500.00,
                    "pnl_percent": 12.5
                },
                ...
            ]
        """
        pass
    
    @abstractmethod
    async def get_transactions(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict]:
        """
        Return transaction history
        
        Returns:
            [
                {
                    "transaction_type": "buy",
                    "asset_symbol": "BTC",
                    "quantity": 0.1,
                    "price": 44000.00,
                    "total_value": 4400.00,
                    "fee": 10.00,
                    "transaction_date": "2024-01-15T10:30:00Z"
                },
                ...
            ]
        """
        pass
    
    @property
    @abstractmethod
    def required_credentials(self) -> List[Dict]:
        """
        Define what credentials are needed
        
        Returns:
            [
                {
                    "name": "api_key",
                    "label": "API Key",
                    "type": "text",
                    "required": True,
                    "help_text": "Get from account settings"
                },
                {
                    "name": "api_secret",
                    "label": "API Secret",
                    "type": "password",
                    "required": True
                }
            ]
        """
        pass
    
    @property
    @abstractmethod
    def rate_limits(self) -> Dict:
        """
        Define API rate limits
        
        Returns:
            {
                "requests_per_minute": 60,
                "requests_per_day": 10000
            }
        """
        pass
```

---

### Built-In Plugins (We Provide)

#### 1. Binance Plugin

```python
class BinancePlugin(BasePlugin):
    """Official Binance Exchange connector"""
    
    BASE_URL = "https://api.binance.com"
    
    async def test_connection(self) -> bool:
        try:
            await self._make_request("/api/v3/account")
            return True
        except:
            return False
    
    async def get_balances(self) -> List[Dict]:
        account = await self._make_request("/api/v3/account")
        balances = []
        
        for balance in account["balances"]:
            free = float(balance["free"])
            locked = float(balance["locked"])
            total = free + locked
            
            if total > 0:
                ticker = await self._get_ticker(balance["asset"])
                balances.append({
                    "asset_symbol": balance["asset"],
                    "asset_type": "crypto",
                    "quantity": total,
                    "current_price": ticker["price"],
                    "current_value": total * ticker["price"],
                    "currency": "USDT"
                })
        
        return balances
    
    @property
    def required_credentials(self) -> List[Dict]:
        return [
            {
                "name": "api_key",
                "label": "Binance API Key",
                "type": "text",
                "required": True,
                "help_text": "Create at binance.com/en/my/settings/api-management",
                "help_url": "https://www.binance.com/en/support/faq/360002502072"
            },
            {
                "name": "api_secret",
                "label": "API Secret",
                "type": "password",
                "required": True
            }
        ]
    
    @property
    def rate_limits(self) -> Dict:
        return {
            "requests_per_minute": 1200,
            "requests_per_day": None
        }
```

---

### Community Plugins (User-Contributed)

Users can submit plugins to marketplace:

```python
class CustomBrokerPlugin(BasePlugin):
    """
    Template for creating custom broker plugins
    """
    
    # User fills in these values
    BASE_URL = "https://api.mybroker.com"
    
    async def get_balances(self) -> List[Dict]:
        # User implements their broker's API logic
        response = await httpx.get(
            f"{self.BASE_URL}/balances",
            headers={"Authorization": f"Bearer {self.credentials['api_key']}"}
        )
        
        # Transform to standard format
        raw_data = response.json()
        return [
            {
                "asset_symbol": item["symbol"],
                "quantity": item["qty"],
                "current_value": item["value"],
                ...
            }
            for item in raw_data
        ]
```

---

### Premium Plugins (Paid APIs)

#### Plaid Integration (Bank Aggregation)

```sql
-- Premium API Subscriptions
CREATE TABLE premium_api_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    
    api_provider VARCHAR(50), -- 'plaid', 'yodlee', 'saltpay'
    subscription_tier VARCHAR(50),
    
    -- Pricing
    monthly_cost NUMERIC(10, 2),
    currency VARCHAR(3),
    
    -- API Credentials (managed by us)
    api_credentials_encrypted JSONB,
    
    -- Limits
    max_connections INTEGER,
    max_refreshes_per_month INTEGER,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    subscription_start_date DATE,
    subscription_end_date DATE,
    
    created_at TIMESTAMP DEFAULT NOW()
);
```

```python
class PlaidPlugin(BasePlugin):
    """
    Plaid bank aggregation
    Cost: $0.25 per connection per month
    """
    
    async def link_bank_account(self) -> str:
        """
        Returns Plaid Link token for user to connect bank
        """
        client = plaid.Client(
            client_id=settings.PLAID_CLIENT_ID,
            secret=settings.PLAID_SECRET,
            environment=settings.PLAID_ENV
        )
        
        response = client.LinkToken.create({
            "user": {"client_user_id": str(self.user_id)},
            "client_name": "Personal Wealth Hub",
            "products": ["auth", "transactions"],
            "country_codes": ["US", "SG", "MY"],
            "language": "en"
        })
        
        return response["link_token"]
    
    async def get_balances(self) -> List[Dict]:
        """Pull live bank balances via Plaid"""
        accounts = await plaid_client.Accounts.balance.get(self.access_token)
        
        return [
            {
                "asset_symbol": acc["subtype"],  # 'checking', 'savings'
                "asset_name": acc["official_name"],
                "asset_type": "bank",
                "current_value": acc["balances"]["current"],
                "currency": acc["balances"]["iso_currency_code"]
            }
            for acc in accounts["accounts"]
        ]
```

---

### Custom API Builder (No-Code)

Visual interface for users to create their own plugins:

```json
{
  "plugin_name": "my_custom_broker",
  "display_name": "My Broker API",
  "api_config": {
    "base_url": "https://api.mybroker.com",
    "auth_type": "bearer_token",
    "auth_header": "Authorization",
    "auth_prefix": "Bearer "
  },
  "endpoints": {
    "get_balances": {
      "method": "GET",
      "path": "/v1/accounts/balances",
      "response_mapping": {
        "assets": "$.data.holdings",
        "asset_symbol": "$.symbol",
        "quantity": "$.quantity",
        "current_value": "$.market_value"
      }
    },
    "get_transactions": {
      "method": "GET",
      "path": "/v1/transactions",
      "query_params": {
        "start_date": "{start_date}",
        "end_date": "{end_date}"
      }
    }
  }
}
```

UI for this:

```
┌─────────────────────────────────────────┐
│  Create Custom API Integration          │
├─────────────────────────────────────────┤
│                                          │
│  Broker Name: [My Broker           ]    │
│  Base URL:    [https://api.mybroker.com]│
│                                          │
│  Authentication Type:                    │
│  ( ) API Key Header                      │
│  (•) Bearer Token                        │
│  ( ) Basic Auth                          │
│                                          │
│  ─────────────────────────────────────  │
│                                          │
│  Balance Endpoint                        │
│  Method: [GET ▼]                        │
│  Path: [/v1/balances              ]    │
│                                          │
│  Response Format (JSON):                │
│  {                                       │
│    "data": {                            │
│      "holdings": [                      │
│        {                                │
│          "symbol": "AAPL",              │
│          "quantity": 10,                │
│          "value": 1750.00               │
│        }                                │
│      ]                                  │
│    }                                    │
│  }                                      │
│                                          │
│  Field Mapping:                         │
│  Symbol:   [data.holdings[].symbol ]   │
│  Quantity: [data.holdings[].quantity]  │
│  Value:    [data.holdings[].value   ]  │
│                                          │
│  [Test Connection]  [Save Plugin]       │
└─────────────────────────────────────────┘
```

---

## 🎨 PREMIUM DESIGN SYSTEM

### Design Principles (Better than References)

1. **Glassmorphism** - Frosted glass cards, depth
2. **Micro-interactions** - Smooth hover, loading states
3. **Data Density** - More info, less scrolling
4. **Mobile-First** - Touch-optimized
5. **Performance** - <100ms interactions

### Color Palette

```css
/* Brand Gradient (Teal to Purple) */
--primary: #06B6D4;
--accent: #8B5CF6;
--gradient-brand: linear-gradient(135deg, #06B6D4 0%, #8B5CF6 100%);

/* Semantic Colors */
--success: #10B981;
--danger: #EF4444;
--warning: #F59E0B;
--info: #3B82F6;

/* Neutral Palette */
--gray-50: #FAFAF9;
--gray-100: #F5F5F4;
--gray-900: #1C1917;

/* Glass Effect */
--glass-bg: rgba(255, 255, 255, 0.7);
--glass-border: rgba(255, 255, 255, 0.18);
--glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
```

### Components (Shadcn + Custom)

```tsx
// Premium Card Component
<Card className="glass-card hover-lift">
  <CardHeader className="gradient-border">
    <CardTitle className="flex items-center gap-2">
      <IconTrendingUp className="text-success" />
      Net Worth
    </CardTitle>
  </CardHeader>
  <CardContent>
    <CurrencyDisplay 
      amount={245832} 
      currency="USD"
      showChange={true}
      changePercent={5.3}
      trend="up"
    />
  </CardContent>
</Card>
```

### Dashboard Layout (Mobile-First)

```
┌─────────────────────────────────────────┐
│  💰 Personal Wealth Hub    🇺🇸 USD  ⚙️  │
├─────────────────────────────────────────┤
│                                          │
│  ╔══════════════════════════════════╗  │
│  ║  Net Worth                        ║  │
│  ║  $245,832                         ║  │
│  ║  +$12,450 (5.3%) ↑ 30D           ║  │
│  ╚══════════════════════════════════╝  │
│                                          │
│  ┌────────────────┬────────────────┐  │
│  │ Total Assets   │ Total Debts    │  │
│  │ $287,421       │ $41,589        │  │
│  │ +8.2% ↑        │ -2.1% ↓        │  │
│  └────────────────┴────────────────┘  │
│                                          │
│  📊 Asset Allocation                   │
│  ╭────────────────────────────────────╮│
│  │ ████████░░░░ 45% Crypto $129,439  ││
│  │ ██████░░░░░░ 30% Stocks  $86,227  ││
│  │ ███░░░░░░░░░ 15% Cash    $43,113  ││
│  │ ██░░░░░░░░░░ 10% Other   $28,642  ││
│  ╰────────────────────────────────────╯│
│                                          │
│  🔗 Connected Accounts (4)             │
│                                          │
│  ┌──────────────────────────────────┐  │
│  │ 🟡 Binance  •2m ago             │  │
│  │ $85,420  +$1,250 (1.5%) ↑       │  │
│  │ [BTC] [ETH] [SOL] +12           │  │
│  └──────────────────────────────────┘  │
│                                          │
│  ┌──────────────────────────────────┐  │
│  │ 🔵 Zerodha  •5m ago             │  │
│  │ ₹35,42,180  +₹74,890 (2.1%) ↑  │  │
│  │ [RELIANCE] [TCS] [INFY] +8      │  │
│  └──────────────────────────────────┘  │
│                                          │
│  💳 Credit Cards (2)                   │
│                                          │
│  ┌──────────────────────────────────┐  │
│  │ CIMB Platinum                     │  │
│  │ RM 4,520 / RM 50,000             │  │
│  │ ▓▓░░░░░░░░ 9% utilization        │  │
│  │ Due: Feb 5 (9 days)              │  │
│  └──────────────────────────────────┘  │
│                                          │
└─────────────────────────────────────────┘
```

---

## 🚀 IMPLEMENTATION ROADMAP

### Phase 1: Core + Multi-Currency (Week 1-2)
- ✅ Backend (FastAPI + PostgreSQL)
- ✅ Multi-currency support (MYR, INR, USD, SGD)
- ✅ Manual assets (insurance, property, vehicles)
- ✅ Debts (loans, credit cards)
- ✅ Basic dashboard

### Phase 2: Built-In Brokers (Week 3-4)
- ✅ Binance plugin
- ✅ LUNO plugin
- ✅ Zerodha plugin
- ✅ IBKR plugin

### Phase 3: Plugin System (Week 5-6)
- ✅ Plugin registry & engine
- ✅ Custom API builder (no-code)
- ✅ Community plugin marketplace
- ✅ Premium API integrations (Plaid)

### Phase 4: Premium Design (Week 7-8)
- ✅ Glassmorphism UI
- ✅ Micro-interactions
- ✅ Mobile optimization
- ✅ Dark mode

---

**This is now MORE powerful than any existing wealth tracker!** 🚀

Key differentiators:
1. **Full debt tracking** (others are weak here)
2. **Insurance with cash values** (nobody does this well)
3. **True multi-currency** (not just display conversion)
4. **Custom API plugins** (GAME CHANGER - users can add ANY broker)
5. **Premium design** (better than Kubera/Wealthica)

Ready to build? Just tell me:
1. **Platform**: Railway / Render
2. **First features**: MVP crypto / Full enhanced
3. **API keys**: Binance + LUNO to start

Let's go! 🎯
