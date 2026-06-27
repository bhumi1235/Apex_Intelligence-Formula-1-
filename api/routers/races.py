"""
routers/races.py — GET /api/races
Returns the upcoming race (from Jolpica-F1 live data) and list of historical
races available for simulation (from the local processed dataset).
Falls back to data/races.json if the live API is unavailable.
"""
import json
import os
from fastapi import APIRouter
from api.services import live_data
from api.services.loader import store

router = APIRouter(prefix="/api/races", tags=["races"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RACES_JSON = os.path.join(BASE_DIR, "data", "races.json")

# Curated circuit info not available from Jolpica
CIRCUIT_META: dict[str, dict] = {
    "Monaco Grand Prix":           {"laps": 78,  "lengthKm": 3.337, "cornerCount": 19, "lapRecord": "1:12.909"},
    "British Grand Prix":          {"laps": 52,  "lengthKm": 5.891, "cornerCount": 18, "lapRecord": "1:27.097"},
    "Belgian Grand Prix":          {"laps": 44,  "lengthKm": 7.004, "cornerCount": 19, "lapRecord": "1:46.286"},
    "Italian Grand Prix":          {"laps": 53,  "lengthKm": 5.793, "cornerCount": 11, "lapRecord": "1:21.046"},
    "Spanish Grand Prix":          {"laps": 66,  "lengthKm": 4.657, "cornerCount": 16, "lapRecord": "1:16.330"},
    "Canadian Grand Prix":         {"laps": 70,  "lengthKm": 4.361, "cornerCount": 14, "lapRecord": "1:13.078"},
    "Austrian Grand Prix":         {"laps": 71,  "lengthKm": 4.318, "cornerCount": 10, "lapRecord": "1:05.619"},
    "Hungarian Grand Prix":        {"laps": 70,  "lengthKm": 4.381, "cornerCount": 14, "lapRecord": "1:16.627"},
    "Dutch Grand Prix":            {"laps": 72,  "lengthKm": 4.259, "cornerCount": 14, "lapRecord": "1:11.097"},
    "Singapore Grand Prix":        {"laps": 62,  "lengthKm": 5.063, "cornerCount": 23, "lapRecord": "1:35.867"},
    "Japanese Grand Prix":         {"laps": 53,  "lengthKm": 5.807, "cornerCount": 18, "lapRecord": "1:30.983"},
    "United States Grand Prix":    {"laps": 56,  "lengthKm": 5.513, "cornerCount": 20, "lapRecord": "1:36.169"},
    "Mexico City Grand Prix":      {"laps": 71,  "lengthKm": 4.304, "cornerCount": 17, "lapRecord": "1:17.774"},
    "São Paulo Grand Prix":        {"laps": 69,  "lengthKm": 4.309, "cornerCount": 15, "lapRecord": "1:10.540"},
    "Las Vegas Grand Prix":        {"laps": 50,  "lengthKm": 6.201, "cornerCount": 17, "lapRecord": "1:34.876"},
    "Abu Dhabi Grand Prix":        {"laps": 58,  "lengthKm": 5.281, "cornerCount": 16, "lapRecord": "1:26.103"},
    "Azerbaijan Grand Prix":       {"laps": 51,  "lengthKm": 6.003, "cornerCount": 20, "lapRecord": "1:43.009"},
    "Bahrain Grand Prix":          {"laps": 57,  "lengthKm": 5.412, "cornerCount": 15, "lapRecord": "1:31.447"},
    "Saudi Arabian Grand Prix":    {"laps": 50,  "lengthKm": 6.174, "cornerCount": 27, "lapRecord": "1:30.734"},
    "Miami Grand Prix":            {"laps": 57,  "lengthKm": 5.412, "cornerCount": 19, "lapRecord": "1:29.708"},
    "Emilia Romagna Grand Prix":   {"laps": 63,  "lengthKm": 4.909, "cornerCount": 19, "lapRecord": "1:15.484"},
    "Qatar Grand Prix":            {"laps": 57,  "lengthKm": 5.380, "cornerCount": 16, "lapRecord": "1:24.319"},
    "Australian Grand Prix":       {"laps": 58,  "lengthKm": 5.278, "cornerCount": 16, "lapRecord": "1:20.235"},
    "Chinese Grand Prix":          {"laps": 56,  "lengthKm": 5.451, "cornerCount": 16, "lapRecord": "1:32.238"},
}


@router.get("")
async def get_races():
    """
    Returns:
    - upcoming: next race details (live from Jolpica-F1, falls back to races.json)
    - historical: all races available for What-If simulation (from local dataset)
    """
    # ── Upcoming race (try live first) ────────────────────────────────────────
    upcoming = None
    next_race_live = await live_data.get_next_race(2026)

    if next_race_live:
        meta = CIRCUIT_META.get(next_race_live["name"], {})
        upcoming = {
            "round": next_race_live["round"],
            "name": next_race_live["name"],
            "circuit": next_race_live.get("circuit", ""),
            "country": next_race_live.get("country", ""),
            "date": next_race_live["date"],
            "laps": meta.get("laps", 57),
            "lengthKm": meta.get("lengthKm", 5.0),
            "cornerCount": meta.get("cornerCount", 15),
            "lapRecord": meta.get("lapRecord", "N/A"),
            "confidence": 0.82,  # base model confidence; updated per prediction run
            "source": "live",
        }
    else:
        # Fallback: races.json
        try:
            with open(RACES_JSON) as f:
                fallback = json.load(f)
            first = fallback["races"][0] if fallback.get("races") else {}
            meta = CIRCUIT_META.get(first.get("name", ""), {})
            upcoming = {
                "round": int(first.get("round", 1)),
                "name": first.get("name", "Unknown Grand Prix"),
                "circuit": "",
                "country": "",
                "date": first.get("date", "2026-01-01"),
                "laps": meta.get("laps", 57),
                "lengthKm": meta.get("lengthKm", 5.0),
                "cornerCount": meta.get("cornerCount", 15),
                "lapRecord": meta.get("lapRecord", "N/A"),
                "confidence": float({"high": 0.85, "medium": 0.72, "low": 0.60}.get(
                    first.get("confidence", "medium"), 0.72
                )),
                "source": "fallback",
            }
        except Exception:
            upcoming = None

    # ── Historical races from local dataset ───────────────────────────────────
    historical = store.get_historical_races()

    return {
        "upcoming": upcoming,
        "historical": historical,
    }
