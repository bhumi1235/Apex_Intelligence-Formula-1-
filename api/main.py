"""
api/main.py — Apex Intelligence FastAPI application entry point.

Startup:
  uvicorn api.main:app --reload --port 8000

All ML artifacts (prediction_model.pkl, simulation_model.pkl, CSVs) are loaded
ONCE at startup via the lifespan context manager — no per-request disk I/O.

CORS is configured to allow the Next.js frontend (localhost:3000 in dev,
Vercel production URL via env var APEX_FRONTEND_URL).
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.services.loader import store
from api.routers import races, drivers, predict, simulate, analytics


# ── Lifespan: load all heavy artifacts at startup ────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load models + datasets once when the server starts."""
    print("\n" + "=" * 50)
    print("  APEX INTELLIGENCE -- API Server Starting")
    print("=" * 50)
    store.load()
    print("[apex] Server ready.\n")
    yield
    # Cleanup (nothing needed — OS will reclaim memory)
    print("\n[apex] Server shutting down.")


# ── Application ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="Apex Intelligence API",
    description=(
        "FastAPI backend for the Apex Intelligence F1 Race Intelligence Platform. "
        "Exposes prediction, simulation, driver analytics, and live race data endpoints."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────

# In production, set APEX_FRONTEND_URL env var to your Vercel domain
FRONTEND_URL = os.getenv("APEX_FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",       # Next.js dev server
        "http://localhost:3001",       # alternate dev port
        FRONTEND_URL,                  # production frontend
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────────

app.include_router(races.router)
app.include_router(drivers.router)
app.include_router(predict.router)
app.include_router(simulate.router)
app.include_router(analytics.router)


# ── Health check ─────────────────────────────────────────────────────────────

@app.get("/", tags=["health"])
async def root():
    return {
        "status": "ok",
        "service": "Apex Intelligence API",
        "version": "1.0.0",
        "models_loaded": store.prediction_model is not None,
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
async def health():
    return {
        "status": "healthy",
        "prediction_model": store.prediction_model is not None,
        "simulation_model": store.simulation_model is not None,
        "dataset_rows": len(store.skill_features) if store.skill_features is not None else 0,
    }
