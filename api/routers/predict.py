"""
routers/predict.py — POST /api/predict
Runs the production prediction model with Monte Carlo simulation for an upcoming race.
Accepts user-provided grid positions and enriches them with historical rolling features.
"""
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from api.schemas.predict import PredictRequest, PredictResponse, DriverResult
from api.services.loader import store
from api.services.enricher import build_race_dataframe_for_prediction

router = APIRouter(prefix="/api/predict", tags=["predict"])


def _extract_contextual_noise(grid_array: np.ndarray) -> np.ndarray:
    """
    Grid-aware Monte Carlo noise — mirrors src/model.py logic.
    Front runners: low variance. Midfield: chaotic. Backmarkers: moderate.
    """
    scale_noise = np.zeros(len(grid_array))
    scale_noise[grid_array <= 5] = 0.3
    scale_noise[(grid_array > 5) & (grid_array <= 12)] = 0.8
    scale_noise[grid_array > 12] = 0.5
    return np.random.normal(loc=0.1, scale=scale_noise)


def _run_monte_carlo(
    model_dict: dict,
    race_df: pd.DataFrame,
    runs: int,
) -> np.ndarray:
    """
    Runs N Monte Carlo iterations. Returns aggregate_matrix (drivers × runs).
    """
    model = model_dict["model"]
    features = model_dict["features"]

    base_deltas = model.predict(race_df[features])
    grids = race_df["GridPosition"].values
    dnf_probs = race_df["DNF_Probability"].fillna(0.0).values

    mc_results = []
    for _ in range(runs):
        noisy_deltas = base_deltas + _extract_contextual_noise(grids)
        raw_dist = grids + noisy_deltas
        crashes = np.random.random(len(raw_dist)) < (dnf_probs * 0.5)
        raw_dist[crashes] += 99
        ordered = pd.Series(raw_dist).rank(method="first").values
        mc_results.append(ordered)

    return np.vstack(mc_results).T  # shape: (n_drivers, runs)


def _trend_from_avg(avg_last3: float, avg_last5: float) -> str:
    """Derive trend label from rolling finish averages."""
    if avg_last3 < avg_last5 - 0.5:
        return "up"
    elif avg_last3 > avg_last5 + 0.5:
        return "down"
    return "steady"


@router.post("", response_model=PredictResponse)
async def predict_race(req: PredictRequest):
    """
    Run the Apex prediction model for an upcoming race.

    The frontend provides driver codes + grid positions.
    The API enriches each driver with their latest historical rolling features
    (AvgFinish_Last3, DNF_Probability, SkillScore, etc.) and runs Monte Carlo
    simulation to produce probabilistic race outcomes.
    """
    if store.prediction_model is None:
        raise HTTPException(503, "Models not loaded yet. Please retry in a few seconds.")

    # Build enriched feature DataFrame
    grid_dicts = [e.model_dump() for e in req.grid]
    race_df = build_race_dataframe_for_prediction(grid_dicts, req.race, req.year)

    if race_df.empty:
        raise HTTPException(400, "Could not build feature rows. Check driver abbreviations.")

    # Run Monte Carlo
    aggregate_matrix = _run_monte_carlo(store.prediction_model, race_df, req.mc_runs)

    # Build results
    results: list[DriverResult] = []
    for i in range(len(race_df)):
        row = race_df.iloc[i]
        abbr = str(row.get("Abbreviation", f"D{i+1}")).upper()
        driver_pos_array = aggregate_matrix[i]

        median_pos = int(np.median(driver_pos_array))
        p25 = int(np.percentile(driver_pos_array, 25))
        p75 = int(np.percentile(driver_pos_array, 75))
        win_pct = float(np.mean(driver_pos_array <= 1) * 100)
        podium_pct = float(np.mean(driver_pos_array <= 3) * 100)
        top10_pct = float(np.mean(driver_pos_array <= 10) * 100)
        confidence = float(max(0, min(100, 100 - (np.std(driver_pos_array) * 10))))
        expected_range = f"P{p25}-P{p75}" if p25 != p75 else f"P{p25}"

        avg3 = float(row.get("AvgFinish_Last3", 10.0))
        avg5 = float(row.get("AvgFinish_Last5", 10.0))
        trend = _trend_from_avg(avg3, avg5)

        results.append(DriverResult(
            rank=median_pos,
            driver=abbr,
            grid=int(row["GridPosition"]),
            median_position=median_pos,
            expected_range=expected_range,
            win_probability=round(win_pct, 1),
            podium_probability=round(podium_pct, 1),
            top10_probability=round(top10_pct, 1),
            confidence=round(confidence, 1),
            trend=trend,
        ))

    # Sort by median predicted position
    results.sort(key=lambda x: x.median_position)
    for idx, r in enumerate(results):
        r.rank = idx + 1

    # Overall model confidence = mean driver confidence, weighted toward top 5
    top5_conf = [r.confidence for r in results[:5]]
    overall_conf = round(float(np.mean(top5_conf)) / 100, 3) if top5_conf else 0.82

    return PredictResponse(
        race=req.race,
        year=req.year,
        confidence=overall_conf,
        mc_runs=req.mc_runs,
        results=results,
    )
