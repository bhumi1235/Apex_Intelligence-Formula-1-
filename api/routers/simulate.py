"""
routers/simulate.py — POST /api/simulate
Historical What-If simulator. Loads actual race rows from driver_skill_features.csv,
applies user grid overrides, and runs Monte Carlo simulation.
"""
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from api.schemas.simulate import SimulateRequest, SimulateResponse, SimDriverResult
from api.services.loader import store
from api.services.enricher import build_race_dataframe_for_simulation

router = APIRouter(prefix="/api/simulate", tags=["simulate"])

# Weather variance multipliers for Monte Carlo noise (echoes simulator.ts logic)
WEATHER_VARIANCE: dict[str, float] = {
    "dry": 1.0,
    "mixed": 2.0,
    "wet": 3.5,
}


def _extract_contextual_noise(grid_array: np.ndarray, weather: str) -> np.ndarray:
    multiplier = WEATHER_VARIANCE.get(weather, 1.0)
    scale_noise = np.zeros(len(grid_array))
    scale_noise[grid_array <= 5] = 0.3 * multiplier
    scale_noise[(grid_array > 5) & (grid_array <= 12)] = 0.8 * multiplier
    scale_noise[grid_array > 12] = 0.5 * multiplier
    return np.random.normal(loc=0.1, scale=scale_noise)


def _run_monte_carlo(
    model_dict: dict,
    race_df: pd.DataFrame,
    runs: int,
    weather: str,
) -> np.ndarray:
    model = model_dict["model"]
    features = model_dict["features"]

    base_deltas = model.predict(race_df[features])
    grids = race_df["GridPosition"].values
    dnf_probs = race_df["DNF_Probability"].fillna(0.0).values

    # Wet weather amplifies DNF risk
    dnf_multiplier = {"dry": 0.5, "mixed": 1.0, "wet": 2.0}.get(weather, 0.5)

    mc_results = []
    for _ in range(runs):
        noisy_deltas = base_deltas + _extract_contextual_noise(grids, weather)
        raw_dist = grids + noisy_deltas
        crashes = np.random.random(len(raw_dist)) < (dnf_probs * dnf_multiplier)
        raw_dist[crashes] += 99
        ordered = pd.Series(raw_dist).rank(method="first").values
        mc_results.append(ordered)

    return np.vstack(mc_results).T  # shape: (n_drivers, runs)


@router.post("", response_model=SimulateResponse)
async def simulate_race(req: SimulateRequest):
    """
    Run a What-If Monte Carlo simulation on a historical race.

    Loads the actual race data for the given year+race from the feature dataset.
    Applies user-requested grid position overrides (e.g. HAM starts P1 instead of P5).
    Returns simulated finishing order with confidence bands and a chaos index
    measuring divergence from the actual historical result.
    """
    if store.simulation_model is None:
        raise HTTPException(503, "Models not loaded yet. Please retry in a few seconds.")

    overrides = [o.model_dump() for o in req.overrides] if req.overrides else []

    try:
        race_df = build_race_dataframe_for_simulation(req.race, req.year, overrides)
    except ValueError as e:
        raise HTTPException(404, str(e))

    if race_df.empty:
        raise HTTPException(404, f"No data found for {req.race} {req.year}")

    # Run Monte Carlo
    aggregate_matrix = _run_monte_carlo(
        store.simulation_model, race_df, req.mc_runs, req.weather
    )

    # Actual historical positions for delta calculation
    actual_positions: dict[str, int | None] = {}
    for _, row in race_df.iterrows():
        abbr = str(row.get("Abbreviation", "")).upper()
        dnf = int(row.get("DNF", 0))
        pos = None if dnf else int(row.get("Position", 99))
        actual_positions[abbr] = pos

    results: list[SimDriverResult] = []
    for i in range(len(race_df)):
        row = race_df.iloc[i]
        abbr = str(row.get("Abbreviation", f"D{i+1}")).upper()
        driver_pos_array = aggregate_matrix[i]

        median_pos = int(np.median(driver_pos_array))
        podium_pct = float(np.mean(driver_pos_array <= 3) * 100)
        top10_pct = float(np.mean(driver_pos_array <= 10) * 100)
        confidence = float(max(0, min(100, 100 - (np.std(driver_pos_array) * 10))))

        actual = actual_positions.get(abbr)
        delta = (actual - median_pos) if (actual is not None and median_pos < 90) else 0

        is_dnf = int(row.get("DNF", 0)) == 1
        results.append(SimDriverResult(
            driver=abbr,
            finish=None if is_dnf else median_pos,
            grid=int(row["GridPosition"]),
            actual_finish=actual,
            delta=delta,
            podium_pct=round(podium_pct, 1),
            top10_pct=round(top10_pct, 1),
            confidence=round(confidence, 1),
        ))

    # Sort by simulated finish (DNFs last)
    results.sort(key=lambda x: x.finish if x.finish is not None else 99)

    # Chaos index: total absolute delta across finishers, capped at 100
    total_delta = sum(abs(r.delta) for r in results if r.finish is not None)
    weather_bonus = {"dry": 0, "mixed": 9, "wet": 18}.get(req.weather, 0)
    chaos_index = min(100, int(total_delta * 4 + weather_bonus))

    return SimulateResponse(
        race=req.race,
        year=req.year,
        weather=req.weather,
        mc_runs=req.mc_runs,
        chaos_index=chaos_index,
        results=results,
    )
