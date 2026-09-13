# FinFlow Current Status (Updated: Sep 13, 2026)

## 🌐 LIVE ON VPS
Deployed and QA-verified on Hostinger VPS `76.13.179.32` (shared box, also runs Kyro/dealzoda/smartnri — used non-conflicting ports):
- **App (what Dad opens)**: `http://76.13.179.32:3001`
- **API** (not for Dad, used by the app itself): `http://76.13.179.32:8001`
- No domain yet, so **no HTTPS** — login password travels unencrypted over the network. Fine for a first look; get a domain + Caddy/nginx reverse proxy with Let's Encrypt before relying on this day to day, especially since mStock broker credentials pass through it.
- Secrets (`SECRET_KEY`, `APP_ENCRYPTION_KEY`, DB password) live only in `/opt/FinFlow/.env` on the VPS — not committed to git, not in this repo.
- Postgres and Redis are container-internal only (no public port) — fixed during this deploy, they were originally exposed to the whole internet with no password.

### Bugs fixed during deployment (would have blocked Dad from ever logging in)
1. `docker-compose.yml` bind-mounted the frontend source over the built container image, hiding `node_modules`/`.next` — container crash-looped on every restart.
2. `bcrypt` 4.1+ broke `passlib`'s internal self-test, so `/auth/register` 500'd on every signup. Pinned `bcrypt==4.0.1` in `requirements.txt`.
3. `NEXT_PUBLIC_API_URL` wasn't passed as a Docker build arg, so the browser bundle would have pointed at `localhost:8000` instead of the real backend.

## ✅ Completed
- **Architecture**: Decoupled multi-product architecture finalized.
- **Backend**: FastAPI structure with Auth, Assets, and Family modules.
- **Database**: PostgreSQL schema for manual entries and portfolio aggregation. SQLite used automatically for local dev.
- **Multi-Currency**: Basic FX service working for conversion and formatting.
- **Broker holdings backend (mStock + Zerodha)**: `BrokerConnector` interface, both connectors, `Holding`/`UserPlugin` models, credential encryption, RSI/MACD/52-week price signals (free Yahoo Finance feed), plain-language tax/price flags, and `/holdings/*` API endpoints. 21 offline tests passing (`pytest backend/tests/ -v`).
- **Holdings dashboard frontend (NEW — Sep 10)**: `Portfolio` modal with two tabs.
  - **Summary tab**: KPI tiles (current value, invested, returns, growth %), Investment-by-Sector pie, Investment-by-Capitalisation donut, Top-5-by-Investment, Invested-vs-Returns, Top-5-by-Returns, plus a Large/Mid/Small/Penny filter. Built with recharts.
  - **Holdings tab**: one row per position — owner, broker badge, ticker + company name, days held, buy/current price, 52-week range bar, gain/loss, RSI + plain gloss, MACD + plain gloss, trend label, rule-based flags.
- **Purchase date / days-held (NEW)**: brokers don't send it, so each row has an inline date picker. Setting it activates the days-held count and the long-term-tax flag. New `PATCH /holdings/positions/{id}` endpoint; new `first_buy_date` handling.
- **Company enrichment (NEW)**: each sync now also pulls company name, sector and market-cap tier from Yahoo (best-effort — nulls tolerated). New `company_name` / `sector` / `cap_tier` columns on `Holding`.
- **Login screen (NEW)**: glass modal ported from `C:\Antigravity\Fortress`, adapted to FinFlow's FastAPI JWT (token in `localStorage`). Sign in / create account, wired to `/auth/register` + `/auth/login`. `Sign in` / `Sign out` in the nav; protected views prompt login.
- **`.env` loading (fix)**: `backend/main.py` now calls `load_dotenv()` on startup — the app previously never read `.env`, so `APP_ENCRYPTION_KEY` was invisible to `uvicorn`.
- **mStock Connector verification**: the mStock integration now correctly uses `Authorization: Bearer <jwtToken>` and `X-PrivateKey` headers based on Type B Portfolio API requirements.
- **Holdings dashboard frontend (UPDATED)**: `Portfolio` modal updated for senior-citizen accessibility with full-screen width, large font sizes, and high-contrast glassmorphism colors.

## 🏗️ In Progress
- **UI Design**: premium "Glassmorphism" design system rollout.
- **Manual Forms**: Asset entry forms for Insurance and Loans.

## ⏳ Next Up
1. **Latest company news**: section on the holdings screen — needs a news feed + a backend endpoint (not built).
2. Decide storage: local SQLite is fine for now; move to Postgres on the VPS before multi-device or historical tracking (there is no price history table yet — only the latest snapshot per holding).
3. Commit the untracked broker + holdings + login files.
4. **Portfolio Connectors**: read-only API integration for Binance and Luno.
5. **Family Roll-up**: combined net-worth views for family accounts.

## 🚧 Blockers
- **Zerodha credentials**: backend + frontend built and tested with mock data, but nothing has touched a real Zerodha account yet.
- **API Keys**: need personal read-only keys for Binance/Luno real-data testing.

## 💡 Ecosystem Note
The **ARUN Trading Bot** is now a separate standalone project. FinFlow will eventually integrate with it via a read-only database connection to show "Bot Managed" assets in the total net worth view.

### Recent Updates (Sep 13, 2026)
- **UI/UX Refinements**: Enlarged fonts across the Summary panel and made the UI more senior-citizen friendly. Simplified owner name displays (e.g. converting emails to first names).
- **mStock Integration**: Added fetching for Cash Balance from the Type A /fundsummary endpoint and displayed it as a top-level KPI on the Dashboard.
- **Holdings Improvements**: Corrected purchase date assignment.
