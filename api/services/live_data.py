"""
services/live_data.py — Fetches live F1 data from OpenF1 and Jolpica-F1 APIs.
Both APIs are free, open-source, and require no authentication.

  OpenF1:    https://openf1.org          (real-time telemetry, qualifying positions)
  Jolpica:   https://api.jolpi.ca/ergast (race schedule, post-qualifying results, standings)
"""
import httpx
from datetime import date, datetime, timezone
from typing import Optional

OPENF1_BASE = "https://api.openf1.org/v1"
JOLPICA_BASE = "https://api.jolpi.ca/ergast/f1"

# Shared async client (reuse connections)
_client = httpx.AsyncClient(timeout=10.0)


# ── OpenF1 ──────────────────────────────────────────────────────────────────

async def get_openf1_qualifying_positions(
    year: int,
    circuit_short_name: str,
) -> Optional[list[dict]]:
    """
    Fetches qualifying grid positions from OpenF1 for the given year and circuit.
    Returns a list of dicts: [{"driver_number": 1, "abbreviation": "VER", "position": 1, ...}]
    or None if no qualifying session is found (between race weekends).
    """
    try:
        # Step 1: find the qualifying session key
        session_url = f"{OPENF1_BASE}/sessions"
        params = {
            "year": year,
            "session_name": "Qualifying",
            "circuit_short_name": circuit_short_name,
        }
        r = await _client.get(session_url, params=params)
        r.raise_for_status()
        sessions = r.json()
        if not sessions:
            return None

        session_key = sessions[-1]["session_key"]

        # Step 2: get positions for that session
        pos_url = f"{OPENF1_BASE}/position"
        pos_r = await _client.get(pos_url, params={"session_key": session_key})
        pos_r.raise_for_status()
        positions = pos_r.json()
        if not positions:
            return None

        # Collapse to final position per driver (last entry per driver number)
        by_driver: dict[int, dict] = {}
        for row in positions:
            dn = row.get("driver_number")
            if dn is not None:
                by_driver[dn] = row

        # Step 3: fetch driver info to get abbreviations
        drv_url = f"{OPENF1_BASE}/drivers"
        drv_r = await _client.get(drv_url, params={"session_key": session_key})
        drv_r.raise_for_status()
        drivers_info = {d["driver_number"]: d for d in drv_r.json()}

        result = []
        for dn, pos_row in by_driver.items():
            drv = drivers_info.get(dn, {})
            result.append({
                "driver_number": dn,
                "abbreviation": drv.get("name_acronym", "UNK"),
                "full_name": drv.get("full_name", ""),
                "team_name": drv.get("team_name", ""),
                "position": pos_row.get("position"),
            })

        result.sort(key=lambda x: x["position"] or 99)
        return result

    except Exception as e:
        print(f"[live_data] OpenF1 error: {e}")
        return None


# ── Jolpica-F1 (Ergast successor) ───────────────────────────────────────────

async def get_jolpica_schedule(year: int) -> Optional[list[dict]]:
    """
    Fetches the full race schedule for a given season.
    Returns list of race dicts with name, date, round, circuit etc.
    """
    try:
        url = f"{JOLPICA_BASE}/{year}.json"
        r = await _client.get(url)
        r.raise_for_status()
        data = r.json()
        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        result = []
        for race in races:
            result.append({
                "round": int(race.get("round", 0)),
                "name": race.get("raceName", ""),
                "circuit": race.get("Circuit", {}).get("circuitName", ""),
                "circuit_id": race.get("Circuit", {}).get("circuitId", ""),
                "country": race.get("Circuit", {}).get("Location", {}).get("country", ""),
                "date": race.get("date", ""),
                "time": race.get("time", ""),
            })
        return result
    except Exception as e:
        print(f"[live_data] Jolpica schedule error: {e}")
        return None


async def get_jolpica_qualifying(year: int, round_num: int) -> Optional[list[dict]]:
    """
    Fetches official qualifying results for a specific race round.
    Returns list: [{"position": 1, "abbreviation": "VER", "team": "...", "q3": "1:11.318"}]
    """
    try:
        url = f"{JOLPICA_BASE}/{year}/{round_num}/qualifying.json"
        r = await _client.get(url)
        r.raise_for_status()
        data = r.json()
        results = (
            data.get("MRData", {})
            .get("RaceTable", {})
            .get("Races", [{}])[0]
            .get("QualifyingResults", [])
        )
        return [
            {
                "position": int(res.get("position", 99)),
                "abbreviation": res.get("Driver", {}).get("code", "UNK"),
                "full_name": f"{res['Driver'].get('givenName','')} {res['Driver'].get('familyName','')}".strip(),
                "team": res.get("Constructor", {}).get("name", ""),
                "q1": res.get("Q1", ""),
                "q2": res.get("Q2", ""),
                "q3": res.get("Q3", ""),
            }
            for res in results
        ]
    except Exception as e:
        print(f"[live_data] Jolpica qualifying error: {e}")
        return None


async def get_jolpica_driver_standings(year: int) -> Optional[list[dict]]:
    """
    Fetches current driver championship standings for a season.
    """
    try:
        url = f"{JOLPICA_BASE}/{year}/driverStandings.json"
        r = await _client.get(url)
        r.raise_for_status()
        data = r.json()
        standings_list = (
            data.get("MRData", {})
            .get("StandingsTable", {})
            .get("StandingsLists", [{}])[0]
            .get("DriverStandings", [])
        )
        return [
            {
                "position": int(s.get("position", 99)),
                "abbreviation": s.get("Driver", {}).get("code", "UNK"),
                "full_name": f"{s['Driver'].get('givenName','')} {s['Driver'].get('familyName','')}".strip(),
                "team": s.get("Constructors", [{}])[0].get("name", ""),
                "points": float(s.get("points", 0)),
                "wins": int(s.get("wins", 0)),
            }
            for s in standings_list
        ]
    except Exception as e:
        print(f"[live_data] Jolpica standings error: {e}")
        return None


async def get_next_race(year: int) -> Optional[dict]:
    """
    Returns the next upcoming race in the season (first race with date >= today).
    """
    schedule = await get_jolpica_schedule(year)
    if not schedule:
        return None
    today = date.today().isoformat()
    upcoming = [r for r in schedule if r["date"] >= today]
    return upcoming[0] if upcoming else schedule[-1]
