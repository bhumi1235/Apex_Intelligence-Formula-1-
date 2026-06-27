"""
schemas/simulate.py — Pydantic models for the POST /api/simulate endpoint.
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal


class GridOverride(BaseModel):
    abbreviation: str = Field(..., description="3-letter driver code")
    grid_position: int = Field(..., ge=1, le=20)


class SimulateRequest(BaseModel):
    race: str = Field(..., description="Historical race name, e.g. 'British Grand Prix'")
    year: int = Field(..., ge=2020, le=2025)
    weather: Literal["dry", "mixed", "wet"] = Field("dry")
    overrides: list[GridOverride] = Field(default_factory=list, max_length=20)
    mc_runs: int = Field(100, ge=10, le=1000)


class SimDriverResult(BaseModel):
    driver: str                   # abbreviation
    finish: int | None            # None = DNF
    grid: int                     # starting position (after override)
    actual_finish: int | None     # real historical finish (None = DNF)
    delta: int                    # actual_finish - simulated_finish (positive = sim is better)
    podium_pct: float
    top10_pct: float
    confidence: float


class SimulateResponse(BaseModel):
    race: str
    year: int
    weather: str
    mc_runs: int
    chaos_index: int              # 0-100: how much the sim diverges from history
    results: list[SimDriverResult]
