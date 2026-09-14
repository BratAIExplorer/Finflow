import os

from dotenv import load_dotenv

load_dotenv()  # read .env before any module (database, auth, crypto_utils) checks os.getenv

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .database import SessionLocal, init_db
from .jobs.trend_snapshot import grade_pending_snapshots, snapshot_all_holdings
from .routers import auth, assets, family, holdings, news

IS_DEV = os.getenv("ENVIRONMENT", "production").lower() == "development"
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "https://finflow.fortressintelligence.space"
).split(",")

app = FastAPI(title="FinFlow API", docs_url="/docs" if IS_DEV else None, redoc_url="/redoc" if IS_DEV else None)

def _run_daily_trend_job():
    db = SessionLocal()
    try:
        written = snapshot_all_holdings(db)
        graded = grade_pending_snapshots(db)
        print(f"[trend job] snapshotted {written} holdings, graded {graded} outcomes")
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    init_db()
    scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
    scheduler.add_job(_run_daily_trend_job, "cron", hour=16, minute=0)
    scheduler.start()

app.include_router(auth.router)
app.include_router(assets.router)
app.include_router(family.router)
app.include_router(holdings.router)
app.include_router(news.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "FinFlow API is running"}
