# FinFlow — Quick Start (Copy & Paste)

Everything here is copy-paste ready. Just run the commands.

---

## One-Time Setup (5 min)

### 1. Python Backend Environment
```powershell
# From C:\Antigravity\FinFlow
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

### 2. Node Frontend Dependencies
```powershell
cd frontend
npm install
cd ..
```

---

## Run Locally (2 terminals, stay open)

### Terminal 1 — FastAPI Backend
```powershell
cd C:\Antigravity\FinFlow
venv\Scripts\Activate.ps1
uvicorn backend.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Terminal 2 — Next.js Frontend
```powershell
cd C:\Antigravity\FinFlow\frontend
npm run dev
```

**Expected output:**
```
  ▲ Next.js 16.1.6
  - Local:        http://localhost:3000
```

---

## Test in Browser

### API Docs (Test Endpoints)
🔗 **`http://localhost:8000/docs`**

Click **Try it out** on any endpoint:
- `POST /auth/register` — Create account
- `POST /auth/login` — Get token
- `POST /assets` — Add asset
- `GET /assets` — List assets

### Dashboard UI
🔗 **`http://localhost:3000`**

See the glassmorphism dashboard with your assets.

---

## Verify It Works

### Quick Test
1. Go to `http://localhost:8000/docs`
2. Try `POST /auth/register`:
   ```json
   {
     "email": "test@example.com",
     "password": "Test123!",
     "family_name": "Smith"
   }
   ```
3. Go to `http://localhost:3000` → See dashboard load

✅ **Done!**

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Cannot connect to database" | Database isn't running. See [SETUP_LOCAL.md](SETUP_LOCAL.md) step 1 |
| "ModuleNotFoundError: backend" | Make sure you're in `C:\Antigravity\FinFlow` (not `frontend`) |
| "Port 8000 in use" | `netstat -ano \| findstr :8000` → kill the process |
| Frontend can't reach API | Backend must be on `http://localhost:8000` |

---

## Project Structure

```
backend/          ← FastAPI API
frontend/         ← Next.js dashboard
docker-compose.yml  ← Production setup
requirements.txt  ← Python deps
.env.example      ← Environment template
```

---

## Next Steps

- ✅ Run both locally ← **You are here**
- 📖 See [SETUP_LOCAL.md](SETUP_LOCAL.md) for detailed setup
- 🚀 Production? See [DEPLOYMENT.md](DEPLOYMENT.md)
- 💾 Commit & push changes

---

That's it! Both services running, ready to develop.
