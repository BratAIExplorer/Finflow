from dotenv import load_dotenv

load_dotenv()  # read .env before any module (database, auth, crypto_utils) checks os.getenv

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routers import auth, assets, family, holdings

app = FastAPI(title="FinFlow API")

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(auth.router)
app.include_router(assets.router)
app.include_router(family.router)
app.include_router(holdings.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "FinFlow API is running"}
