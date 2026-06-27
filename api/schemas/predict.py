"""
schemas/predict.py — Pydantic models for the POST /api/predict endpoint.
"""
from pydantic import BaseModel, Field
from typing import Optional


class GridEntry(BaseModel):
    abbreviation: str = Field(..., description="3-letter driver code, e.g. 'VER'")
    grid_position: int = Field(..., ge=1, le=20, description="Starting grid position (1 = pole)")
    quali_gap_to_pole: float = Field(0.0, ge=0.0, description="Gap to pole in seconds (0.0 for pole sitter)")


class PredictRequest(BaseModel):
    race: str = Field(..., description="Full race name, e.g. 'Monaco Grand Prix'")
    year: int = Field(2026, ge=2020, le=2030)
    grid: list[GridEntry] = Field(..., min_length=2, max_length=20)
    mc_runs: int = Field(100, ge=10, le=1000, description="Monte Carlo iterations")


class DriverResult(BaseModel):
    rank: int
    driver: str
    grid: int
    median_position: int
    expected_range: str           # e.g. "P1-P2" or "P3"
    win_probability: float        # 0–100
    podium_probability: float     # 0–100
    top10_probability: float      # 0–100
    confidence: float             # 0–100
    trend: str                    # "up" | "down" | "steady"


class PredictResponse(BaseModel):
    race: str
    year: int
    confidence: float             # overall model confidence 0–1
    mc_runs: int
    results: list[DriverResult]
