# Local Development Setup — No Docker Required

This guide runs FinFlow entirely on your local machine using native Python and Node.js.

## Prerequisites

- **Python 3.13+** — [Download](https://www.python.org/downloads/)
- **Node.js 18+** — [Download](https://nodejs.org/)
- **PostgreSQL 14+** — [Download](https://www.postgresql.org/download/) (or use a cloud DB)

---

## Step 1: Set Up PostgreSQL

### Option A: Local Installation (Windows)
1. Install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/windows/)
2. During setup, set password for `postgres` user (e.g., `postgres123`)
3. Keep port as default `5432`

### Option B: Use a Cloud Database (Faster)
If you don't want to install PostgreSQL locally:

1. Use **Railway.app** or **Supabase**:
   - Railway: Sign up → New Project → Add PostgreSQL → Copy connection URL
   - Supabase: Create project → Copy `postgresql://...` URL from settings

2. Copy the connection string into `.env` as `DATABASE_URL`

### Create Local Database

If using local PostgreSQL:

```powershell
# Open PostgreSQL command prompt or psql
psql -U postgres

# Inside psql, run:
CREATE DATABASE finflow_db;
CREATE USER finflow_user WITH PASSWORD 'finflow_password';
ALTER ROLE finflow_user SET client_encoding TO 'utf8';
ALTER ROLE finflow_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE finflow_user SET default_transaction_deferrable TO on;
ALTER ROLE finflow_user SET default_transaction_read_uncommitted TO off;
GRANT ALL PRIVILEGES ON DATABASE finflow_db TO finflow_user;
\q
```

---

## Step 2: Set Up Backend (Python)

1. **Navigate to project root**:
   ```powershell
   cd C:\Antigravity\FinFlow
   ```

2. **Create and activate virtual environment**:
   ```powershell
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```

3. **Create `.env` file** (copy from template):
   ```powershell
   copy .env.example .env
   ```

4. **Edit `.env`** with your database credentials:
   ```ini
   DATABASE_URL=postgresql://finflow_user:finflow_password@localhost:5432/finflow_db
   SECRET_KEY=your-secret-key-here-change-in-production
   ```

5. **Install Python dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

6. **Verify backend loads** (should print OK):
   ```powershell
   python -c "from backend.database import engine, init_db; print('OK: Database module imports')"
   ```

---

## Step 3: Run Backend API

In the same PowerShell terminal (with venv activated):

```powershell
uvicorn backend.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Test the API

Open **`http://localhost:8000/docs`** in your browser.

You'll see an interactive API explorer where you can:
- ✅ Try POST `/auth/register` — Create account
- ✅ Try POST `/auth/login` — Get JWT token
- ✅ Try POST `/assets` — Add family asset
- ✅ Try GET `/family/members` — List family

---

## Step 4: Set Up Frontend (Node.js)

**Open a NEW PowerShell terminal** (keep the backend running in the other):

1. **Navigate to frontend**:
   ```powershell
   cd C:\Antigravity\FinFlow\frontend
   ```

2. **Install dependencies**:
   ```powershell
   npm install
   ```

3. **Create `.env.local`** (Next.js reads this):
   ```ini
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Run dev server**:
   ```powershell
   npm run dev
   ```

You should see:
```
  ▲ Next.js 16.1.6
  - Local:        http://localhost:3000
```

Open **`http://localhost:3000`** in your browser and you'll see the glassmorphism dashboard.

---

## Step 5: Test the Full Stack

### 1. Register a User
Go to `http://localhost:8000/docs`:
- Click **POST /auth/register**
- Click "Try it out"
- Fill in JSON:
  ```json
  {
    "email": "user@example.com",
    "password": "Test123!",
    "family_name": "Smith"
  }
  ```
- Click **Execute** → Copy the `access_token` from response

### 2. Login
- Click **POST /auth/login**
- Fill in form data: email + password
- Execute → Copy the new token

### 3. Add an Asset
- Click **POST /assets**
- Paste token in **Authorize** button (top right)
- Fill in:
  ```json
  {
    "name": "Tesla Stock",
    "type": "stock",
    "value": 15000,
    "currency": "USD"
  }
  ```
- Execute

### 4. View Dashboard
Go to `http://localhost:3000` — the UI should update to show your asset on the chart.

---

## Troubleshooting

### Backend won't start: "Database connection refused"
- ✅ Check PostgreSQL is running: `psql -U postgres -c "SELECT 1;"`
- ✅ Verify `DATABASE_URL` in `.env` is correct
- ✅ Make sure `finflow_user` has access: `psql -U finflow_user finflow_db`

### "ModuleNotFoundError: No module named 'backend'"
- ✅ Make sure you're in `C:\Antigravity\FinFlow` directory (not `frontend`)
- ✅ Check venv is activated: `(venv)` should appear in terminal

### Frontend shows "Cannot reach API"
- ✅ Backend must be running on `http://localhost:8000`
- ✅ Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
- ✅ No CORS errors? Backend should allow all origins (it does by default)

### "Port 8000 already in use"
```powershell
# Find and kill the process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## Development Workflow

**Terminal 1 — Backend** (stays running):
```powershell
cd C:\Antigravity\FinFlow
venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload
```

**Terminal 2 — Frontend** (stays running):
```powershell
cd C:\Antigravity\FinFlow\frontend
npm run dev
```

**Terminal 3 — Git/Admin** (for commits, etc.):
```powershell
cd C:\Antigravity\FinFlow
git status
git add .
git commit -m "Feature: ..."
```

---

## Next Steps

1. ✅ Backend running on `http://localhost:8000`
2. ✅ Frontend running on `http://localhost:3000`
3. ✅ Test endpoints via `http://localhost:8000/docs`
4. 📝 Make changes, see them reload instantly
5. 🚀 When ready for production, see [DEPLOYMENT.md](DEPLOYMENT.md)

---

## Database Migrations (if needed later)

When adding new models, create a migration:
```powershell
alembic revision --autogenerate -m "Add new table"
alembic upgrade head
```

---

You're all set! Happy coding 🎉
