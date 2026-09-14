# Graph Report - .  (2026-09-10)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 402 nodes · 606 edges · 23 communities (18 shown, 5 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 54 edges (avg confidence: 0.75)
- Token cost: 1,181 input · 228 output

## Graph Freshness
- Built from commit: `c3c8cd51`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Dashboard Rule Flags
- Broker Connector Interface
- Docker and Infrastructure
- Backend Core Services
- Frontend Development Dependencies
- Frontend UI Dependencies
- Security and Data Models
- Technical Analysis Signals
- Project Documentation and Roadmap
- Frontend Asset Management
- Plugin and Integration System
- TypeScript Configuration
- Deployment and Architecture
- Wealth Hub Features
- Frontend Layout and Fonts
- ESLint Configuration
- Next.js Configuration
- PostCSS Configuration
- App Event Handlers
- Database Base Model

## God Nodes (most connected - your core abstractions)
1. `ZerodhaConnector` - 17 edges
2. `Python requirements.txt` - 17 edges
3. `compilerOptions` - 16 edges
4. `BrokerConnectionError` - 16 edges
5. `User` - 16 edges
6. `RawHolding` - 13 edges
7. `_FakeClient` - 12 edges
8. `MStockConnector` - 11 edges
9. `BrokerConnector` - 10 edges
10. `_get_owned_plugin()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `Multi-Currency First UI (always-visible switcher)` --semantically_similar_to--> `Multi-Currency System (MYR/INR/USD/SGD)`  [INFERRED] [semantically similar]
  PREMIUM_DESIGN_MOCKUPS.md → FINFLOW_PROJECT_BRIEF.md
- `Plugin System` --semantically_similar_to--> `Custom API Plugin System`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → WEALTH_HUB_V2_ENHANCED.md
- `Glassmorphism + Depth Design` --semantically_similar_to--> `Premium Glassmorphism Design`  [INFERRED] [semantically similar]
  PREMIUM_DESIGN_MOCKUPS.md → FINFLOW_PROJECT_BRIEF.md
- `Architecture Tech Stack` --semantically_similar_to--> `FinFlow Tech Stack (FastAPI/PostgreSQL/Redis/React)`  [INFERRED] [semantically similar]
  ARCHITECTURE.md → FINFLOW_PROJECT_BRIEF.md
- `Architecture Security (Fernet, read-only, JWT, HTTPS)` --semantically_similar_to--> `Security Model (read-only keys, Fernet, JWT)`  [INFERRED] [semantically similar]
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

## Communities (23 total, 5 thin omitted)

### Community 0 - "Dashboard Rule Flags"
Cohesion: 0.39
Nodes (8): build_flags(), holding_period_flag(), PlainFlag, price_position_flag(), Plain-language, rule-based flags for the dashboard's "What to know" chip —…, test_long_term_flag_over_one_year(), test_short_term_flag_under_one_year(), date

### Community 1 - "Broker Connector Interface"
Cohesion: 0.07
Nodes (27): ABC, BrokerConnectionError, BrokerConnector, Shared contract every broker connector implements. This is the "no-code plugin"…, What a broker connector hands back for one stock position, before any…, Raised for anything that stops a sync: expired session, bad credentials,…, One instance = one broker ACCOUNT (not one broker). Two Zerodha logins are two…, Make sure we have a valid, non-expired session token, refreshing it if the… (+19 more)

### Community 2 - "Docker and Infrastructure"
Cohesion: 0.06
Nodes (47): backend (FastAPI container), db (postgres:16-alpine), FinFlow docker-compose, frontend (Next.js container), redis (redis:7-alpine), FinFlow Frontend (Next.js create-next-app), Geist Font (next/font), Vercel Platform Deployment (+39 more)

### Community 3 - "Backend Core Services"
Cohesion: 0.07
Nodes (36): create_access_token(), get_password_hash(), timedelta, verify_password(), CurrencyService, get_db(), on_startup(), get (+28 more)

### Community 4 - "Frontend Development Dependencies"
Cohesion: 0.08
Nodes (25): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom (+17 more)

### Community 5 - "Frontend UI Dependencies"
Cohesion: 0.08
Nodes (25): dependencies, class-variance-authority, clsx, framer-motion, @hookform/resolvers, lucide-react, next, react (+17 more)

### Community 6 - "Security and Data Models"
Cohesion: 0.13
Nodes (34): decrypt_credentials(), encrypt_credentials(), _get_fernet(), Encrypts/decrypts broker credentials (API keys, TOTP secrets) before they touch…, dict -> encrypted string, safe to store in a JSON/String column., encrypted string -> dict. Raises cryptography.fernet.InvalidToken if the key is…, Debt, Holding (+26 more)

### Community 7 - "Technical Analysis Signals"
Cohesion: 0.12
Nodes (20): classify_trend(), compute_macd_hist(), compute_rsi(), compute_signals(), fetch_daily_history(), PriceSignals, Free public price data + simple technical signals — deliberately NOT pulled…, Raises ValueError if Yahoo has no data for this symbol (e.g. delisted, or the… (+12 more)

### Community 8 - "Project Documentation and Roadmap"
Cohesion: 0.07
Nodes (33): API Integrations (Binance/LUNO/Kite/IBKR/ExchangeRate), Architecture Security (Fernet, read-only, JWT, HTTPS), Broker Holdings Backend (BrokerConnector, mStock+Zerodha), CONFIRM-BEFORE-LIVE broker caution, Decoupled Multi-Product Architecture, RSI/MACD/52-week Price Signals (Yahoo Finance feed), CURRENT_STATUS.md (Where We Are), Minimal Documentation Principle (3 essential docs) (+25 more)

### Community 9 - "Frontend Asset Management"
Cohesion: 0.09
Nodes (21): AddAssetForm(), AddAssetFormProps, AssetFormData, assetSchema, TODO: Connect to actual API, Account, AccountForm(), api() (+13 more)

### Community 11 - "Plugin and Integration System"
Cohesion: 0.14
Nodes (15): Plugin System, Competitive Advantages vs Kubera/Wealthica, FinFlow Database Schema, BrokerConnector interface (brokers/base.py), mStock Connector, Zerodha Connector, pyotp, BasePlugin Interface (+7 more)

### Community 13 - "TypeScript Configuration"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 15 - "Deployment and Architecture"
Cohesion: 0.29
Nodes (7): Financial Services Skills Guide, claude_skill() Integration in FastAPI Endpoints, Architecture Tech Stack, Local -> GitHub -> VPS Workflow, VPS + Docker Deployment, ARCHITECTURE.md (The How), FinFlow Tech Stack (FastAPI/PostgreSQL/Redis/React)

### Community 17 - "Wealth Hub Features"
Cohesion: 0.33
Nodes (6): ARUN/Titan Trading Bot Read-Only Bridge, debt_payments Table, debts Table, Glassmorphism Premium Design System, manual_assets Table, Personal Wealth Hub v2.0 Architecture

### Community 20 - "Frontend Layout and Fonts"
Cohesion: 0.40
Nodes (3): inter, metadata, outfit

## Knowledge Gaps
- **106 isolated node(s):** `inter`, `outfit`, `metadata`, `assetSchema`, `AssetFormData` (+101 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `ZerodhaConnector` connect `Broker Connector Interface` to `Security and Data Models`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `FinFlow Personal Wealth Hub` connect `Project Documentation and Roadmap` to `Plugin and Integration System`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Why does `Custom API Plugin System` connect `Plugin and Integration System` to `Project Documentation and Roadmap`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `ZerodhaConnector` (e.g. with `BrokerConnectionError` and `BrokerConnector`) actually correct?**
  _`ZerodhaConnector` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `BrokerConnectionError` (e.g. with `MStockConnector` and `ZerodhaConnector`) actually correct?**
  _`BrokerConnectionError` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `inter`, `outfit`, `metadata` to the rest of the system?**
  _106 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Broker Connector Interface` be split into smaller, more focused modules?**
  _Cohesion score 0.07239819004524888 - nodes in this community are weakly interconnected._