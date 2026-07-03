# FinFlow — Open-source Family Wealth Sharing Platform

A premium financial dashboard for families to track assets, manage insurance, and coordinate lending.

**Live Features:**
- 🔐 Authentication (register, login, JWT tokens)
- 💰 Asset tracking (add/view family assets)
- 👨‍👩‍👧 Family management (invitations, shared access)
- 📊 Premium glassmorphism dashboard UI (Next.js 19 + Tailwind)

**In Development:**
- Broker connectors (Binance, Luno)
- Insurance forms & templates
- Loan request workflows

---

## Quick Start (Local Development)

### Prerequisites
- Python 3.13+
- Node.js 18+
- PostgreSQL 14+

### Backend Setup

1. **Activate Python environment** (from `C:\Antigravity\FinFlow`):
   ```powershell
   venv\Scripts\Activate.ps1
   ```

2. **Create `.env` file**:
   ```bash
   copy .env.example .env
   ```

3. **Set up database** (first time only):
   ```powershell
   venv\Scripts\python -m alembic upgrade head
   ```
   Or for a fresh database, the app auto-creates tables on startup.

4. **Run backend** (API listens on `http://localhost:8000`):
   ```powershell
   venv\Scripts\uvicorn backend.main:app --reload
   ```

5. **Test API** (interactive docs):
   - Open `http://localhost:8000/docs`
   - Try endpoints: POST `/auth/register`, POST `/auth/login`, POST `/assets`, etc.

### Frontend Setup

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Run dev server** (opens `http://localhost:3000`):
   ```bash
   npm run dev
   ```

---

## Project Structure

```
FinFlow/
├── backend/                 # FastAPI REST API
│   ├── main.py              # App entry point
│   ├── database.py          # SQLAlchemy setup
│   ├── models.py            # Database schemas
│   ├── auth.py              # JWT/login logic
│   ├── currency.py          # Exchange rate API
│   └── routers/
│       ├── auth.py          # Authentication endpoints
│       ├── assets.py        # Asset CRUD
│       └── family.py        # Family invites/sharing
│
├── frontend/                # Next.js 19 dashboard
│   ├── app/                 # Page routes
│   ├── components/          # Reusable UI
│   │   ├── StatCard.tsx
│   │   ├── PortfolioChart.tsx
│   │   └── AddAssetForm.tsx
│   └── package.json
│
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Local + prod configs
└── .env.example             # Environment template
```

---

## Environment Variables

Copy `.env.example` → `.env` and fill in your values:

```ini
# Database
DATABASE_URL=postgresql://finflow_user:finflow_password@localhost:5432/finflow_db
POSTGRES_USER=finflow_user
POSTGRES_PASSWORD=finflow_password
POSTGRES_DB=finflow_db

# API
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional: Exchange Rate API
EXCHANGERATE_API_KEY=your-api-key
```

---

## API Endpoints (Testing)

Once backend is running, visit `http://localhost:8000/docs`:

**Auth:**
- `POST /auth/register` — Create account
- `POST /auth/login` — Get JWT token

**Assets:**
- `GET /assets` — List family assets
- `POST /assets` — Add asset
- `DELETE /assets/{id}` — Remove asset

**Family:**
- `POST /family/invite` — Invite family member
- `GET /family/members` — List family

---

## Docker (Production Deployment)

See [DEPLOYMENT.md](DEPLOYMENT.md) for VPS setup instructions.

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

## Recent Fixes

- ✅ **Fixed database import bug** (`backend/database.py` line 1) — was importing non-existent `create_all` function
- ✅ **Verified backend startup** — FastAPI app loads, all endpoints registered
- ✅ **Verified frontend** — Next.js build works, dashboard UI renders

---

## Next Steps

1. Set environment variables in `.env`
2. Run backend + frontend locally to test
3. Test API endpoints via `http://localhost:8000/docs`
4. For VPS deployment, see [DEPLOYMENT.md](DEPLOYMENT.md)

---

## Architecture Notes

- **Backend**: FastAPI + SQLAlchemy (PostgreSQL)
- **Frontend**: Next.js 19 + React 19 + Tailwind CSS
- **Auth**: JWT tokens, bcrypt hashing
- **Caching**: Redis (optional, configured in docker-compose)
- **Broker APIs**: Binance, Luno (future)

---

Questions? Check [DEPLOYMENT.md](DEPLOYMENT.md) for production setup.
