# Graph Report - FinFlow  (2026-09-10)

## Corpus Check
- 93 files · ~59,160 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1037 nodes · 1298 edges · 72 communities (54 shown, 18 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 57 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c3c8cd51`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Finflow/backend/routers/auth.py
- test_holdings.py
- Python requirements.txt
- backend/routers/auth.py
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
- framer-motion
- lucide-react
- next
- tailwind-merge
- Finflow/frontend/postcss.config.mjs
- PROJECT.md
- clsx
- framer-motion
- next
- recharts
- tailwind-merge

## God Nodes (most connected - your core abstractions)
1. `ZerodhaConnector` - 17 edges
2. `Python requirements.txt` - 17 edges
3. `compilerOptions` - 16 edges
4. `BrokerConnectionError` - 16 edges
5. `compilerOptions` - 16 edges
6. `RawHolding` - 13 edges
7. `_FakeClient` - 12 edges
8. `📋 Finflow Documentation Analysis` - 12 edges
9. `✅ Implementation Checklist - Personal Wealth Hub v2.0` - 12 edges
10. `MStockConnector` - 11 edges

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

## Communities (72 total, 18 thin omitted)

### Community 0 - "Finflow/backend/routers/auth.py"
Cohesion: 0.07
Nodes (43): CurrencyService, create_access_token(), get_password_hash(), timedelta, verify_password(), CurrencyService, get_db(), init_db() (+35 more)

### Community 1 - "test_holdings.py"
Cohesion: 0.06
Nodes (35): ABC, BrokerConnectionError, BrokerConnector, Shared contract every broker connector implements. This is the "no-code plugin"…, What a broker connector hands back for one stock position, before any…, Raised for anything that stops a sync: expired session, bad credentials,…, One instance = one broker ACCOUNT (not one broker). Two Zerodha logins are two…, Make sure we have a valid, non-expired session token, refreshing it if the… (+27 more)

### Community 2 - "Python requirements.txt"
Cohesion: 0.18
Nodes (14): JWT Authentication, backend/pricing.py, RSI/MACD/52-week Range Signals, fastapi, httpx, pandas, passlib[bcrypt], pydantic (+6 more)

### Community 3 - "backend/routers/auth.py"
Cohesion: 0.08
Nodes (42): create_access_token(), get_password_hash(), timedelta, verify_password(), get_db(), init_db(), on_startup(), get (+34 more)

### Community 4 - "devDependencies"
Cohesion: 0.12
Nodes (17): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom (+9 more)

### Community 5 - "dependencies"
Cohesion: 0.13
Nodes (15): dependencies, class-variance-authority, @hookform/resolvers, lucide-react, react, react-dom, react-hook-form, zod (+7 more)

### Community 6 - "holdings.py"
Cohesion: 0.11
Nodes (37): decrypt_credentials(), encrypt_credentials(), _get_fernet(), Encrypts/decrypts broker credentials (API keys, TOTP secrets) before they touch…, dict -> encrypted string, safe to store in a JSON/String column., encrypted string -> dict. Raises cryptography.fernet.InvalidToken if the key is…, classify_trend(), Returns {"label": str, "strength": 1|2, "direction": "up"|"down"|"flat"}. Fixed… (+29 more)

### Community 7 - "pricing.py"
Cohesion: 0.15
Nodes (19): _cap_tier(), CompanyMeta, compute_macd_hist(), compute_rsi(), compute_signals(), fetch_company_meta(), fetch_daily_history(), PriceSignals (+11 more)

### Community 8 - "FinFlow Personal Wealth Hub"
Cohesion: 0.06
Nodes (39): API Integrations (Binance/LUNO/Kite/IBKR/ExchangeRate), Plugin System, Architecture Security (Fernet, read-only, JWT, HTTPS), Broker Holdings Backend (BrokerConnector, mStock+Zerodha), CONFIRM-BEFORE-LIVE broker caution, Decoupled Multi-Product Architecture, RSI/MACD/52-week Price Signals (Yahoo Finance feed), CURRENT_STATUS.md (Where We Are) (+31 more)

### Community 9 - "frontend/app/page.tsx"
Cohesion: 0.05
Nodes (37): AddAssetForm(), AddAssetFormProps, AssetFormData, assetSchema, TODO: Connect to actual API, Account, AccountForm(), api() (+29 more)

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
Nodes (15): dependencies, class-variance-authority, @hookform/resolvers, react, react-dom, react-hook-form, recharts, zod (+7 more)

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

## Knowledge Gaps
- **497 isolated node(s):** `inter`, `outfit`, `metadata`, `assetSchema`, `AssetFormData` (+492 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CurrencyService` connect `Finflow/backend/routers/auth.py` to `backend/routers/auth.py`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Why does `ZerodhaConnector` connect `test_holdings.py` to `holdings.py`?**
  _High betweenness centrality (0.005) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `ZerodhaConnector` (e.g. with `BrokerConnectionError` and `BrokerConnector`) actually correct?**
  _`ZerodhaConnector` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `BrokerConnectionError` (e.g. with `MStockConnector` and `ZerodhaConnector`) actually correct?**
  _`BrokerConnectionError` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `inter`, `outfit`, `metadata` to the rest of the system?**
  _497 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Finflow/backend/routers/auth.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06516290726817042 - nodes in this community are weakly interconnected._
- **Should `test_holdings.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06187202538339503 - nodes in this community are weakly interconnected._