# 🏦 FinFlow — Open-source Family Wealth Sharing Platform

> **A high-frequency, multi-currency personal wealth tracker designed for global portfolios.** Aggregate every asset, liability, and currency in an ultra-modern glassmorphic interface — built for families to track assets, manage insurance, and coordinate lending.

[![Next.js](https://img.shields.io/badge/Next.js-16.1.6-black?style=flat&logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.2-blue?style=flat&logo=react)](https://react.dev/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-v4-38bdf8?style=flat&logo=tailwindcss)](https://tailwindcss.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker)](https://www.docker.com/)

**🌐 Live**: `https://finflow.fortressintelligence.space` — deployed, HTTPS, security-audited. See [CURRENT_STATUS.md](CURRENT_STATUS.md) for full deployment notes.

---

## ✨ Key Features

**Live:**
- 🔐 Authentication (register, login, JWT tokens, server-side password strength + login lockout)
- 💰 Asset tracking (add/view family assets)
- 👨‍👩‍👧 Family management (invitations, shared access)
- 📊 Premium glassmorphism dashboard UI (Next.js 19 + Tailwind), redesigned for senior-citizen readability (full-screen, large fonts, high contrast)
- 📈 Broker holdings dashboard — mStock + Zerodha (2 accounts) connectors, read-only, with RSI/MACD/52-week-range signals, cash balance KPI, auto-reconciled purchase dates via FIFO trade-history matching
- 🗂️ **Market Board tab** — watchlist with RSI/MACD trend verdicts, price-sensitive news feed, add/remove stocks, CSV/XLSX export
- ☀️ / 🌙 **Dual Theme Engine (Light & Dark Mode)**: instant toggle in the floating glass nav bar, zero-flicker pre-hydration script, persistent `localStorage` preference
- 🔍 **Enhanced Readability Typography**: scaled typography (+15–20% boost) across all components for superior legibility
- 🌐 **Multi-Currency**: real-time conversion across USD, MYR, INR, and SGD with smart regional formatting
- 🐳 **Production Docker & VPS Ready**: multi-stage Next.js standalone container, FastAPI backend, PostgreSQL, and Redis, all managed via Docker Compose

**In Development:**
- Broker connectors (Binance, Luno)
- Insurance forms & templates
- Loan request workflows

---

## 🛠️ Architecture & Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | Next.js 16 (App Router & Turbopack), React 19, TypeScript, Tailwind CSS v4, Framer Motion, Lucide Icons, Recharts |
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy, Uvicorn |
| **Database & Cache** | PostgreSQL 15/16, Redis 7 |
| **Deployment** | Docker, Docker Compose, Linux VPS (Ubuntu / Debian / Hostinger / AWS / Linode) |

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- **Node.js**: v20+ (v22 recommended)
- **Python**: 3.11+
- **PostgreSQL 14+** (or use the auto-created SQLite dev database)

### Backend Setup

1. **Create and activate a Python environment**:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Create `.env` file**:
   ```bash
   cp .env.example .env
   ```

3. **Run backend** (API listens on `http://localhost:8000`):
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

4. **Test API** (interactive docs): open `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## ☁️ VPS Deployment Guide

Deploying FinFlow to your VPS takes less than 2 minutes using Docker:

### 1. On your VPS:
```bash
git clone https://github.com/BratAIExplorer/Finflow.git /opt/Finflow
cd /opt/Finflow

cp .env.example .env
nano .env

chmod +x deploy.sh
./deploy.sh
```

### 2. Updating on VPS
Whenever you push updates to GitHub, simply run:
```bash
cd /opt/Finflow
./deploy.sh
```
The script pulls the latest code, builds the standalone images, and restarts services with zero orphaned containers.

See [DEPLOYMENT.md](DEPLOYMENT.md) for the full server setup walkthrough.

---

## 📁 Repository Structure

```
Finflow/
├── backend/                  # FastAPI Python backend
│   ├── main.py               # App entry point
│   ├── database.py           # SQLAlchemy setup
│   ├── models.py             # Database schemas
│   ├── currency.py           # Multi-currency FX converter
│   ├── crypto_utils.py       # Encrypts broker credentials at rest
│   ├── pricing.py            # Price feed + RSI/MACD/52-week signals
│   ├── plain_flags.py        # Plain-language tax/price flags
│   ├── board/                # Market Board (watchlist, news, export)
│   ├── brokers/
│   │   ├── base.py           # BrokerConnector interface
│   │   ├── mstock.py         # mStock connector (TOTP-automatable)
│   │   └── zerodha.py        # Zerodha connector (daily one-click login)
│   ├── tests/                # Offline tests — no real credentials/network needed
│   └── routers/
│       ├── auth.py           # Authentication endpoints
│       ├── assets.py         # Asset CRUD
│       ├── family.py         # Family invites/sharing
│       ├── holdings.py       # Broker account + holdings endpoints
│       └── board.py          # Market Board endpoints
│
├── frontend/                 # Next.js 16 dashboard
│   ├── app/
│   │   ├── globals.css       # Light/Dark tokens & Glassmorphism styles
│   │   ├── layout.tsx        # Pre-hydration theme loader
│   │   └── page.tsx          # Landing page with ThemeToggle
│   ├── components/
│   │   ├── ThemeToggle.tsx   # Light/Dark switch button
│   │   ├── AddAssetForm.tsx  # Manual asset intake modal
│   │   ├── portfolio/        # Portfolio tabs incl. MarketBoardPanel
│   │   └── ui/                # Reusable glass UI components
│   ├── lib/
│   │   └── utils.ts          # Classnames utility (clsx + twMerge)
│   └── Dockerfile            # Multi-stage standalone Next.js build
│
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Production Docker orchestration
├── deploy.sh                 # VPS one-click deployment script
├── .env.example              # Environment variables template
└── DEPLOYMENT.md             # In-depth server deployment documentation
```

---

## Environment Variables

Copy `.env.example` → `.env` and fill in your values (see the file for the full list, including `APP_ENCRYPTION_KEY` for broker credential encryption).

---

## API Endpoints (Testing)

Once backend is running, visit `http://localhost:8000/docs`:

**Auth:** `POST /auth/register`, `POST /auth/login`

**Assets:** `GET /assets`, `POST /assets`, `DELETE /assets/{id}`

**Family:** `POST /family/invite`, `GET /family/members`

**Broker holdings (mStock / Zerodha):**
- `POST /holdings/accounts` — Connect a broker account
- `GET /holdings/accounts` — List connected broker accounts and last sync status
- `POST /holdings/accounts/{plugin_id}/sync` — mStock: fully automatic (TOTP-based). Zerodha: needs a fresh daily session
- `GET /holdings/` — Combined holdings with gain/loss, 52-week range, RSI/MACD, trend label, tax/price flags

**Market Board:**
- `GET /board/` — Cached watchlist snapshot (instant tab switching)
- `POST /board/refresh`, `POST /board/add`, `POST /board/remove`

Offline test suite: `pytest backend/tests/ -v` (no real credentials or network needed — mocked HTTP).

---

## Docker (Production Deployment)

For local Docker testing:
```bash
docker-compose up --build
```

Then:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

---

## Architecture Notes

- **Backend**: FastAPI + SQLAlchemy (PostgreSQL)
- **Frontend**: Next.js 16 + React 19 + Tailwind CSS v4
- **Auth**: JWT tokens, bcrypt hashing
- **Caching**: Redis (optional, configured in docker-compose)
- **Broker APIs**: mStock, Zerodha (holdings, read-only, backend done); Binance, Luno (future)

---

## 📄 License
Private & Proprietary • FinFlow 2026
