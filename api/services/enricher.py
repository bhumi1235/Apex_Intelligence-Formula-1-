"""
services/enricher.py — Builds complete feature rows for the ML models.

For PREDICTION (upcoming race): takes user-provided grid position + quali gap and
fills in all rolling/contextual features from the most recent driver data in the CSV.

For SIMULATION (historical): looks up the actual row from driver_skill_features.csv
and optionally overrides grid position.
"""
import numpy as np
import pandas as pd
from typing import Optional
from api.services.loader import store


# The exact feature set the production models expect (from model.py INITIAL_FEATURES, pruned)
MODEL_FEATURES = [
    "GridPosition",
    "Grid_x_Skill",
    "DriverPointsPercentile",
    "TeamPointsPercentile",
    "TeamCategory",
    "ConstructorGapPct",
    "Form_x_Team",
    "AvgFinish_Last5",
    "GridQualiInteraction",
    "AvgFinish_Last3",
    "QualiGapToPole",
    "DNF_Probability",
]

# Street circuits (from features.py)
STREET_CIRCUITS = {
    "Monaco Grand Prix",
    "Azerbaijan Grand Prix",
    "Singapore Grand Prix",
    "Saudi Arabian Grand Prix",
    "Miami Grand Prix",
    "Las Vegas Grand Prix",
    "Abu Dhabi Grand Prix",
}


def build_prediction_row(
    abbreviation: str,
    grid_position: int,
    quali_gap_to_pole: float,
    race_name: str,
    year: int,
) -> Optional[dict]:
    """
    Builds a single feature row for the prediction model using:
    - User-provided: grid_position, quali_gap_to_pole
    - Historical rolling: pulled from the driver's most recent CSV row
    Returns a dict of {feature: value} for all MODEL_FEATURES, plus metadata.
    Returns None if the driver has no historical data at all.
    """
    latest = store.get_latest_driver_row(abbreviation)

    if latest is None:
        # Unknown driver — use neutral defaults
        avg_finish_last3 = 10.0
        avg_finish_last5 = 10.0
        dnf_prob = 0.1
        skill_score = 50.0
        driver_points_pct = 0.5
        team_points_pct = 0.5
        team_category = 2.0
        constructor_gap_pct = 0.5
    else:
        avg_finish_last3 = float(latest.get("AvgFinish_Last3", 10.0) or 10.0)
        avg_finish_last5 = float(latest.get("AvgFinish_Last5", 10.0) or 10.0)
        dnf_prob = float(latest.get("DNF_Probability", 0.1) or 0.1)
        skill_score = float(latest.get("SkillScore", 50.0) or 50.0)
        driver_points_pct = float(latest.get("DriverPointsPercentile", 0.5) or 0.5)
        team_points_pct = float(latest.get("TeamPointsPercentile", 0.5) or 0.5)
        team_category = float(latest.get("TeamCategory", 2.0) or 2.0)
        constructor_gap_pct = float(latest.get("ConstructorGapPct", 0.5) or 0.5)

    # Derived interaction features
    grid_x_skill = grid_position * skill_score
    quali_interaction = grid_position * quali_gap_to_pole
    form_x_team = avg_finish_last3 * team_category

    return {
        "Abbreviation": abbreviation.upper(),
        "GridPosition": float(grid_position),
        "QualiGapToPole": quali_gap_to_pole,
        "AvgFinish_Last3": avg_finish_last3,
        "AvgFinish_Last5": avg_finish_last5,
        "DNF_Probability": dnf_prob,
        "SkillScore": skill_score,
        "DriverPointsPercentile": driver_points_pct,
        "TeamPointsPercentile": team_points_pct,
        "TeamCategory": team_category,
        "ConstructorGapPct": constructor_gap_pct,
        "GridQualiInteraction": quali_interaction,
        "Grid_x_Skill": grid_x_skill,
        "Form_x_Team": form_x_team,
        "IsStreetCircuit": int(race_name in STREET_CIRCUITS),
    }


def build_race_dataframe_for_prediction(
    grid: list[dict],  # [{"abbreviation": "VER", "grid_position": 1, "quali_gap_to_pole": 0.0}]
    race_name: str,
    year: int,
) -> pd.DataFrame:
    """
    Builds the full feature DataFrame for a prediction run.
    Enriches each driver entry with historical rolling features.
    """
    rows = []
    for entry in grid:
        abbr = entry["abbreviation"]
        gpos = entry["grid_position"]
        gap = entry.get("quali_gap_to_pole", 0.0)

        row = build_prediction_row(abbr, gpos, gap, race_name, year)
        if row is None:
            continue
        rows.append(row)

    df = pd.DataFrame(rows)
    # Ensure all model features present; fill any remaining NaNs with sensible defaults
    for feat in MODEL_FEATURES:
        if feat not in df.columns:
            df[feat] = 0.0
        df[feat] = pd.to_numeric(df[feat], errors="coerce").fillna(0.0)

    return df


def build_race_dataframe_for_simulation(
    race_name: str,
    year: int,
    overrides: Optional[list[dict]] = None,  # [{"abbreviation": "HAM", "grid_position": 1}]
) -> pd.DataFrame:
    """
    Fetches the actual historical race rows from driver_skill_features.csv
    and applies any grid position overrides requested by the user.
    """
    race_df = store.get_race_rows(year, race_name)

    if race_df.empty:
        raise ValueError(f"No data found for {race_name} {year}")

    # Apply overrides
    if overrides:
        override_map = {o["abbreviation"].upper(): o["grid_position"] for o in overrides}
        for abbr, new_grid in override_map.items():
            mask = race_df["Abbreviation"] == abbr
            if mask.any():
                race_df.loc[mask, "GridPosition"] = float(new_grid)
                # Recompute interaction features for overridden rows
                race_df.loc[mask, "Grid_x_Skill"] = (
                    float(new_grid) * race_df.loc[mask, "SkillScore"].fillna(50.0)
                )
                race_df.loc[mask, "GridQualiInteraction"] = (
                    float(new_grid) * race_df.loc[mask, "QualiGapToPole"].fillna(0.0)
                )
                race_df.loc[mask, "Form_x_Team"] = (
                    race_df.loc[mask, "AvgFinish_Last3"].fillna(10.0)
                    * race_df.loc[mask, "TeamCategory"].fillna(2.0)
                )

    # Ensure all model features present
    for feat in MODEL_FEATURES:
        if feat not in race_df.columns:
            race_df[feat] = 0.0
        race_df[feat] = pd.to_numeric(race_df[feat], errors="coerce").fillna(0.0)

    return race_df.reset_index(drop=True)
