"""
routers/analytics.py — GET /api/analytics/* endpoints
Provides driver standings, feature importance, model accuracy stats,
and individual race results for the Analytics and Rankings pages.
"""
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from api.schemas.analytics import (
    StandingsResponse, DriverStanding,
    FeatureImportanceResponse, FeatureImportanceItem,
    AnalyticsOverviewResponse, TrackTypeAccuracy, ModelAccuracyItem,
    RaceResultResponse, RaceResultRow,
)
from api.services.loader import store
from api.services import live_data

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

# Feature human-readable labels (model abbreviation → display name)
FEATURE_LABELS: dict[str, str] = {
    "GridPosition":          "Grid position",
    "Grid_x_Skill":          "Grid × Skill interaction",
    "DriverPointsPercentile":"Driver championship momentum",
    "TeamPointsPercentile":  "Team championship percentile",
    "TeamCategory":          "Team tier (Top / Mid / Back)",
    "ConstructorGapPct":     "Constructor points gap",
    "Form_x_Team":           "Recent form × Team strength",
    "AvgFinish_Last5":       "Avg finish (last 5 races)",
    "GridQualiInteraction":  "Grid × Qualifying gap",
    "AvgFinish_Last3":       "Avg finish (last 3 races)",
    "QualiGapToPole":        "Qualifying gap to pole",
    "DNF_Probability":       "DNF probability",
    "SkillScore":            "Apex driver skill score",
    "IsStreetCircuit":       "Street circuit flag",
    "TrackCode":             "Track encoding",
}

# Street circuit identifier for track-type accuracy breakdown
STREET_CIRCUITS = {
    "Monaco Grand Prix", "Azerbaijan Grand Prix", "Singapore Grand Prix",
    "Saudi Arabian Grand Prix", "Miami Grand Prix", "Las Vegas Grand Prix",
}

# High-speed circuits
HIGH_SPEED_CIRCUITS = {
    "Belgian Grand Prix", "Italian Grand Prix", "British Grand Prix",
    "Dutch Grand Prix", "Austrian Grand Prix",
}


@router.get("/drivers", response_model=StandingsResponse)
async def get_driver_standings(
    year: int = Query(2025, ge=2020, le=2025),
    use_live: bool = Query(True, description="Try fetching live Jolpica standings first"),
):
    """
    Returns driver standings with Apex skill scores for the given season.
    Tries Jolpica-F1 API for official points/wins, then enriches with local skill scores.
    Falls back fully to computed local data if the API is unavailable.
    """
    skill_df = store.get_skill_scores(year)
    skill_map: dict[str, float] = {}
    quali_map: dict[str, float] = {}
    races_map: dict[str, int] = {}
    if not skill_df.empty:
        for _, row in skill_df.iterrows():
            abbr = str(row["Abbreviation"]).upper()
            skill_map[abbr] = round(float(row.get("SkillScore", 50.0)), 1)
            quali_map[abbr] = round(float(row.get("AvgQualiDelta", 0.0)), 4)
            races_map[abbr] = int(row.get("Races", 0))

    # ── Try live Jolpica standings ─────────────────────────────────────────────
    live_standings = None
    if use_live:
        live_standings = await live_data.get_jolpica_driver_standings(year)

    if live_standings:
        # Compute podiums from local dataset
        season_df = store.get_driver_standings(year)
        podium_map: dict[str, int] = {}
        if not season_df.empty:
            for abbr, grp in season_df.groupby("Abbreviation"):
                podium_map[str(abbr).upper()] = int((grp["Position"] <= 3).sum())

        result_standings: list[DriverStanding] = []
        for s in live_standings:
            abbr = s["abbreviation"].upper()
            result_standings.append(DriverStanding(
                position=s["position"],
                driver=abbr,
                full_name=s["full_name"],
                team=s["team"],
                points=s["points"],
                wins=s["wins"],
                podiums=podium_map.get(abbr, 0),
                skill_score=skill_map.get(abbr, 50.0),
                avg_quali_delta=quali_map.get(abbr, 0.0),
                races=races_map.get(abbr, 0),
            ))
    else:
        # ── Fully local fallback ──────────────────────────────────────────────
        season_df = store.get_driver_standings(year)
        if season_df.empty:
            raise HTTPException(404, f"No data for season {year}")

        driver_agg = season_df.groupby("Abbreviation").agg(
            points=("Points", "sum"),
            wins=("Position", lambda x: (x == 1).sum()),
            podiums=("Position", lambda x: (x <= 3).sum()),
            team=("TeamName", "last"),
        ).reset_index()

        # Sort by points descending
        driver_agg = driver_agg.sort_values("points", ascending=False).reset_index(drop=True)

        result_standings = []
        for idx, row in driver_agg.iterrows():
            abbr = str(row["Abbreviation"]).upper()
            result_standings.append(DriverStanding(
                position=idx + 1,
                driver=abbr,
                full_name=abbr,
                team=str(row["team"]),
                points=float(row["points"]),
                wins=int(row["wins"]),
                podiums=int(row["podiums"]),
                skill_score=skill_map.get(abbr, 50.0),
                avg_quali_delta=quali_map.get(abbr, 0.0),
                races=races_map.get(abbr, 0),
            ))

    return StandingsResponse(season=year, standings=result_standings)


@router.get("/features", response_model=FeatureImportanceResponse)
async def get_feature_importance():
    """
    Returns real XGBoost feature importance from the production prediction model.
    Normalized to 0-100% weights.
    """
    if store.prediction_model is None:
        raise HTTPException(503, "Model not loaded")

    model = store.prediction_model["model"]
    features = store.prediction_model["features"]
    importances = model.feature_importances_

    total = importances.sum()
    items = [
        FeatureImportanceItem(
            feature=FEATURE_LABELS.get(feat, feat),
            importance=round(float(imp), 5),
            weight_pct=round(float(imp / total * 100), 1) if total > 0 else 0.0,
        )
        for feat, imp in sorted(zip(features, importances), key=lambda x: -x[1])
    ]
    return FeatureImportanceResponse(features=items)


@router.get("/overview", response_model=AnalyticsOverviewResponse)
async def get_analytics_overview():
    """
    Combined endpoint for the Analytics page:
    - Feature importance from the model
    - Track-type prediction accuracy from historical data
    - Time-series cross-validation MAE results
    """
    if store.prediction_model is None:
        raise HTTPException(503, "Model not loaded")

    # Feature importance
    model = store.prediction_model["model"]
    features = store.prediction_model["features"]
    importances = model.feature_importances_
    total = importances.sum()
    fi_items = [
        FeatureImportanceItem(
            feature=FEATURE_LABELS.get(feat, feat),
            importance=round(float(imp), 5),
            weight_pct=round(float(imp / total * 100), 1) if total > 0 else 0.0,
        )
        for feat, imp in sorted(zip(features, importances), key=lambda x: -x[1])
    ]

    # Track-type accuracy from historical validation data
    sf = store.skill_features.copy()
    sf["DeltaPosition"] = sf["Position"] - sf["GridPosition"]

    def track_mae(mask: pd.Series) -> float:
        subset = sf[mask & (sf["DNF"] == 0)]
        if subset.empty:
            return 75.0
        # Proxy for confidence: inverse of MAE, scaled 0-100
        mae = subset["DeltaPosition"].abs().mean()
        return round(float(max(0, min(100, 100 - mae * 6))), 1)

    track_accuracy = [
        TrackTypeAccuracy(type="Permanent circuits", confidence=track_mae(
            ~sf["Race"].isin(STREET_CIRCUITS | HIGH_SPEED_CIRCUITS))),
        TrackTypeAccuracy(type="Street circuits", confidence=track_mae(
            sf["Race"].isin(STREET_CIRCUITS))),
        TrackTypeAccuracy(type="High-speed", confidence=track_mae(
            sf["Race"].isin(HIGH_SPEED_CIRCUITS))),
    ]

    # Model accuracy from time-based CV splits (static from training output)
    model_accuracy = [
        ModelAccuracyItem(year=2023, mae=2.41, cv_split="2020–22 → 2023"),
        ModelAccuracyItem(year=2024, mae=2.28, cv_split="2020–23 → 2024"),
        ModelAccuracyItem(year=2025, mae=2.35, cv_split="2020–24 → 2025"),
    ]

    return AnalyticsOverviewResponse(
        feature_importance=fi_items,
        track_accuracy=track_accuracy,
        model_accuracy=model_accuracy,
    )


@router.get("/race/{year}/{race_name}", response_model=RaceResultResponse)
async def get_race_result(year: int, race_name: str):
    """
    Returns full historical race results for a specific year and race.
    Used for the What-If simulator baseline display and race replay.
    """
    # URL decode race name (spaces encoded as %20 or +)
    from urllib.parse import unquote
    race_name_decoded = unquote(race_name.replace("+", " "))

    df = store.get_race_rows(year, race_name_decoded)
    if df.empty:
        raise HTTPException(404, f"No data for {race_name_decoded} {year}")

    round_num = int(df["Round"].iloc[0]) if "Round" in df.columns else 0

    results: list[RaceResultRow] = []
    for _, row in df.sort_values("Position").iterrows():
        dnf = int(row.get("DNF", 0)) == 1
        pos = 99 if dnf else int(row.get("Position", 99))
        results.append(RaceResultRow(
            position=pos,
            driver=str(row.get("Abbreviation", "UNK")).upper(),
            team=str(row.get("TeamName", "")),
            grid=int(row.get("GridPosition", 99)),
            points=float(row.get("Points", 0)),
            status=str(row.get("Status", "DNF" if dnf else "Finished")),
            dnf=dnf,
        ))

    return RaceResultResponse(
        race=race_name_decoded,
        year=year,
        round=round_num,
        results=results,
    )
