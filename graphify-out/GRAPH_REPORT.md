# Graph Report - FinFlow  (2026-09-14)

## Corpus Check
- 108 files · ~70,340 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1175 nodes · 1639 edges · 86 communities (67 shown, 19 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 58 edges (avg confidence: 0.73)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9549a1b6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Finflow/backend/routers/auth.py
- RawHolding
- Python requirements.txt
- backend/main.py
- devDependencies
- dependencies
- holdings.py
- pricing.py
- FinFlow Personal Wealth Hub
- frontend/app/page.tsx
- 🎨 Personal Wealth Hub - PREMIUM DESIGN MOCKUPS
- BasePlugin Interface
- 🎨 Personal Wealth Hub - PREMIUM DESIGN MOCKUPS
- TypeScript Configuration
- 🎨 Personal Wealth Hub - PREMIUM DESIGN MOCKUPS
- Deployment and Architecture
- ✅ Implementation Checklist - Personal Wealth Hub v2.0
- Wealth Hub Features
- 🔌 CUSTOM API PLUGIN SYSTEM (Game Changer!)
- ✅ Implementation Checklist - Personal Wealth Hub v2.0
- Frontend Layout and Fonts
- ✅ Implementation Checklist - Personal Wealth Hub v2.0
- 🔌 CUSTOM API PLUGIN SYSTEM (Game Changer!)
- 🔌 CUSTOM API PLUGIN SYSTEM (Game Changer!)
- ESLint Configuration
- Next.js Configuration
- PostCSS Configuration
- 📋 Finflow Documentation Analysis
- compilerOptions
- Finflow/frontend/components/AddAssetForm.tsx
- devDependencies
- dependencies
- 🏗️ TECHNICAL ARCHITECTURE
- 🚀 Deployment Guide: VPS with Docker
- Finflow/frontend/package.json
- frontend/package.json
- 🏦 Finflow - Personal Wealth Hub
- Uvicorn FastAPI Backend (port 8000)
- FinFlow Current Status (Updated: Feb 7, 2026)
- backend/routers/holdings.py
- FinFlow Platform
- 💎 CORE FEATURES
- 📊 CURRENT STATUS
- 💰 COST BREAKDOWN
- 📅 IMPLEMENTATION ROADMAP
- Local Development Setup (No Docker)
- backend (FastAPI container)
- 🔍 KEY DIFFERENTIATORS
- 🎯 PROJECT OVERVIEW
- Finflow/frontend/app/layout.tsx
- frontend/README.md
- gen_status.py
- ARCHITECTURE.md
- Finflow/frontend/eslint.config.mjs
- Finflow/frontend/next.config.ts
- clsx
- holdingsFormat.ts
- lucide-react
- next
- tailwind-merge
- Finflow/frontend/postcss.config.mjs
- PROJECT.md
- clsx
- framer-motion
- test_backtest_trend.py
- recharts
- tailwind-merge
- test_trend_snapshot.py
- backend/routers/auth.py
- test_holdings.py
- backend/models.py
- _FakeClient
- BrokerConnectionError
- plain_flags.py
- news.py
- Key Integration Details
- MStockConnector
- recharts
- lucide-react

## God Nodes (most connected - your core abstractions)
1. `BrokerConnectionError` - 17 edges
2. `ZerodhaConnector` - 17 edges
3. `Python requirements.txt` - 17 edges
4. `compilerOptions` - 16 edges
5. `compilerOptions` - 16 edges
6. `MStockConnector` - 14 edges
7. `backtest_symbol()` - 14 edges
8. `RawHolding` - 13 edges
9. `record_snapshot()` - 13 edges
10. `_FakeClient` - 12 edges

## Surprising Connections (you probably didn't know these)
- `Multi-Currency First UI (always-visible switcher)` --semantically_similar_to--> `Multi-Currency System (MYR/INR/USD/SGD)`  [INFERRED] [semantically similar]
  PREMIUM_DESIGN_MOCKUPS.md → FINFLOW_PROJECT_BRIEF.md
- `Plugin System` --semantically_similar_to--> `Custom API Plugin System`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → WEALTH_HUB_V2_ENHANCED.md
- `db (postgres:16-alpine)` --semantically_similar_to--> `PostgreSQL 14+ Local/Cloud Database`  [INFERRED] [semantically similar]
  docker-compose.yml → SETUP_LOCAL.md
- `Glassmorphism + Depth Design` --semantically_similar_to--> `Premium Glassmorphism Design`  [INFERRED] [semantically similar]
  PREMIUM_DESIGN_MOCKUPS.md → FINFLOW_PROJECT_BRIEF.md
- `Architecture Tech Stack` --semantically_similar_to--> `FinFlow Tech Stack (FastAPI/PostgreSQL/Redis/React)`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → FINFLOW_PROJECT_BRIEF.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **FinFlow MVP Stack and Deployment** — architecture_tech_stack, finflow_project_brief_tech_stack, deployment_vps_docker [INFERRED 0.75]
- **Read-Only Broker Integration Flow** — finflow_project_brief_broker_apis, current_status_broker_holdings_backend, implementation_checklist_plugin_system_foundation, implementation_checklist_auto_sync_engine [INFERRED 0.75]
- **Three Essential FinFlow Docs** — finflow_docs_analysis_project_md, finflow_docs_analysis_architecture_md, finflow_docs_analysis_current_status_md, finflow_docs_analysis_minimal_documentation [EXTRACTED 0.75]
- **Broker Holdings Dashboard Pipeline** — readme_backend_holdings_router, readme_broker_base, readme_pricing_module, readme_crypto_utils, readme_plain_flags [EXTRACTED 0.95]
- **FinFlow Docker Compose Stack** — docker_compose_db, docker_compose_redis, docker_compose_backend, docker_compose_frontend [EXTRACTED 0.95]
- **Multi-Currency Conversion Subsystem** — wealth_hub_v2_enhanced_currency_service, wealth_hub_v2_enhanced_currency_rates, wealth_hub_v2_enhanced_exchangerate_api, wealth_hub_v2_enhanced_redis_fx_cache [EXTRACTED 0.95]

## Communities (86 total, 19 thin omitted)

### Community 0 - "Finflow/backend/routers/auth.py"
Cohesion: 0.06
Nodes (43): CurrencyService, create_access_token(), get_password_hash(), timedelta, verify_password(), CurrencyService, get_db(), init_db() (+35 more)

### Community 1 - "RawHolding"
Cohesion: 0.17
Nodes (10): ABC, BrokerConnector, Shared contract every broker connector implements. This is the "no-code plugin"…, What a broker connector hands back for one stock position, before any…, One instance = one broker ACCOUNT (not one broker). Two Zerodha logins are two…, Make sure we have a valid, non-expired session token, refreshing it if the…, Return every current stock position. Must call ensure_session() first., RawHolding (+2 more)

### Community 2 - "Python requirements.txt"
Cohesion: 0.18
Nodes (14): JWT Authentication, backend/pricing.py, RSI/MACD/52-week Range Signals, fastapi, httpx, pandas, passlib[bcrypt], pydantic (+6 more)

### Community 3 - "backend/main.py"
Cohesion: 0.16
Nodes (15): get_db(), init_db(), on_startup(), get, on_event, root(), _run_daily_trend_job(), get_shared_access() (+7 more)

### Community 4 - "devDependencies"
Cohesion: 0.12
Nodes (17): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom (+9 more)

### Community 5 - "dependencies"
Cohesion: 0.13
Nodes (15): dependencies, class-variance-authority, @hookform/resolvers, next, react, react-dom, react-hook-form, zod (+7 more)

### Community 6 - "holdings.py"
Cohesion: 0.14
Nodes (35): decrypt_credentials(), encrypt_credentials(), _get_fernet(), Encrypts/decrypts broker credentials (API keys, TOTP secrets) before they touch…, dict -> encrypted string, safe to store in a JSON/String column., encrypted string -> dict. Raises cryptography.fernet.InvalidToken if the key is…, add_broker_account(), delete_broker_account() (+27 more)

### Community 7 - "pricing.py"
Cohesion: 0.29
Nodes (9): _cap_tier(), CompanyMeta, fetch_company_meta(), fetch_daily_history(), DataFrame, Free public price data + simple technical signals — deliberately NOT pulled…, Best-effort company classification from Yahoo's .info blob. Yahoo's `.info` is…, Raises ValueError if Yahoo has no data for this symbol (e.g. delisted, or the… (+1 more)

### Community 8 - "FinFlow Personal Wealth Hub"
Cohesion: 0.06
Nodes (39): API Integrations (Binance/LUNO/Kite/IBKR/ExchangeRate), Plugin System, Architecture Security (Fernet, read-only, JWT, HTTPS), Broker Holdings Backend (BrokerConnector, mStock+Zerodha), CONFIRM-BEFORE-LIVE broker caution, Decoupled Multi-Product Architecture, RSI/MACD/52-week Price Signals (Yahoo Finance feed), CURRENT_STATUS.md (Where We Are) (+31 more)

### Community 9 - "frontend/app/page.tsx"
Cohesion: 0.11
Nodes (23): Home(), AddAssetForm(), AddAssetFormProps, AssetFormData, assetSchema, TODO: Connect to actual API, Account, AccountForm() (+15 more)

### Community 10 - "🎨 Personal Wealth Hub - PREMIUM DESIGN MOCKUPS"
Cohesion: 0.05
Nodes (38): 1. Glassmorphism + Depth, 1. Loading States, 1. Net Worth Counter Animation, 1. Net Worth Line Chart (Sparkline), 2. Asset Allocation Donut Chart, 2. Card Hover Effect, 2. Micro-interactions, 2. Optimistic Updates (+30 more)

### Community 11 - "BasePlugin Interface"
Cohesion: 0.25
Nodes (9): BrokerConnector interface (brokers/base.py), mStock Connector, Zerodha Connector, pyotp, BasePlugin Interface, BinancePlugin, No-Code Custom API Builder, PlaidPlugin (Bank Aggregation) (+1 more)

### Community 12 - "🎨 Personal Wealth Hub - PREMIUM DESIGN MOCKUPS"
Cohesion: 0.05
Nodes (38): 1. Glassmorphism + Depth, 1. Loading States, 1. Net Worth Counter Animation, 1. Net Worth Line Chart (Sparkline), 2. Asset Allocation Donut Chart, 2. Card Hover Effect, 2. Micro-interactions, 2. Optimistic Updates (+30 more)

### Community 13 - "TypeScript Configuration"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 14 - "🎨 Personal Wealth Hub - PREMIUM DESIGN MOCKUPS"
Cohesion: 0.05
Nodes (38): 1. Glassmorphism + Depth, 1. Loading States, 1. Net Worth Counter Animation, 1. Net Worth Line Chart (Sparkline), 2. Asset Allocation Donut Chart, 2. Card Hover Effect, 2. Micro-interactions, 2. Optimistic Updates (+30 more)

### Community 15 - "Deployment and Architecture"
Cohesion: 0.29
Nodes (7): Financial Services Skills Guide, claude_skill() Integration in FastAPI Endpoints, Architecture Tech Stack, Local -> GitHub -> VPS Workflow, VPS + Docker Deployment, ARCHITECTURE.md (The How), FinFlow Tech Stack (FastAPI/PostgreSQL/Redis/React)

### Community 16 - "✅ Implementation Checklist - Personal Wealth Hub v2.0"
Cohesion: 0.06
Nodes (35): 1. Choose Deployment Platform, 2. Provide API Keys (Read-Only), 3. Confirm Feature Priority, 4. Set Up Infrastructure, APIs & Services, Backend, 🤖 COMPANION PRODUCT: ARUN TRADING BOT, 🎯 COMPETITIVE ADVANTAGES (+27 more)

### Community 17 - "Wealth Hub Features"
Cohesion: 0.33
Nodes (6): ARUN/Titan Trading Bot Read-Only Bridge, debt_payments Table, debts Table, Glassmorphism Premium Design System, manual_assets Table, Personal Wealth Hub v2.0 Architecture

### Community 18 - "🔌 CUSTOM API PLUGIN SYSTEM (Game Changer!)"
Cohesion: 0.06
Nodes (35): 1. Binance Plugin, 1. Manual Assets (Insurance, Property, Vehicles), 2. Debts & Liabilities (Loans, Credit Cards, Mortgages), 3. Debt Payment History, 4. Currency Rates (Real-Time Conversion), 5. User Preferences (Multi-Currency), 7. CROSS-PRODUCT COMPATIBILITY (Companion Apps), Architecture Overview (+27 more)

### Community 19 - "✅ Implementation Checklist - Personal Wealth Hub v2.0"
Cohesion: 0.06
Nodes (34): 1. Choose Deployment Platform, 2. Provide API Keys (Read-Only), 3. Confirm Feature Priority, 4. Set Up Infrastructure, APIs & Services, Backend, 🎯 COMPETITIVE ADVANTAGES, 💰 COST BREAKDOWN (+26 more)

### Community 20 - "Frontend Layout and Fonts"
Cohesion: 0.40
Nodes (3): inter, metadata, outfit

### Community 21 - "✅ Implementation Checklist - Personal Wealth Hub v2.0"
Cohesion: 0.06
Nodes (34): 1. Choose Deployment Platform, 2. Provide API Keys (Read-Only), 3. Confirm Feature Priority, 4. Set Up Infrastructure, APIs & Services, Backend, 🎯 COMPETITIVE ADVANTAGES, 💰 COST BREAKDOWN (+26 more)

### Community 22 - "🔌 CUSTOM API PLUGIN SYSTEM (Game Changer!)"
Cohesion: 0.06
Nodes (32): 1. Binance Plugin, 1. Manual Assets (Insurance, Property, Vehicles), 2. Debts & Liabilities (Loans, Credit Cards, Mortgages), 3. Debt Payment History, 4. Currency Rates (Real-Time Conversion), 5. User Preferences (Multi-Currency), Architecture Overview, Built-In Plugins (We Provide) (+24 more)

### Community 23 - "🔌 CUSTOM API PLUGIN SYSTEM (Game Changer!)"
Cohesion: 0.06
Nodes (32): 1. Binance Plugin, 1. Manual Assets (Insurance, Property, Vehicles), 2. Debts & Liabilities (Loans, Credit Cards, Mortgages), 3. Debt Payment History, 4. Currency Rates (Real-Time Conversion), 5. User Preferences (Multi-Currency), Architecture Overview, Built-In Plugins (We Provide) (+24 more)

### Community 28 - "📋 Finflow Documentation Analysis"
Cohesion: 0.07
Nodes (29): 1. **PROJECT.md** - The "What & Why", 2. **ARCHITECTURE.md** - The "How", 3. **CURRENT_STATUS.md** - The "Where We Are", 4. **DECISIONS.md** - Decision Log, 5. **BUG_LOG.md** - Bug Tracker, 6. **USER_GUIDE.md** - Documentation, 🎯 BOTTOM LINE, ⛔ DELETE THESE (Not Needed) (+21 more)

### Community 29 - "compilerOptions"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 32 - "Finflow/frontend/components/AddAssetForm.tsx"
Cohesion: 0.12
Nodes (13): AddAssetForm(), AddAssetFormProps, AssetFormData, assetSchema, TODO: Connect to actual API, GlassInput, GlassInputProps, GlassSelect (+5 more)

### Community 33 - "devDependencies"
Cohesion: 0.12
Nodes (17): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom (+9 more)

### Community 34 - "dependencies"
Cohesion: 0.13
Nodes (15): dependencies, class-variance-authority, framer-motion, @hookform/resolvers, react, react-dom, react-hook-form, zod (+7 more)

### Community 35 - "🏗️ TECHNICAL ARCHITECTURE"
Cohesion: 0.18
Nodes (11): API Integrations, Backend, Bank Aggregation (Premium), Broker APIs, Database Schema (Simplified), Deployment, Exchange Rate Provider, Frontend (+3 more)

### Community 36 - "🚀 Deployment Guide: VPS with Docker"
Cohesion: 0.22
Nodes (8): 🚀 Deployment Guide: VPS with Docker, 🔄 How to Update, 📋 Prerequisites, Step 1: Set Up Git (Local), Step 2: Set Up VPS (One-Time), Step 3: Configure Environment, Step 4: Run It! 🚀, 🔄 The Workflow

### Community 37 - "Finflow/frontend/package.json"
Cohesion: 0.22
Nodes (8): name, private, scripts, build, dev, lint, start, version

### Community 38 - "frontend/package.json"
Cohesion: 0.22
Nodes (8): name, private, scripts, build, dev, lint, start, version

### Community 39 - "🏦 Finflow - Personal Wealth Hub"
Cohesion: 0.25
Nodes (7): 🏦 Finflow - Personal Wealth Hub, Immediate Actions (This Week), 📞 LET'S BUILD!, 🎯 NEXT STEPS, 📋 TABLE OF CONTENTS, Week 1 Milestones, Week 2 Milestones

### Community 40 - "Uvicorn FastAPI Backend (port 8000)"
Cohesion: 0.29
Nodes (8): FinFlow Frontend (Next.js create-next-app), Geist Font (next/font), Vercel Platform Deployment, Swagger API Docs (/docs), FinFlow Quick Start Guide, Next.js Frontend Dev Server (port 3000), Uvicorn FastAPI Backend (port 8000), NEXT_PUBLIC_API_URL

### Community 41 - "FinFlow Current Status (Updated: Feb 7, 2026)"
Cohesion: 0.29
Nodes (6): 🚧 Blockers, ✅ Completed, 💡 Ecosystem Note, FinFlow Current Status (Updated: Feb 7, 2026), 🏗️ In Progress, ⏳ Next Up

### Community 42 - "backend/routers/holdings.py"
Cohesion: 0.29
Nodes (7): APP_ENCRYPTION_KEY, backend/routers/holdings.py, Broker Holdings Dashboard, backend/crypto_utils.py, backend/plain_flags.py, backend/tests/test_holdings.py, cryptography

### Community 43 - "FinFlow Platform"
Cohesion: 0.29
Nodes (7): Asset Tracking, Database create_all Import Bug, Family Management, FinFlow Platform, Auto-create Tables on Startup, FinFlow Verified Status Report, Windows-friendly Dependency Constraints

### Community 44 - "💎 CORE FEATURES"
Cohesion: 0.33
Nodes (6): 1. Asset Tracking, 2. Debt Management, 3. Multi-Currency System, 4. Custom API Plugin System 🚀, 5. Premium Design, 💎 CORE FEATURES

### Community 45 - "📊 CURRENT STATUS"
Cohesion: 0.33
Nodes (6): 🚧 Blockers, ✅ Completed, 📊 CURRENT STATUS, 🏗️ In Progress, ⏳ Next Up (Immediate), 💡 Open Questions

### Community 46 - "💰 COST BREAKDOWN"
Cohesion: 0.33
Nodes (6): Budget Option: Render, 💰 COST BREAKDOWN, Development, Monthly Running Costs, Premium Features (Optional), Recommended: Railway

### Community 47 - "📅 IMPLEMENTATION ROADMAP"
Cohesion: 0.33
Nodes (6): 📅 IMPLEMENTATION ROADMAP, Phase 1: MVP Core (Week 1-2), Phase 2: Stock Brokers (Week 3-4), Phase 3: Custom Plugins (Week 5-6), Phase 4: Premium Polish (Week 7-8), Phase 5: Multi-User (Week 9+)

### Community 48 - "Local Development Setup (No Docker)"
Cohesion: 0.40
Nodes (6): alembic, psycopg2-binary, Alembic Database Migrations, .env Configuration, Local Development Setup (No Docker), PostgreSQL 14+ Local/Cloud Database

### Community 49 - "backend (FastAPI container)"
Cohesion: 0.70
Nodes (5): backend (FastAPI container), db (postgres:16-alpine), FinFlow docker-compose, frontend (Next.js container), redis (redis:7-alpine)

### Community 50 - "🔍 KEY DIFFERENTIATORS"
Cohesion: 0.40
Nodes (5): 🔍 KEY DIFFERENTIATORS, 🚀 UNIQUE ADVANTAGE, vs Kubera, vs Public.com, vs Wealthica

### Community 51 - "🎯 PROJECT OVERVIEW"
Cohesion: 0.40
Nodes (5): Mission, 🎯 PROJECT OVERVIEW, Success Criteria, Target Users, The Problem We're Solving

### Community 52 - "Finflow/frontend/app/layout.tsx"
Cohesion: 0.40
Nodes (3): inter, metadata, outfit

### Community 53 - "frontend/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 54 - "gen_status.py"
Cohesion: 0.83
Nodes (3): git(), main(), md_to_html()

### Community 59 - "holdingsFormat.ts"
Cohesion: 0.07
Nodes (53): fetchCash(), fetchHoldings(), getToken(), PortfolioPage(), Tab, TABS, LoginModal(), Props (+45 more)

### Community 67 - "test_backtest_trend.py"
Cohesion: 0.10
Nodes (38): DataFrame, Offline tests for backend/tools/backtest_trend.py. No network — builds a…, A persistent downtrend sits below its own 200 DMA almost the whole way down —…, ADX has no live counterpart to cross-check against — it's backtest-only (see…, No live pricing.py function to cross-check against, so pin the ADX series…, Every graded row's hit_Nd must only be set when the future bar actually exists…, Regression: numpy.bool_ (vs. Python bool) in an object-dtype DataFrame column…, Guards the exact groupby(...).mean() bug found in live testing: build many rows… (+30 more)

### Community 72 - "test_trend_snapshot.py"
Cohesion: 0.16
Nodes (26): grade_pending_snapshots(), Session, Trend-accuracy tracking: record each trend call for every held stock, then…, Build (and add, uncommitted) one TrendSnapshot row from already-computed…, Insert one TrendSnapshot per Holding using today's signals. Returns the count…, For every snapshot with a due, ungraded window, fetch the current price and…, record_snapshot(), snapshot_all_holdings() (+18 more)

### Community 73 - "backend/routers/auth.py"
Cohesion: 0.16
Nodes (19): create_access_token(), get_password_hash(), timedelta, verify_password(), User, get_current_user(), login(), BaseModel (+11 more)

### Community 74 - "test_holdings.py"
Cohesion: 0.13
Nodes (17): classify_trend(), compute_macd_hist(), compute_rsi(), Series, Returns {"label": str, "strength": 1|2, "direction": "up"|"down"|"flat"}. Fixed…, Offline tests for the broker-holdings feature — no real broker credentials or…, test_below_cost_flag(), test_classify_trend_handles_missing_data() (+9 more)

### Community 75 - "backend/models.py"
Cohesion: 0.18
Nodes (15): Debt, Holding, ManualAsset, Base, A single broker-synced stock position, one row per (plugin, symbol). Read-only…, UserPlugin, UserPreferences, AssetCreate (+7 more)

### Community 76 - "_FakeClient"
Cohesion: 0.15
Nodes (6): _FakeClient, _FakeResponse, Stands in for httpx.Client — records calls, returns queued fake responses., test_mstock_fetch_holdings_parses_and_filters_zero_qty(), test_zerodha_fetch_holdings_parses_with_valid_session(), Exception

### Community 77 - "BrokerConnectionError"
Cohesion: 0.27
Nodes (5): BrokerConnectionError, Raised for anything that stops a sync: expired session, bad credentials,…, session_state is UserPlugin.config — where the daily access_token lives. Pass…, Call this once, right after the person's browser redirects back with…, ZerodhaConnector

### Community 78 - "plain_flags.py"
Cohesion: 0.33
Nodes (9): build_flags(), holding_period_flag(), PlainFlag, price_position_flag(), Plain-language, rule-based flags for the dashboard's "What to know" chip —…, test_long_term_flag_over_one_year(), test_near_high_flag(), test_short_term_flag_under_one_year() (+1 more)

### Community 79 - "news.py"
Cohesion: 0.31
Nodes (8): _fetch_one(), list_news(), _pub(), get, Session, User, Company news per holding, ported from Deepaks-Bots/news.py (Google News RSS).…, _sentiment()

### Community 80 - "Key Integration Details"
Cohesion: 0.29
Nodes (6): Authentication Flow (Type A), Fetching Holdings (Type B), Important Quirks, Key Integration Details, mStock API Reference, Useful Links

## Knowledge Gaps
- **513 isolated node(s):** `inter`, `outfit`, `metadata`, `assetSchema`, `AssetFormData` (+508 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ZerodhaConnector` connect `BrokerConnectionError` to `RawHolding`, `test_holdings.py`, `_FakeClient`, `holdings.py`?**
  _High betweenness centrality (0.007) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `BrokerConnectionError` (e.g. with `MStockConnector` and `ZerodhaConnector`) actually correct?**
  _`BrokerConnectionError` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `ZerodhaConnector` (e.g. with `BrokerConnectionError` and `BrokerConnector`) actually correct?**
  _`ZerodhaConnector` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `inter`, `outfit`, `metadata` to the rest of the system?**
  _513 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Finflow/backend/routers/auth.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06352087114337568 - nodes in this community are weakly interconnected._
- **Should `devDependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._
- **Should `dependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._