"""
routers/drivers.py — GET /api/drivers
Returns the 2026 driver roster (from data/drivers.json enriched with skill scores)
and all historical driver abbreviations for simulator dropdowns.
"""
import json
import os
from fastapi import APIRouter
from api.services.loader import store

router = APIRouter(prefix="/api/drivers", tags=["drivers"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DRIVERS_JSON = os.path.join(BASE_DIR, "data", "drivers.json")

# Mapping from full names in drivers.json → abbreviation used in model CSV
NAME_TO_ABBR: dict[str, str] = {
    "Max Verstappen":     "VER",
    "Charles Leclerc":   "LEC",
    "Lando Norris":      "NOR",
    "George Russell":    "RUS",
    "Lewis Hamilton":    "HAM",
    "Oscar Piastri":     "PIA",
    "Carlos Sainz":      "SAI",
    "Fernando Alonso":   "ALO",
    "Lance Stroll":      "STR",
    "Pierre Gasly":      "GAS",
    "Jack Doohan":       "DOO",
    "Alexander Albon":   "ALB",
    "Yuki Tsunoda":      "TSU",
    "Liam Lawson":       "LAW",
    "Nico Hülkenberg":   "HUL",
    "Gabriel Bortoleto": "BOR",
    "Esteban Ocon":      "OCO",
    "Oliver Bearman":    "BEA",
    "Andrea Kimi Antonelli": "ANT",
    "Isack Hadjar":      "HAD",
}


@router.get("")
async def get_drivers():
    """
    Returns:
    - current: 2026 driver roster with team info and latest Apex skill scores
    - historical_abbr: all driver abbreviations in the historical dataset (for simulator dropdowns)
    """
    # ── Current roster from drivers.json ─────────────────────────────────────
    try:
        with open(DRIVERS_JSON) as f:
            raw = json.load(f)
        drivers_raw = raw.get("drivers", [])
    except Exception:
        drivers_raw = []

    # Latest skill scores (2025)
    skill_df = store.get_skill_scores(2025)
    skill_map: dict[str, float] = {}
    quali_map: dict[str, float] = {}
    if not skill_df.empty:
        for _, row in skill_df.iterrows():
            abbr = str(row.get("Abbreviation", "")).upper()
            skill_map[abbr] = round(float(row.get("SkillScore", 50.0)), 1)
            quali_map[abbr] = round(float(row.get("AvgQualiDelta", 0.0)), 3)

    current = []
    for d in drivers_raw:
        name = d.get("name", "")
        abbr = NAME_TO_ABBR.get(name, name[:3].upper())
        current.append({
            "name": name,
            "abbreviation": abbr,
            "team": d.get("team", ""),
            "teamColor": d.get("teamColor", "#ffffff"),
            "skillScore": skill_map.get(abbr, 50.0),
            "avgQualiDelta": quali_map.get(abbr, 0.0),
        })

    # ── Historical abbreviations from dataset ─────────────────────────────────
    historical_abbr = sorted(
        store.skill_features["Abbreviation"].unique().tolist()
    )

    return {
        "current": current,
        "historical_abbr": historical_abbr,
    }
