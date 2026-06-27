"""
services/loader.py — Singleton loader for all ML artifacts and processed datasets.
Loaded ONCE at FastAPI startup via lifespan; injected into routers via app.state.
"""
import os
import joblib
import pandas as pd
from typing import Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED = os.path.join(BASE_DIR, "data", "processed")


class ModelStore:
    """
    Holds all loaded artifacts so they are never re-read from disk per request.
    """
    def __init__(self):
        self.prediction_model: dict[str, Any] | None = None   # {"model": XGB, "features": [...]}
        self.simulation_model: dict[str, Any] | None = None
        self.skill_features: pd.DataFrame | None = None       # driver_skill_features.csv
        self.skill_scores: pd.DataFrame | None = None         # driver_skill.csv
        self.full_dataset: pd.DataFrame | None = None         # full_dataset.csv

    def load(self):
        """Load everything from disk. Called once during FastAPI lifespan startup."""
        print("[loader] Loading prediction model...")
        self.prediction_model = joblib.load(os.path.join(PROCESSED, "prediction_model.pkl"))

        print("[loader] Loading simulation model...")
        self.simulation_model = joblib.load(os.path.join(PROCESSED, "simulation_model.pkl"))

        print("[loader] Loading driver skill features CSV...")
        self.skill_features = pd.read_csv(os.path.join(PROCESSED, "driver_skill_features.csv"))

        print("[loader] Loading driver skill scores CSV...")
        self.skill_scores = pd.read_csv(os.path.join(PROCESSED, "driver_skill.csv"))

        print("[loader] Loading full dataset CSV...")
        self.full_dataset = pd.read_csv(os.path.join(PROCESSED, "full_dataset.csv"))

        print("[loader] [OK] All artifacts loaded.")

    # ── Convenience accessors ───────────────────────────────────────────────────

    def get_latest_driver_row(self, abbreviation: str) -> pd.Series | None:
        """
        Returns the most recent skill_features row for a driver (last 2025 race).
        Used by enricher.py to seed rolling features for upcoming predictions.
        """
        df = self.skill_features
        driver_df = df[df["Abbreviation"] == abbreviation.upper()].copy()
        if driver_df.empty:
            return None
        # Sort by Year then Round, take last
        driver_df = driver_df.sort_values(["Year", "Round"])
        return driver_df.iloc[-1]

    def get_race_rows(self, year: int, race: str) -> pd.DataFrame:
        """
        Returns all rows for a specific year+race from the feature dataset.
        Used by the simulation router.
        """
        df = self.skill_features
        mask = (df["Year"] == year) & (df["Race"] == race)
        return df[mask].copy()

    def get_historical_races(self) -> list[dict]:
        """Returns unique year+race combinations available for simulation."""
        df = self.full_dataset[["Year", "Race", "Round"]].drop_duplicates()
        df = df.sort_values(["Year", "Round"])
        return [
            {"id": f"{row['Race']}-{row['Year']}", "name": row["Race"], "year": int(row["Year"]), "round": int(row["Round"])}
            for _, row in df.iterrows()
        ]

    def get_driver_standings(self, year: int) -> pd.DataFrame:
        """
        Returns per-driver aggregated stats for a given season from the full dataset.
        """
        df = self.full_dataset[self.full_dataset["Year"] == year].copy()
        return df

    def get_skill_scores(self, year: int) -> pd.DataFrame:
        """Returns skill scores for a given year."""
        return self.skill_scores[self.skill_scores["Year"] == year].copy()


# Global singleton — assigned during lifespan startup
store = ModelStore()
