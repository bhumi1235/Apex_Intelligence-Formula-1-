"""
features.py — Feature engineering pipeline for F1 race position prediction.
Consolidates all feature logic from notebooks 02 and 03.
"""
import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED = os.path.join(BASE_DIR, "data", "processed")

# Street / semi-street circuits
STREET_CIRCUITS = [
    "Monaco Grand Prix",
    "Azerbaijan Grand Prix",
    "Singapore Grand Prix",
    "Saudi Arabian Grand Prix",
    "Miami Grand Prix",
    "Las Vegas Grand Prix",
    "Abu Dhabi Grand Prix",
]

# The generalized features used by the models and simulator to prevent exact tracking
MODEL_FEATURES = [
    "GridPosition",
    "QualiGapToPole",
    "AvgFinish_Last3",
    "AvgFinish_Last5",
    "DNF_Probability",
    "SkillScore",
    "TeamPointsPercentile",
    "DriverPointsPercentile",
    "ConstructorGapPct",
    "TeamCategory",
    "GridQualiInteraction",
    "AvgQualiDelta",
    "IsStreetCircuit",
    "TrackCode",
    "Grid_x_Skill",
    "Form_x_Team"
]


def add_rolling_features(df):
    """Add rolling average finish and DNF rate features (shifted to avoid leakage)."""
    df = df.sort_values(["Abbreviation", "Year", "Round"]).copy()

    df["AvgFinish_Last3"] = (
        df.groupby("Abbreviation")["Position"]
        .transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    )

    df["AvgFinish_Last5"] = (
        df.groupby("Abbreviation")["Position"]
        .transform(lambda x: x.shift(1).rolling(5, min_periods=1).mean())
    )

    df["DNF_Probability"] = (
        df.groupby("Abbreviation")["DNF"]
        .transform(lambda x: x.shift(1).rolling(5, min_periods=1).mean())
    )

    return df


def add_cumulative_points(df):
    """Add season-cumulative driver and team points (shifted to avoid leakage)."""
    df = df.sort_values(["Abbreviation", "Year", "Round"]).copy()

    df["SeasonPointsSoFar"] = (
        df.groupby(["Abbreviation", "Year"])["Points"]
        .transform(lambda x: x.shift(1).cumsum().fillna(0))
    )

    df["TeamSeasonPoints"] = (
        df.groupby(["TeamName", "Year"])["Points"]
        .transform(lambda x: x.shift(1).cumsum().fillna(0))
    )

    return df


def add_team_context(df):
    """Add team median position and driver-vs-team delta."""
    team_avg = (
        df.groupby(["Year", "Race", "TeamName"])["Position"]
        .median()
        .reset_index()
    )
    team_avg.columns = ["Year", "Race", "TeamName", "TeamMedianPosition"]

    df = df.merge(team_avg, on=["Year", "Race", "TeamName"], how="left")
    df["DriverVsTeamDelta"] = df["TeamMedianPosition"] - df["Position"]

    return df


def add_derived_features(df):
    """Add grid-to-finish delta, normalized position, street circuit flag, etc."""
    df["GridToFinishDelta"] = df["GridPosition"] - df["Position"]

    df["NormalizedPosition"] = df.groupby(["Year", "Race"])["Position"].transform(
        lambda x: (x - x.min()) / (x.max() - x.min()) if x.max() > x.min() else 0
    )

    df["IsStreetCircuit"] = df["Race"].isin(STREET_CIRCUITS).astype(int)

    # Track Code mapping
    df["TrackCode"] = df["Race"].astype("category").cat.codes

    # Constructor championship gap as a strict percentage of the leader's points
    df["ConstructorGapPct"] = df.groupby(["Year", "Race"])["TeamSeasonPoints"].transform(
        lambda x: (x.max() - x) / max(x.max(), 1.0)
    )

    # Driver championship percentile (smooth distribution)
    df["DriverPointsPercentile"] = df.groupby(["Year", "Race"])["SeasonPointsSoFar"].rank(
        pct=True
    )
    
    # Team championship percentile
    df["TeamPointsPercentile"] = df.groupby(["Year", "Race"])["TeamSeasonPoints"].rank(
        pct=True
    )

    # Bucketed team strength (1=Top Teams, 2=Midfield, 3=Backmarkers)
    team_ranks = df.groupby(["Year", "Race"])["TeamSeasonPoints"].rank(
        ascending=False, method="dense"
    )
    df["TeamCategory"] = pd.cut(
        team_ranks, 
        bins=[0, 3, 7, 20], 
        labels=[1, 2, 3],
        right=True
    ).astype(float)

    # Interaction Features
    df["GridQualiInteraction"] = df["GridPosition"] * df["QualiGapToPole"].fillna(0)
    df["Grid_x_Skill"] = df["GridPosition"] * df["SkillScore"].fillna(50.0)
    df["Form_x_Team"] = df["AvgFinish_Last3"].fillna(10.0) * df["TeamCategory"].fillna(2.0)

    return df


def merge_skill_scores(df, skill_df):
    """Merge driver skill scores into the main dataframe."""
    skill_cols = skill_df[["Year", "Abbreviation", "SkillScore", "AvgQualiDelta"]]
    df = df.merge(skill_cols, on=["Year", "Abbreviation"], how="left")

    # Fill missing skill scores with neutral value (50)
    df["SkillScore"] = df["SkillScore"].fillna(50.0)
    df["AvgQualiDelta"] = df["AvgQualiDelta"].fillna(0.0)

    return df


def build_features(df, skill_df):
    """Run the full feature engineering pipeline."""
    print("  Adding rolling features...")
    df = add_rolling_features(df)

    print("  Adding cumulative points...")
    df = add_cumulative_points(df)

    print("  Adding team context...")
    df = add_team_context(df)

    print("  Merging skill scores...")
    df = merge_skill_scores(df, skill_df)

    print("  Adding derived features...")
    df = add_derived_features(df)

    # Mathematical defaults for 0-point race starts (Race 1)
    df["TeamPointsPercentile"] = df["TeamPointsPercentile"].fillna(0.5)
    df["DriverPointsPercentile"] = df["DriverPointsPercentile"].fillna(0.5)
    df["ConstructorGapPct"] = df["ConstructorGapPct"].fillna(0.0)
    
    # Sensible defaults for independent features 
    df["TeamCategory"] = df["TeamCategory"].fillna(2.0)
    df["GridQualiInteraction"] = df["GridQualiInteraction"].fillna(0.0)
    df["QualiGapToPole"] = df["QualiGapToPole"].fillna(df["QualiGapToPole"].median())

    return df


def save_features(df):
    """Save the feature-engineered dataset."""
    path = os.path.join(PROCESSED, "driver_skill_features.csv")
    df.to_csv(path, index=False)
    print(f"✓ Saved features to {path} — {df.shape[0]} rows, {df.shape[1]} columns")


if __name__ == "__main__":
    from collect import load_all_seasons, save_full_dataset
    from skill import compute_skill_scores, save_skill_scores

    # Step 1: Load data
    print("=" * 50)
    print("STEP 1: Loading all seasons")
    print("=" * 50)
    df = load_all_seasons()
    save_full_dataset(df)

    # Step 2: Compute skill scores
    print("\n" + "=" * 50)
    print("STEP 2: Computing driver skill scores")
    print("=" * 50)
    skill = compute_skill_scores(df)
    save_skill_scores(skill)

    # Step 3: Feature engineering
    print("\n" + "=" * 50)
    print("STEP 3: Feature engineering")
    print("=" * 50)
    df = build_features(df, skill)
    save_features(df)

    # Verify model features
    print("\n" + "=" * 50)
    print("VERIFICATION")
    print("=" * 50)
    print(f"Model features present: {all(f in df.columns for f in MODEL_FEATURES)}")
    print(f"NaN check per model feature:")
    for f in MODEL_FEATURES:
        n = df[f].isna().sum()
        print(f"  {f}: {n} NaN{'s' if n != 1 else ''}")
    print(f"Years: {sorted(df['Year'].unique())}")
    print(f"Total rows: {len(df)}")
