"""
schemas/analytics.py — Pydantic models for the GET /api/analytics/* endpoints.
"""
from pydantic import ConfigDict
from pydantic import BaseModel
from typing import Optional


class DriverStanding(BaseModel):
    position: int
    driver: str               # abbreviation
    full_name: str
    team: str
    points: float
    wins: int
    podiums: int
    skill_score: float        # 0-100 Apex custom score
    avg_quali_delta: float    # seconds vs teammate (negative = faster)
    races: int


class StandingsResponse(BaseModel):
    season: int
    standings: list[DriverStanding]


class FeatureImportanceItem(BaseModel):
    feature: str
    importance: float         # raw XGBoost importance
    weight_pct: float         # normalized to 0-100 percentage


class FeatureImportanceResponse(BaseModel):
    features: list[FeatureImportanceItem]


class TrackTypeAccuracy(BaseModel):
    type: str
    confidence: float


class ModelAccuracyItem(BaseModel):
    year: int
    mae: float                # mean absolute error in finishing positions
    cv_split: str             # e.g. "2020-23 → 2024"


class AnalyticsOverviewResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    feature_importance: list[FeatureImportanceItem]
    track_accuracy: list[TrackTypeAccuracy]
    model_accuracy: list[ModelAccuracyItem]


class RaceResultRow(BaseModel):
    position: int
    driver: str               # abbreviation
    team: str
    grid: int
    points: float
    status: str
    dnf: bool


class RaceResultResponse(BaseModel):
    race: str
    year: int
    round: int
    results: list[RaceResultRow]
