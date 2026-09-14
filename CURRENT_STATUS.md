# FinFlow Current Status (Updated: Sep 14, 2026)

## 📈 Trend accuracy tracking (NEW) — Sep 14, 2026
Dad decides buy/sell based on the Bullish/Bearish trend label, but until now
only the *latest* label was ever stored — no way to check if a past call was
right. Added:
- **`trend_snapshots` table** (`backend/models.py`): one row per holding per
  day — label, RSI/MACD, price at capture, and hit/miss outcome columns for
  1-day, 7-day, and 30-day windows (null = still pending).
- **`backend/jobs/trend_snapshot.py`**: `snapshot_all_holdings()` records
  today's call for every held stock (reuses the existing
  `pricing.compute_signals`/`classify_trend` — no new price logic);
  `grade_pending_snapshots()` checks due windows against the current price
  and marks hit/miss by direction only (Bullish = hit if price rose,
  Bearish = hit if it fell; Neutral is never graded).
- **Scheduled via in-process APScheduler** (`backend/main.py`, started in the
  existing `on_startup` hook), daily at 16:00 IST — chosen over VPS crontab
  since it ships inside the container automatically, no host-side setup
  needed on the shared Hostinger box.
- **New endpoint**: `GET /holdings/{id}/trend-history` — same ownership
  check as `PATCH /holdings/positions/{id}`, returns the stored snapshots.
- Not built yet (deliberately, per the plan): no frontend accuracy widget —
  needs a few weeks of real data first — and no change to the trend
  labeling rules themselves.
- Tests: `backend/tests/test_trend_snapshot.py` (6 tests, offline/mocked).
  Full suite: 25/26 passing (`test_mstock_fetch_holdings_parses_and_filters_zero_qty`
  fails, pre-existing and unrelated — see the mStock 502 issue already noted
  from the prior session, not touched here).

## 📄 Portfolio: modal → full page, + News tab — Sep 14, 2026
Portfolio was a fullscreen overlay modal opened from the nav (`HoldingsDashboard.tsx`).
Replaced with a real route:
- **`frontend/app/portfolio/page.tsx`** — a proper Next.js page at `/portfolio`
  with Summary / Holdings / News tabs. Redirects to `/` if not logged in.
  `HoldingsDashboard.tsx` (the old modal) deleted — nothing else referenced it.
- **News tab**: per-holding headlines via Google News RSS, ported from
  `C:\Antigravity\Deepaks-Bots\news.py` (material-news keyword tagging +
  pos/neg/neutral sentiment). New backend route `backend/routers/news.py`
  (`GET /news/`), registered in `main.py`. Added `feedparser` to
  `requirements.txt`. Unlike the bot's poller, this is a stateless GET —
  no `seen.sqlite` dedup, it just returns current top headlines per holding
  on every call.
- Verified: TS typecheck clean, backend router imports clean, unauthenticated
  `/portfolio` redirects to `/`, authenticated page renders all 3 tabs, and
  the news fetch was confirmed live against the real portfolio's 16 holdings
  (Google News RSS returned real headlines).

## 🧓 Senior-friendly Holdings redesign — Sep 14, 2026
The Holdings tab was a data table pinned to `min-w-[1400px]` — 11 columns,
guaranteed horizontal scroll on any laptop, small low-contrast secondary
text. Replaced with a compact expandable row list per stock:
- **Always visible**: stock, broker, owner, shares, buy price, current
  price, gain/loss — no sideways scrolling, no matter how many stocks.
- **Tap a row** to reveal RSI, MACD, trend, 52-week range, and flags —
  detail is one tap away instead of a mandatory extra 6 columns.
- Held-duration shows a plain day count (`held 1187 days`) — simplified
  from an earlier `Xy Yd` / `X years Y months` attempt per user feedback
  ("just number of days held").
- Validated against a 20+ multi-broker mock portfolio scenario before
  building — a full-card-per-stock layout was considered and rejected
  because it doesn't scan quickly at that volume; the tap-to-expand row
  keeps scanning fast while eliminating horizontal scroll entirely.
- Fixed a real `.gitignore` bug found in the process: a bare `lib/` rule
  (meant for Python venvs) was silently excluding `frontend/lib/` — real
  TypeScript source that had never once been committed to git.

## 🌐 LIVE ON VPS
Deployed and QA-verified on Hostinger VPS `76.13.179.32` (shared box, also runs Kyro/dealzoda/smartnri — used non-conflicting ports):
- **App (what Dad opens)**: `https://finflow.fortressintelligence.space` — real HTTPS, free Let's Encrypt cert via certbot, auto-renews. DNS: A record `finflow` → `76.13.179.32` on the `fortressintelligence.space` Namecheap zone (added 2026-09-13).
- Old bare-IP links (`http://76.13.179.32:3001` / `:8001`) still work directly but skip HTTPS — use the domain instead.
- nginx reverse-proxies `/` → frontend container (3001) and `/api/` → backend container (8001), both container-internal now; only 80/443 are meant to be used externally.
- Secrets (`SECRET_KEY`, `APP_ENCRYPTION_KEY`, DB password) live only in `/opt/FinFlow/.env` on the VPS — not committed to git, not in this repo.
- Postgres and Redis are container-internal only (no public port) — fixed during this deploy, they were originally exposed to the whole internet with no password.

### Bugs fixed during deployment (would have blocked Dad from ever logging in)
1. `docker-compose.yml` bind-mounted the frontend source over the built container image, hiding `node_modules`/`.next` — container crash-looped on every restart.
2. `bcrypt` 4.1+ broke `passlib`'s internal self-test, so `/auth/register` 500'd on every signup. Pinned `bcrypt==4.0.1` in `requirements.txt`.
3. `NEXT_PUBLIC_API_URL` wasn't passed as a Docker build arg, so the browser bundle would have pointed at `localhost:8000` instead of the real backend.

## 🔒 Security Audit — Sep 13, 2026 (signed off)
Live-tested against the deployed VPS, not just read from source:
- **IDOR**: registered two real test accounts, confirmed user B gets `404`/`[]` trying to read, PATCH, or DELETE user A's broker account/holdings by guessing IDs. Every route in `holdings.py`, `assets.py`, `family.py` requires `get_current_user` and filters by `current_user.id`.
- **Auth bypass**: no-token request to a protected route → `401`. Confirmed.
- **SQL injection**: probed the login form with a classic `' OR '1'='1` payload — SQLAlchemy ORM parameterizes everything, no effect.
- **Weak passwords (found + fixed)**: server accepted `"1234"` via direct API call — the 8-char minimum was frontend-only. Added a server-side check in `backend/routers/auth.py`; now returns `422`.
- **Brute force (found + fixed)**: no limit on failed logins. Added an in-memory 5-attempts/5-minute lockout per email (`429` after 5 fails) — `ponytail: single-worker in-memory lockout, move to Redis if this ever runs multi-worker`.
- **Secrets**: `SECRET_KEY`, `APP_ENCRYPTION_KEY`, DB password are random-generated, live only in the VPS's `/opt/FinFlow/.env`, never committed.
- **Network exposure**: Postgres and Redis are container-internal only (fixed this session — both were previously bound to `0.0.0.0` with no auth, reachable from the open internet).
- **Transport**: real HTTPS via Let's Encrypt on `finflow.fortressintelligence.space`, nginx reverse proxy, HTTP→HTTPS redirect.
- **Fixed (Sep 13, 2026 follow-up)**: `/docs` and `/redoc` are now disabled unless `ENVIRONMENT=development` is set (defaults to off — the VPS doesn't set this, so prod stays locked). `CORS allow_origins` now reads from `ALLOWED_ORIGINS` env var, defaulting to `https://finflow.fortressintelligence.space` instead of `*`. See `backend/main.py`.
- **Explicitly rejected**: a suggestion (from a separate parallel session) to copy the `.env` secrets and SQLite DB to Dad's laptop for a local install. Don't do this — it relocates the broker-credential encryption key onto a second, less-controlled machine and defeats the point of the hosted URL. See the walkthrough note in this session's transcript for the reasoning.

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
1. **Trend accuracy widget**: surface `GET /holdings/{id}/trend-history` on the
   dashboard (e.g. "Very Bullish called right 6/9 times") — data pipeline is
   built (see above), needs a few weeks of real snapshots before it's meaningful.
2. Commit the untracked broker + holdings + login files.
3. **Portfolio Connectors**: read-only API integration for Binance and Luno.
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
