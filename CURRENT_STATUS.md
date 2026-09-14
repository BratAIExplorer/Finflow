# FinFlow Current Status (Updated: Sep 14, 2026)

## 🐛 Regression Fixed: CORS/localhost:8000 on Live Site — Sep 14, 2026
The VPS redeploy above (theme-engine fix) introduced a real regression:
merging `main`'s `frontend/Dockerfile` wholesale dropped the
`ARG NEXT_PUBLIC_API_URL` / `ENV` wiring the old Dockerfile had. Since
Next.js inlines `NEXT_PUBLIC_*` vars at **build time**, every component
(`portfolio/page.tsx`, `BrokerSettings`, `LoginModal`, `HoldingsTable`,
`MarketBoardPanel`, `NewsPanel`) silently fell back to its
`http://localhost:8000` default — breaking every API call on the live site
with `CORS policy: No 'Access-Control-Allow-Origin' header` errors, since
the browser was trying to reach `localhost` instead of
`https://finflow.fortressintelligence.space/api`.

**Fix**: restored the two missing lines in `frontend/Dockerfile`'s builder
stage (`ARG NEXT_PUBLIC_API_URL` + `ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}`)
so `docker-compose.yml`'s existing build arg actually reaches the build.
Verified locally (built bundle has zero `localhost:8000` occurrences, real
URL present) and on the live container (`docker exec finflow-frontend grep`
— 0 `localhost:8000`, 4 files with the correct origin) before calling it
done. Pushed as `7249a9c` on `main`, redeployed to the VPS.

**Lesson**: when a merge conflict resolution replaces a whole file (not a
targeted patch), diff the old and new versions for *behavior*, not just
"does it look more complete" — the newer Dockerfile looked like a strict
upgrade (multi-stage, non-root user, standalone output) but silently
dropped a load-bearing build arg the old one had. Worth an explicit
post-merge smoke test against the deployed environment's actual origin,
not just `tsc`/`build` succeeding.

## 🚀 VPS Deploy Drift Fixed: Theme Engine Now Actually Live — Sep 14, 2026
Discovered the Light/Dark toggle documented as "done" (see below) had never
reached the live site, because three copies of the frontend had silently
diverged:
- `main` (git) had the real theme-engine code (`ThemeToggle.tsx`, pre-hydration
  script, typography scale).
- `feature/market-board-tab` (git) was branched before that commit and never
  merged it — same hardcoded `className="dark"` bug, no toggle.
- **The VPS itself (`/opt/FinFlow`) has no `.git` at all** — it's a manual
  `scp`/file-drop deploy that had drifted from *both* branches independently,
  and turned out to match `feature/market-board-tab`'s pre-merge state almost
  byte-for-byte (confirmed via diff before touching anything).
- A second, unused nested copy at `/opt/FinFlow/Finflow/frontend/` (not
  referenced by `docker-compose.yml`'s build context) added to the confusion
  during investigation — left in place, harmless, but worth cleaning up.

**Fix**: merged `main` into `feature/market-board-tab` locally (real 2-parent
merge — resolved 11 conflicts across `.env.example`, `.gitignore`,
`CURRENT_STATUS.md`, `DEPLOYMENT.md`, `README.md`, `docker-compose.yml`,
`frontend/Dockerfile`, `layout.tsx`, `page.tsx`, `PortfolioChart.tsx`,
`lib/utils.ts`), keeping this branch's auth flow (`LoginModal`,
`BrokerSettings`, `requireAuth` gating) alongside `main`'s `ThemeToggle` and
styling. Verified backend pytest (65/66 — see known-issue note below) and a
clean frontend production build before pushing to `origin/feature/market-board-tab`.
Then `scp`'d the merged frontend files to `/opt/FinFlow/frontend/` (the real
build path) via a one-off SSH key set up for this session, and rebuilt the
`frontend` container. Verified live: `finflow-theme` (the toggle's
localStorage key) and the "Sign in" button both present in the served HTML,
public site returns `200`.

**Known pre-existing issue (not caused by this work, not fixed yet)**:
`backend/tests/test_holdings.py::test_mstock_fetch_holdings_parses_and_filters_zero_qty`
fails because its fake HTTP fixture only queues one response before the
`ensure_session()` call, but that method now makes two real calls
(`/login` then `/verifytotp`) since `ec0aa98`'s 502-fix. No production
impact — the connector logic is correct, only the test fixture is stale.

**Follow-up recommended, not done yet**: set up a real `git clone` on the VPS
so future deploys are `git pull && rebuild` instead of hand-copied files —
today's whole investigation started because the server silently drifted from
every git branch with no way to diff against it.

## 📊 Deepak's Market Board Migrated as 4th Tab in Portfolio (NEW) — Sep 14, 2026
Migrated the entire standalone market board functionality from `C:\Antigravity\My Bots\DadsDashboard` directly into FinFlow's `/portfolio` page as a dedicated **Market Board** tab placed right after News:
- **Zero Functionality Lost**:
  - Watchlist management: loads from `backend/board/my_stocks.txt` (seeded with Dad's 12 NSE stocks: `KERNEX`, `NETWEB`, `ROSSTECH`, `DATAPATTNS`, `IDEA`, `SMLMAH`, `AVALON`, `BSE`, `GVT&D`, `APOLLO`, `BLUESTONE`, `MTARTECH`).
  - Price & Technical signals: yfinance quotes (`.NS`), Wilder's 14-period RSI with plain-language status (`Oversold — looks cheap`, `Weak`, `Neutral`, `Getting expensive`, `Overbought`), MACD 12/26/9 histogram with momentum status (`Rising — momentum up`, `Positive`, `Falling — momentum down`, `Negative`, `Flat`).
  - 5-bucket Trend Verdict (`Very Bullish`, `Bullish`, `Neutral`, `Bearish`, `Very Bearish`) with color coding and direction arrows.
  - Watchlist News: Google News RSS per watchlist stock, price-sensitive keyword tagging (`MATERIAL` keywords tuple -> red `IMPORTANT` badge), and sentiment classification (`pos`, `neg`, `neu`). Deduplication stored via SQLite `seen.sqlite`.
  - Add / Remove stock: Form to add NSE symbol and company name, with interactive red ✕ chips to remove stocks.
  - Desktop export: Retained export to `Desktop\MarketBoard` (`board_latest.csv`/`.xlsx`, `history.csv`/`.xlsx`, `news_history.csv`) for local environments; gracefully disabled in headless VPS/Docker environments.
- **Backend Architecture**:
  - New modular package `backend/board/` (`watchlist.py`, `data.py`, `news.py`, `export.py`).
  - FastAPI router `backend/routers/board.py` registered at `/board/` with `GET /board/` (in-memory cached snapshot for instant tab switching), `POST /board/refresh`, `POST /board/add`, `POST /board/remove`.
  - 15-minute background refresh job scheduled via in-process APScheduler alongside the daily trend job.
- **Frontend Architecture**:
  - `frontend/components/portfolio/MarketBoardPanel.tsx`: faithful senior-readable UI matching Deepak's Market Board with paper/cream aesthetics, large typography, indicator badges, and sources attribution table.
  - `frontend/app/portfolio/page.tsx`: updated `Tab` type to `"summary" | "holdings" | "news" | "board"`, tab list with `"Market Board"` placed after `"news"`.
- **Verification & Testing**:
  - Hermetic unit tests in `backend/tests/test_board.py` with 100% offline pass rate (12/12 passed). Full test suite: 71 passed (71/71 passing).
  - TypeScript compilation clean (`tsc --noEmit` exited with 0 errors).
  - Next.js production build (`npm run build`) compiled successfully with static route `/portfolio`.

## 📅 mStock Holding Acquisition Dates Auto-Reconciliation (NEW) — Sep 14, 2026
Automated purchase date resolution for mStock holdings, eliminating the `held — set date` prompt:
- **Root Cause Solved**: mStock's `/portfolio/holdings` endpoint aggregates positions without purchase timestamps, leaving `first_buy_date` empty and requiring manual entry.
- **Session & Credential Reuse**: Reuses the user's existing encrypted API credentials and active session token stored in `UserPlugin` (no extra setup or user input required).
- **FIFO Trade History Reconciliation**: `MStockConnector` automatically queries `GET /openapi/typea/trades` over the prior 365 days and runs a FIFO (First-In, First-Out) matching algorithm across BUY and SELL executions to pinpoint the acquisition date of remaining open lots.
- **Automatic UI & Tax Flag Activation**: Persists `first_buy_date` to `Holding.first_buy_date`. The frontend automatically converts `held — set date` into the actual holding duration (e.g. `held 183 days`) and activates the >365-day Long-Term Capital Gains tax flag.
- **Resilient Fallback**: Gracefully falls back to standard holding sync if the trades endpoint is unavailable or trades predate the query window.
- **Tests**: Verified by unit test suite in `backend/tests/test_mstock_dates.py` (100% pass).

## ☀️ / 🌙 Light & Dark Mode Engine + Typography Scaling — Sep 14, 2026
Full dual-theme support and enhanced typography scale deployed to `main`:
- **Light Mode (White) & Dark Mode Switcher**: Added an interactive Sun ☀️ / Moon 🌙 toggle button (`frontend/components/ThemeToggle.tsx`) in the floating glass navigation bar. Smooth animated pill transition with active theme state. User choice is stored in `localStorage` (`finflow-theme`) and loaded via pre-hydration script in `layout.tsx` to eliminate theme flashing.
- **Adaptive Glassmorphism**: In `frontend/app/globals.css`, updated CSS tokens and `.glass-surface` styling to adapt dynamically: clean slate-50/white frosted cards with `border-slate-200/90` and crisp text in Light Mode, and midnight glass in Dark Mode.
- **Increased Typography Scale**: Scaled base HTML font size to `17.5px` (+15–20% boost to all rem units) and enlarged component sizes: Hero Headline (`text-6xl md:text-8xl lg:text-9xl`), Net Worth (`text-5xl md:text-6xl`), Stat Cards (`text-3xl font-extrabold`), form inputs/labels (`text-base` / `text-sm`), and chart axis (`14px`).
- **Production Docker & VPS Orchestration**: Added multi-stage standalone `frontend/Dockerfile`, `docker-compose.yml`, automated `deploy.sh` script, and `.env.example`.
- **Code Health**: Added missing `frontend/lib/utils.ts` (`clsx` + `tailwind-merge`). Production build (`npm run build`) compiles with 0 errors.

## ⚠️ RETRACTION: neither momentum finding holds up — Sep 14, 2026
Two entries below (**"Strongest finding yet: sector laggards bounce back"**
and the Nifty-relative momentum result inside **"Two follow-up backtests"**)
are **retracted**. Both survived a first round of review but not a second,
more careful one. Left in place below rather than deleted, with this notice
first — showing what changed and why matters more than a clean-looking history.

**What was wrong, found by re-reviewing the methodology (not new data):**
1. **Wrong null.** The 55.3%/56.6%/z=-10.7 figures were compared against a
   50% coin flip. The actual unconditional base rate (price up in 30 days,
   this universe/window) is **51.5%** — the real gap was smaller than reported.
2. **Absolute grading of a relative claim.** "Outperform Nifty" is a relative
   claim (beat the benchmark), but it was graded on the stock's *absolute*
   price direction, not on whether the outperformance continued. A stock can
   beat a falling Nifty while falling itself — that's not what the label
   claims to predict, and it lets generic market drift masquerade as edge.
   The sector-relative "reversal" finding's headline evidence — hit rate
   strengthening monotonically from 1d→30d — has an equally parsimonious
   explanation under this bug: longer windows accumulate more drift, which
   *mechanically* produces that exact monotonic shape with zero real
   reversal effect required. Same bug, same illusion, both tests.
3. **Overlapping samples faked the sample size.** z-scores were computed as
   if 2,395 daily-sampled, 30-day-forward-window rows were independent
   trials. Consecutive rows share ~97% of their window. The real
   independent sample size is roughly (stocks) × (non-overlapping 6-month
   blocks) — on 16 stocks, about 30, not 2,395.
4. **Contradicted by better prior art already in this org.**
   `TradingBot/strategies/BACKTEST_FINDINGS.md` §9 already ran proper
   Jegadeesh-Titman 12-1 cross-sectional momentum — 48 Nifty names,
   **15 years**, monthly (non-overlapping), 40bps single-stock cost — and it
   **lost to equal-weight buy-and-hold** (18.2% vs 19.7% CAGR). Same factor
   family, far higher rigor, already answered. This should have been found
   during the original reuse-first search and wasn't — a real miss.

**Corrected diagnostic, run to confirm rather than just argue the math**:
fixed both bugs (relative-continuation grading + non-overlapping blocks) in
`backtest_momentum_corrected()`, re-ran on both the 16-stock and 50-stock
(`NIFTY_50`) universes, and on the sector-relative test. Every cell's
significance measured against its own matched empirical base rate, not an
assumed 50%:

| Test | n | Hit rate | Base rate | z |
|---|---|---|---|---|
| Nifty-relative Outperform (16 stocks) | 15 | 60.0% | 50.0% | 0.77 |
| Nifty-relative Underperform (16 stocks) | 13 | 69.2% | 50.0% | 1.38 |
| Nifty-relative Outperform (50 stocks) | 44 | 63.6% | 56.2% | 0.99 |
| Nifty-relative Underperform (50 stocks) | 46 | 52.2% | 56.2% | -0.55 |
| Sector-relative Outperform | 33 | 39.4% | 46.3% | **-0.79** |
| Sector-relative Underperform | 40 | 47.5% | 46.3% | 0.15 |

**Every cell is under |z|=1.4 — indistinguishable from noise, several not
even pointed the direction originally claimed.** This is a confirmatory
diagnostic on a small sample (30-96 observations per test), not the decisive
evidence on its own — `BACKTEST_FINDINGS.md` §9's 15-year result is what
actually settles it, and this corrected re-test agrees with it rather than
contradicting it. Consistent, not coincidental.

**Practical conclusion, matching this org's own prior finding**: no active
signal tested so far — RSI/MACD, ADX-gated, 200-DMA-gated, Nifty-relative
momentum, sector-relative momentum — beats simply holding a diversified
basket, net of realistic assumptions. The trend label on the dashboard
should be read as descriptive, not predictive. The parallel session's draft
plan to migrate the dashboard's trend label to the momentum signal should
**stop**, not pause — the finding it was built on didn't hold up.

**Adopted going forward**: any future signal claim in this project reports
significance corrected for the number of variants checked and for
non-independence of overlapping observations (the same idea as the
"Deflated Sharpe Ratio") — never a raw/naive z-score.

**Also fixed while reviewing this (unrelated bugs, both live in production, not deferred):**
- `docker-compose.yml`: `ACCESS_TOKEN_EXPIRE_MINUTES: 30` was hardcoded,
  silently overriding `auth.py`'s 7-day default and unfixable via `.env` —
  Dad was being logged out every 30 minutes in production. Fixed to
  `${ACCESS_TOKEN_EXPIRE_MINUTES:-10080}`. Also dropped `--reload` from the
  prod uvicorn command — combined with the `./backend` bind mount, any file
  touch on the VPS was restarting the whole app (and the in-process
  scheduler) mid-run. **Requires a VPS-side redeploy to take effect** —
  `/opt/FinFlow` is `scp`/`tar`-deployed, not git-managed (per
  `DEPLOYMENT.md`), so editing this repo file alone doesn't reach
  production; whoever deploys next must edit
  `/opt/FinFlow/docker-compose.yml` directly and run
  `docker compose up -d backend`.
- `backend/jobs/trend_snapshot.py`'s `grade_pending_snapshots()` had two
  real bugs, fixed rather than deferred since the job runs live daily and
  every day deferred was another day of bad data written to the very table
  meant to keep this honest: (1) it graded against *today's* live price
  compared by calendar days, which silently mis-grades on weekends/holidays
  (Saturday's "current price" is Friday's close, so a Friday snapshot's
  1-day grade compares a price to itself) — fixed to grade against the
  actual close on/after the due *trading* date; (2) it re-queried and
  re-priced every fully-graded historical snapshot forever — fixed by
  filtering out rows where `hit_30d` is already set. New tests in
  `backend/tests/test_trend_snapshot.py` cover both.
- Left alone (found, not yet acted on): `Finflow/Finflow/docker-compose.yml`
  is a genuinely empty (0 bytes), stale file dated Jul 3 — harmless but
  confusing for a future session; flagging for deletion rather than
  deleting without being asked.

## 🏆 RETRACTED — Strongest finding yet: sector laggards bounce back — Sep 14, 2026
Continued digging for signals after the Nifty-relative momentum result.
GitHub-checked first (per dev workflow): reviewed `backtesting.py` (8,961★),
`vectorbt` (9,081★) and `ta-lib-python` (12,245★) — none earned their
complexity for what was left to test (a couple more indicator formulas, a
different benchmark series); stuck with the existing hand-rolled, tested
`backtest_trend.py`. Reused `TradingBot/strategies/sector_map.py`'s NSE
sector mapping instead of building one.

- **Momentum lookback scan** (1/3/6/9/12 months): 6-month remains the
  cleanest single window (55.3% @ 30d, z=5.2). The 9-12mo "losers keep
  losing" cells were also large (z=3.8-4.2) but came from scanning five
  windows to find them — flagged as unconfirmed until tested on an
  independent universe, not treated as a finding on their own.
- **Volume confirmation** (only count a 6mo-Outperform call when that day's
  volume is above its own 20-day average): hit rate rose from 55.3% to
  **57.6%** at 30 days, but on roughly half the sample (n=962 vs 2,395) — so
  the raw z-score actually *fell* slightly (5.2 → 4.7) despite the better
  point estimate. Both are strongly significant; volume confirmation trades
  frequency for a somewhat higher per-call hit rate, it doesn't add a new
  edge on top of momentum.
- **Sector-relative momentum** (has a stock beaten its *own sector peers*
  over 6 months, leave-one-out so it's never compared against itself; 40
  symbols across 10 sectors, reusing TradingBot's sector map): outperformers
  showed a **weaker** version of the Nifty-relative result (53.6% @ 30d,
  z=5.7). But the underperform side is the real story:
  **sector laggards do not keep lagging — they bounce.** Betting that an
  underperformer keeps falling was wrong **56.5% of the time** at 30 days
  (43.5% hit rate against a "keeps falling" bet — z = **-10.7**, the largest
  magnitude of anything tested this session), and the effect **strengthens
  monotonically** with the window: z = -1.9 (1d) → -4.3 (7d) → -10.7 (30d).
  A clean, monotonic pattern across one test (not five scanned windows) is
  what makes this the most convincing single result so far — this reads as
  genuine mean-reversion: a stock that's quietly fallen behind its own
  sector peers tends to catch back up, not keep falling further behind.
- **Practical read**: two independent, real effects now identified —
  (1) a stock beating the broad market over 6 months tends to keep beating
  it (continuation), and (2) a stock lagging its own sector peers tends to
  catch back up (reversion). These point in different directions
  deliberately — momentum vs. mean-reversion are the two classic families
  of quant signals, and finding one real example of each is a more solid
  foundation than finding two variations on the same idea.
- Code: `backtest_momentum()` extended with `volume=`, plus
  `build_sector_benchmark()` and `run_sector_momentum()`, all in
  `backend/tools/backtest_trend.py`. Tests: 14 total (5 new) in
  `backend/tests/test_backtest_trend.py`.
- Not built into the product yet — still at the "what's real" stage; next
  is deciding what to actually put in front of Dad.

## 🔑 mStock connector was re-authenticating via TOTP on every single sync — Sep 14, 2026
Found while tracing the broker-abstraction graph: `MStockConnector` stored its
daily session token only as an in-memory instance attribute
(`self._access_token`), never in `UserPlugin.config`. `ZerodhaConnector`
already did this correctly (`session_state` dict, persisted by the router).
Since `_make_connector()` builds a fresh connector object per request, mStock's
"is my session still fresh" check was always `False` — every sync ran a full
TOTP round-trip, whether or not the token from an hour ago was still valid.
- **Fixed**: `MStockConnector` now takes `session_state` (same
  `access_token`/`access_token_date` shape as Zerodha) and
  [holdings.py](backend/routers/holdings.py)'s `_make_connector()` /
  `_run_sync()` load and persist it through `UserPlugin.config`, same as
  Zerodha already did. TOTP now only fires once per day, not once per sync.
- **Also fixed in passing**: `test_mstock_fetch_holdings_parses_and_filters_zero_qty`
  was queuing an unused extra fake HTTP response, which shifted the mock
  response order and made the test fail for the wrong reason — removed it.
- Test: `test_mstock_skips_totp_when_session_state_is_fresh` in
  `backend/tests/test_holdings.py` guards the caching behavior — it queues
  zero login/TOTP responses, so a regression back to always-re-authenticate
  fails loudly (IndexError) instead of silently.
- **Not changed**: no DB migration — existing `plugin.config` rows already
  default to `{}`, so old mStock accounts just re-auth once more on the first
  sync after deploy, then cache normally like Zerodha does.

## 🎯 Two follow-up backtests — RETRACTED (see top of this file) — Sep 14, 2026
**The "real signal" (Nifty-relative momentum) below is retracted — see the
⚠️ RETRACTION entry at the top of this file for why (wrong null, absolute-
vs-relative grading bug, overlapping samples).** The 200-DMA result's
"inconclusive" verdict still stands as originally written.

Extended `backend/tools/backtest_trend.py` with the two candidates from the
"how would you improve accuracy" discussion, same 16-symbol/2-year data, same
no-lookahead/direction-only methodology as the original (coin-flip) result:

- **200-day moving average alignment filter** (only trust a Bullish call when
  price is above its own 200 DMA, Bearish when below — targets RSI/MACD
  firing against the stock's own primary trend): **mostly still noise**
  (43–57% across cells). One cell (Bearish, 30-day, n=272) hit 56.6%, but
  that's only ~2.2 standard deviations from a coin flip on one of many cells
  tested — the kind of result that shows up by chance when you check enough
  slices. Not treating it as a finding without more data.
- **Relative momentum vs Nifty 50** (independent signal, not an RSI/MACD
  filter: has the stock outperformed the index over the trailing ~6 months?
  — the best-documented factor in equity research, e.g. Jegadeesh-Titman):
  **this one is real.** Stocks that had been outperforming Nifty went on to
  rise over the next 30 days **55.3% of the time** (n=2,395) — about
  **5.2 standard deviations** from a 50/50 coin flip, not explainable by
  chance at that sample size. The 1-day and 7-day windows were still ~49–52%
  (no short-term edge — momentum is a medium-term effect, consistent with the
  literature), and the underperform side was closer to neutral (48.5% at 30
  days) — momentum showing up mainly on the winning side, at the horizon
  research predicts, is what makes this look like a real effect rather than a
  lucky cell.
- **Conclusion**: still not touching `classify_trend()`'s live labeling logic
  — momentum is a genuinely different signal, not a tweak to RSI/MACD, so
  the honest next step is surfacing it as a **second, independent** data
  point (e.g. "Outperforming Nifty by X% over 6mo") alongside the existing
  trend label, not folding it into the same rule table. Not built yet —
  discussing scope with the user before adding it to `Holding`/the dashboard.
- Code: `backtest_momentum()` and the `require_sma200_alignment` gate on
  `backtest_symbol()`, both in `backend/tools/backtest_trend.py`. Tests:
  `backend/tests/test_backtest_trend.py` now has 11 tests (5 new).

## 🔐 Auth flow — fixed 15-min session expiry + added sign-in-from-error path — Sep 14, 2026
Portfolio page showed "Session expired" with no way to sign back in except
navigating away. Root cause found while fixing it: `backend/auth.py`'s
`create_access_token()` defaults to a **15-minute** expiry when no
`expires_delta` is passed, and `routers/auth.py`'s `login()` never passed one
— so every login silently expired in 15 minutes regardless of the
(unused) `ACCESS_TOKEN_EXPIRE_MINUTES` constant.
- **Fixed**: `login()` now passes `expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)`;
  the constant itself raised to 7 days (env-overridable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
  — this is a single-user portfolio viewer, no reason to force re-login mid-session.
- **Frontend**: [frontend/app/portfolio/page.tsx](frontend/app/portfolio/page.tsx) now shows
  a "Sign in" button next to the expired-session message that opens the existing
  `LoginModal` in place, instead of leaving the user stuck.
- **Password reset**: no email service exists in FinFlow yet (checked — nothing
  configured), so a real "forgot password" email flow wasn't built. Added
  `backend/tools/reset_password.py` instead — an admin CLI
  (`python -m backend.tools.reset_password <email> <new_password>`) that resets
  a password directly in the DB, no email infra needed. `LoginModal` now has a
  small hint pointing to this instead of promising a self-serve reset that
  doesn't exist.
- Test: `backend/tests/test_auth_token_expiry.py` guards against the
  expires_delta regression coming back.
- **Note**: while testing this live, the real `bharatsamant@gmail.com` password
  in the dev DB got overwritten by the CLI test run — reset it again if needed.

## 🔬 Trend label backtest — result: no measurable edge — Sep 14, 2026
Before waiting weeks for live `trend_snapshots` data to judge accuracy, ran the
exact same direction-only grading logic against 2 years of real NSE history
(16 liquid large/mid-caps: RELIANCE, TCS, HDFCBANK, INFY, etc.) instead —
answers the "is this trustworthy?" question today, not in 30 days.
- **New**: `backend/tools/backtest_trend.py` — `python -m backend.tools.backtest_trend
  [SYMBOL...]`. Vectorized (computes RSI/MACD/ADX once per symbol over the
  full history, no lookahead — confirmed by
  `test_backtest_symbol_produces_no_lookahead_rows`), so it runs in seconds,
  not the weeks the live tracker needs.
- **Result — current `classify_trend()` rule table has no measurable
  directional edge**: hit rates across all 4 labels (Bullish/Bearish/Very
  Bullish/Very Bearish) and all 3 windows (1/7/30 days) landed at **45–53%**
  — indistinguishable from a coin flip (n=1,100–2,100 per cell, so this isn't
  a small-sample fluke).
- **Tested the ADX-filter idea from the trend-improvement discussion** (only
  grade/act on calls made when ADX ≥ 20, i.e. an actual trend is underway,
  not chop) — **no improvement**: 46–53% gated vs. 45–53% ungated, same
  coin-flip range. The hypothesis that whipsaw-in-chop was the main accuracy
  problem did not hold up against real data.
- **Conclusion, stated plainly**: RSI+MACD alone is not currently a validated
  trading signal for this portfolio's stocks over these windows. Not changing
  `classify_trend()`'s live logic on the strength of an unproven "fix" —
  ADX gating was reverted from `pricing.py` (no production code depends on
  it; it stays as backtest-only, ported from
  `C:\Antigravity\TradingBot\regime_monitor.py`'s `_calculate_adx()`).
- **What this means for Dad's dashboard right now**: the trend label should
  be read as descriptive ("here's what RSI/MACD currently say"), not
  predictive. The `trend_snapshots` tracker built alongside this (below)
  still ships — it's what will show, with real numbers over time, whether
  that changes; right now the backtest says don't expect it to.
- Reused, not rebuilt: the ADX Wilder formula came from
  `TradingBot/regime_monitor.py`; the "no-lookahead" backtest discipline
  followed `TradingBot/strategies/factor_backtest.py`'s stated honesty rules.
  `TradingBot/_dev_tools/backtester.py` (uses the `backtesting.py` package)
  was reviewed but not reused — it's built for simulating buy/sell trades
  with cash/commission, a different shape of problem than grading a label's
  hit rate.
- Tests: `backend/tests/test_backtest_trend.py` (7 tests) — including a
  regression test for a real bug hit during this work (see below).
- **Bug found + fixed during this work**: the backtest's hit-rate columns
  were stored as `numpy.bool_` in an object-dtype DataFrame column, which
  silently broke `.mean()` under `groupby()` — first run showed ~0.1% hit
  rates (obviously wrong, not "the strategy is terrible"). Root-caused to the
  dtype, fixed by storing native Python `bool`, re-verified against a manual
  count, and added `test_summarize_hit_rate_matches_manual_count_at_scale` +
  `test_backtest_symbol_hit_values_are_native_bool_not_numpy_bool` so it
  can't silently regress.

## 📈 Trend accuracy tracking (NEW) — Sep 14, 2026
Dad decides buy/sell based on the Bullish/Bearish trend label, but until now
only the *latest* label was ever stored — no way to check if a past call was
right. Added:
- **`trend_snapshots` table** (`backend/models.py`): one row per holding per
  day — label, RSI/MACD, price at capture, and hit/miss outcome columns for
  1-day, 7-day, and 30-day windows (null = still pending).
- **`backend/jobs/trend_snapshot.py`**: `record_snapshot()` writes one row
  from already-computed signals (reuses `pricing.compute_signals`/
  `classify_trend` — no new price logic); `grade_pending_snapshots()` checks
  due windows against the current price and marks hit/miss by direction only
  (Bullish = hit if price rose, Bearish = hit if it fell; Neutral is never
  graded). `record_snapshot()` is called from **two** places, per user
  request: the manual "sync now" route (`holdings.py`) *and* the daily
  scheduled job — so an intraday trend flip from Dad clicking refresh gets
  captured too, not just the once-a-day scheduled call. This means multiple
  rows/day are possible on days he refreshes more than once — expected, not
  a bug.
- **Daily job scheduled via in-process APScheduler** (`backend/main.py`,
  started in the existing `on_startup` hook) at 16:00 IST, as a safety net
  for days nobody opens the dashboard — chosen over VPS crontab since it
  ships inside the container automatically, no host-side setup needed on the
  shared Hostinger box.
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
- **Multi-Currency**: FX service working for conversion and formatting (MYR, INR, USD, SGD).
- **Theme Engine**: Complete **Light Mode (White)** and **Dark Mode** toggle switch with smooth animations and persistent user preference.
- **Adaptive Glassmorphism**: Tailored frosted glass styling for both dark midnight and clean bright light modes.
- **Typography Scaling**: Increased font size scale (+15–20% boost) across all components (Hero, Net Worth, Stat cards, inputs, charts) for effortless readability.
- **Docker & VPS Deployment**: Standalone production Next.js Dockerfile, FastAPI Dockerfile, multi-container `docker-compose.yml`, automated `deploy.sh` script, and `.env.example`.
- **Code Utilities**: Standardized `cn` utility (`clsx` + `tailwind-merge`) resolving compilation dependencies.
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
