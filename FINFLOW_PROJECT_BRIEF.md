# 🏦 Finflow - Personal Wealth Hub
**Project Brief & Technical Specification**

*Last Updated: January 27, 2025*

---

## 📋 TABLE OF CONTENTS
1. [Project Overview](#project-overview)
2. [Core Features](#core-features)
3. [Technical Architecture](#technical-architecture)
4. [Implementation Roadmap](#implementation-roadmap)
5. [Current Status](#current-status)
6. [Next Steps](#next-steps)

---

## 🎯 PROJECT OVERVIEW

### Mission
Build a personal wealth tracking platform that automatically aggregates ALL my financial accounts (crypto, stocks, banks, insurance, debts) across multiple currencies into one beautiful dashboard.

### Target Users
1. **Primary**: Me (Malaysian resident, crypto + stocks investor)
2. **Secondary**: Family members (dad in India with Zerodha account)
3. **Tertiary**: Friends & extended network

### The Problem We're Solving
- Financial data scattered across 6+ brokers/exchanges
- Manual tracking in spreadsheets is tedious
- Existing solutions (Wealthica, Kubera) lack:
  - Full debt tracking
  - Insurance with cash values
  - Custom broker plugins
  - Premium design quality

### Success Criteria
- ✅ **MVP**: See my entire net worth in one dashboard
- ✅ **Phase 2**: All brokers auto-syncing every 5-60 minutes
- ✅ **Phase 3**: Family members can use it with their own accounts
- ✅ **Phase 4**: Users can add custom broker APIs (plugin system)

---

## 💎 CORE FEATURES

### 1. Asset Tracking
**Auto-Sync Accounts**:
- 🟡 Binance (crypto exchange)
- 🟠 LUNO (SEA crypto platform)
- 🔵 Zerodha (Indian stocks)
- 🟣 Interactive Brokers (US/global stocks)
- 🟢 Moomoo (US/Asian markets)
- ⚪ Mstock (Indian broker)

**Manual Assets**:
- 🏦 Bank accounts (savings, fixed deposits)
- 🏠 Real estate (residential, commercial, REITs)
- 🛡️ Insurance (term life, whole life, endowment, ULIP)
  - Track: Coverage amount, cash value, beneficiary, premiums
- 🚗 Vehicles (cars, motorcycles)
- 💰 EPF / PPF / Pension funds
- 💎 Other (jewelry, art, collectibles, business equity)

### 2. Debt Management
**Credit Cards**:
- Outstanding balance
- Credit limit & utilization %
- Minimum payment vs full balance
- Due dates with reminders
- Interest calculation if minimum paid

**Loans**:
- 🏡 Home loans / Mortgages
- 🚗 Car loans
- 👤 Personal loans
- 🎓 Student loans
- 📊 Payment schedules & amortization

### 3. Multi-Currency System
**Supported Currencies**:
- 🇺🇸 USD (US Dollar)
- 🇲🇾 MYR (Malaysian Ringgit)
- 🇮🇳 INR (Indian Rupee) - with lakhs/crores formatting
- 🇸🇬 SGD (Singapore Dollar)

**Features**:
- Real-time exchange rate conversion
- User-selectable base currency
- Smart formatting (₹1.2L instead of ₹120,000)
- Show amounts in multiple currencies simultaneously
- Historical rate tracking

### 4. Custom API Plugin System 🚀
**Game Changer**: Users can add ANY broker/bank they want!

**Three Types of Plugins**:
1. **Built-in** - Pre-built by us (Binance, Zerodha, etc.)
2. **Community** - User-contributed and shared
3. **Premium** - Paid third-party (Plaid, Yodlee for bank aggregation)
4. **Custom** - No-code API builder for personal use

**No-Code API Builder**:
- Visual interface to configure any REST API
- Map JSON responses to standard format
- Test connection wizard
- Save as private plugin

### 5. Premium Design
**Better than Kubera, Wealthica, Public.com**:
- ✨ Glassmorphism (frosted glass cards)
- 🎬 Smooth micro-interactions (no spinners, only skeletons)
- 📱 Mobile-first responsive design
- 🌈 Modern gradient color system
- ⚡ Fast (<2s load time)
- 🌙 Dark mode support

---

## 🏗️ TECHNICAL ARCHITECTURE

### Tech Stack

#### Backend
```
Language: Python 3.11+
Framework: FastAPI
Database: PostgreSQL 15
Cache: Redis
Task Queue: APScheduler (background jobs)
Authentication: JWT tokens
Encryption: Fernet (for API keys)
```

#### Frontend
```
Framework: React 18 + TypeScript
Styling: Tailwind CSS + shadcn/ui components
Charts: Recharts
State Management: Zustand
API Client: TanStack Query (React Query)
Build Tool: Vite
```

#### Deployment
```
Platform: Railway (recommended) / Render / DigitalOcean
Containerization: Docker + Docker Compose
CI/CD: GitHub Actions
Monitoring: Sentry (error tracking)
SSL: Let's Encrypt (automatic via Railway)
```

### Database Schema (Simplified)

```sql
-- Core Tables
users (id, email, password_hash, created_at)
user_preferences (user_id, base_currency, theme, notifications)

-- Connected Accounts
accounts (id, user_id, broker, api_key_encrypted, last_synced_at)
holdings (id, account_id, asset_symbol, quantity, current_value, pnl)
transactions (id, account_id, type, asset, quantity, price, date)

-- Manual Assets
manual_assets (id, user_id, category, name, value, currency, 
              insurance_fields, property_fields, vehicle_fields)

-- Debts
debts (id, user_id, debt_type, outstanding_balance, interest_rate,
       monthly_payment, due_date, credit_limit)
debt_payments (id, debt_id, payment_date, amount, principal, interest)

-- Multi-Currency
currency_rates (base_currency, target_currency, rate, date)

-- Plugin System
plugin_registry (id, plugin_name, plugin_type, code, config_schema)
user_plugins (id, user_id, plugin_id, credentials_encrypted, is_active)

-- Tracking
networth_history (user_id, total_assets, total_debts, net_worth, date)
```

### API Integrations

#### Exchange Rate Provider
- **Primary**: ExchangeRate-API (free 1,500 req/month)
- **Fallback**: Fixer.io / CurrencyAPI
- **Cache**: 24 hours (update daily at 00:00 UTC)

#### Broker APIs
| Broker | API Type | Rate Limit | Refresh Frequency |
|--------|----------|------------|-------------------|
| Binance | REST + WebSocket | 1200 req/min | 5 minutes |
| LUNO | REST | 10 req/sec | 10 minutes |
| Zerodha | Kite Connect (OAuth) | 3 req/sec | 15 minutes |
| IBKR | Client Portal API | Varies | 30 minutes |
| Moomoo | OpenAPI | 100 req/min | 10 minutes |

#### Bank Aggregation (Premium)
- **Plaid**: $0.25 per connection/month (US, SG, some MY banks)
- **Yodlee**: $20-50/month flat fee
- **SaltPay**: Alternative for SEA banks

### Security Model

**Principles**:
1. **Read-only API keys ONLY** - No trading, no withdrawals
2. **Encrypted at rest** - All API keys use Fernet encryption
3. **HTTPS everywhere** - Let's Encrypt SSL
4. **JWT authentication** - Short-lived tokens with refresh
5. **Rate limiting** - Prevent API abuse
6. **Audit logging** - Track all sensitive operations

**Master Key**: Stored as environment variable, never in code

---

## 📅 IMPLEMENTATION ROADMAP

### Phase 1: MVP Core (Week 1-2)
**Goal**: Manual tracking + basic crypto auto-sync

**Tasks**:
- [x] Backend setup (FastAPI + PostgreSQL + Docker)
- [x] Database schema implementation
- [ ] User authentication (register, login, JWT)
- [ ] Multi-currency system
  - [ ] Exchange rate API integration
  - [ ] Conversion functions
  - [ ] Currency formatting
- [ ] Manual asset forms
  - [ ] Bank accounts
  - [ ] Insurance policies
  - [ ] Property
  - [ ] Vehicles
- [ ] Manual debt forms
  - [ ] Credit cards
  - [ ] Loans
- [ ] Binance API integration
- [ ] LUNO API integration
- [ ] Basic dashboard
  - [ ] Net worth card
  - [ ] Asset vs debt breakdown
  - [ ] Currency switcher
- [ ] VPS deployment (Railway)

**Deliverable**: I can see my net worth (crypto + manual assets) in one dashboard

---

### Phase 2: Stock Brokers (Week 3-4)
**Goal**: Auto-sync all broker accounts

**Tasks**:
- [ ] Plugin system foundation
  - [ ] Plugin registry database
  - [ ] Base plugin interface
  - [ ] Credential encryption
- [ ] Built-in plugins
  - [ ] Zerodha Kite API
  - [ ] IBKR Client Portal API
  - [ ] Moomoo OpenAPI
- [ ] Auto-sync engine
  - [ ] APScheduler background jobs
  - [ ] Rate limit management
  - [ ] Error handling & retry
- [ ] Enhanced dashboard
  - [ ] Connected accounts list
  - [ ] Holdings breakdown per account
  - [ ] Performance charts (6M, 1Y)
  - [ ] Transaction history

**Deliverable**: All my brokers auto-sync, full portfolio visibility

---

### Phase 3: Custom Plugins (Week 5-6)
**Goal**: Users can add their own brokers

**Tasks**:
- [ ] Plugin marketplace
  - [ ] Browse/search available plugins
  - [ ] Install/uninstall
  - [ ] Ratings & reviews
- [ ] No-code API builder
  - [ ] Visual configuration UI
  - [ ] Response mapping tool
  - [ ] Test connection wizard
  - [ ] Save as personal plugin
- [ ] Community plugins
  - [ ] Submit plugin for review
  - [ ] Version control
  - [ ] Documentation generator
- [ ] Premium APIs
  - [ ] Plaid integration (bank aggregation)
  - [ ] Yodlee integration
  - [ ] Subscription management

**Deliverable**: Users can add ANY broker, even ones I've never heard of

---

### Phase 4: Premium Polish (Week 7-8)
**Goal**: Production-ready, beautiful UX

**Tasks**:
- [ ] Design system implementation
  - [ ] Glassmorphic cards
  - [ ] Gradient system
  - [ ] Micro-interactions
  - [ ] Loading skeletons
- [ ] Advanced features
  - [ ] Interactive charts (Recharts)
  - [ ] Asset allocation donut chart
  - [ ] Debt payoff calculator
  - [ ] Export to Excel/CSV
- [ ] Mobile optimization
  - [ ] Touch-optimized UI
  - [ ] Bottom navigation
  - [ ] Swipe gestures
  - [ ] Pull-to-refresh
- [ ] Dark mode
- [ ] Notifications
  - [ ] Weekly summary emails
  - [ ] Debt due reminders
  - [ ] Large transaction alerts

**Deliverable**: Production-ready, better than any competitor

---

### Phase 5: Multi-User (Week 9+)
**Goal**: Scale to family & friends

**Tasks**:
- [ ] User management (registration, email verification)
- [ ] Multi-tenant architecture
- [ ] Family features
  - [ ] Invitation system
  - [ ] Family net worth roll-up
  - [ ] Privacy controls
- [ ] Billing (optional)
  - [ ] Free tier
  - [ ] Premium tier
  - [ ] Payment processing

**Deliverable**: SaaS platform for family & friends

---

## 📊 CURRENT STATUS

**Date**: January 27, 2025

### ✅ Completed
- [x] Product requirements defined
- [x] Technical architecture designed
- [x] Database schema finalized
- [x] Multi-currency strategy planned
- [x] Plugin system architecture designed
- [x] Premium design system specified
- [x] Implementation roadmap created

### 🏗️ In Progress
- [ ] Backend setup (FastAPI + PostgreSQL)
- [ ] Railway deployment configuration

### ⏳ Next Up (Immediate)
1. Deploy initial backend to Railway
2. Implement user authentication
3. Build manual asset forms
4. Integrate Binance API
5. Create basic dashboard UI

### 🚧 Blockers
- Waiting for Railway account setup
- Need Binance API keys (read-only)
- Need LUNO API keys (read-only)

### 💡 Open Questions
- Should we prioritize Plaid integration early?
- Dark mode in MVP or Phase 4?
- Do we need Mstock integration or is CSV import enough?

---

## 💰 COST BREAKDOWN

### Development
- **Your Cost**: $0 (I'm building it)

### Monthly Running Costs

#### Recommended: Railway
```
Platform Service: $5-10/month
PostgreSQL: Included
Redis: Included
Domain (optional): ~$1/month
Total: $10-15/month
```

#### Budget Option: Render
```
PostgreSQL: Free tier
Web Service: Free (sleeps) or $7/month
Total: $0-7/month
```

### Premium Features (Optional)
```
Plaid API: $0.25 per bank connection/month
Yodlee: $20-50/month
ExchangeRate-API: Free (1500 req/month)
```

**Recommendation**: Start with Railway ($10-15/month), add Plaid only if users request bank aggregation.

---

## 🎯 NEXT STEPS

### Immediate Actions (This Week)

**You**:
1. Create Railway account (railway.app)
2. Obtain read-only API keys:
   - Binance: API Key + Secret
   - LUNO: API Key + Secret
3. Choose domain name (optional): finflow.yourname.com

**Me**:
1. Initialize FastAPI project structure
2. Set up PostgreSQL database schema
3. Deploy initial backend to Railway
4. Implement user authentication
5. Build currency conversion system

### Week 1 Milestones
- [ ] Backend deployed and accessible via HTTPS
- [ ] Database schema live
- [ ] User registration/login working
- [ ] Currency conversion working
- [ ] Manual asset forms functional

### Week 2 Milestones
- [ ] Binance integration complete
- [ ] LUNO integration complete
- [ ] Basic dashboard displaying net worth
- [ ] Currency switcher working
- [ ] Manual assets + debts tracked

---

## 🔍 KEY DIFFERENTIATORS

### vs Kubera
1. ✅ Custom plugin system (users add their own brokers)
2. ✅ Better mobile experience
3. ✅ Glassmorphic modern design
4. ✅ Full debt management with schedules
5. ✅ Insurance with cash values

### vs Wealthica
1. ✅ Superior UI/UX
2. ✅ True multi-currency (not just conversion)
3. ✅ Loan amortization schedules
4. ✅ Credit card optimization
5. ✅ No-code custom API builder

### vs Public.com
1. ✅ Net worth aggregation (not just trading)
2. ✅ Debt management
3. ✅ Multi-account consolidation
4. ✅ Insurance portfolio tracking
5. ✅ Family sharing features

### 🚀 UNIQUE ADVANTAGE
**Plugin system**: Users can add ANY broker/bank API themselves. This is unprecedented in wealth tracking apps and solves the "long tail" problem where competitors need years to add every broker globally.

---

## 📞 LET'S BUILD!

**To start building TODAY**, provide:

1. **Deployment choice**: Railway (recommended) or Render
2. **API credentials** (when ready):
   - Binance API Key + Secret (read-only permissions)
   - LUNO API Key + Secret (read-only permissions)
3. **Email**: For deployment notifications
4. **Preferred domain** (optional): finflow.yourname.com

Then I'll:
- Set up the complete backend
- Deploy to Railway/Render
- Implement first broker integration
- Build basic dashboard
- Provide you with a working URL within 1-2 weeks

**Ready when you are!** 🚀

---

*This document is the single source of truth for Finflow. All other documentation is derivative of this brief.*
