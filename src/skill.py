"""
skill.py — Compute driver skill scores via teammate comparisons
"""
import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED = os.path.join(BASE_DIR, "data", "processed")


def compute_teammate_comparisons(df):
    """
    For each race, compare each driver against their teammate(s).
    Only compare when neither driver DNF'd.
    Returns a DataFrame with PositionDelta and QualiDelta per comparison.
    """
    skill_rows = []

    for (year, race, team), group in df.groupby(["Year", "Race", "TeamName"]):
        if len(group) < 2:
            continue

        drivers = group[["Abbreviation", "Position", "QualiGapToPole"]].values

        for i in range(len(drivers)):
            for j in range(len(drivers)):
                if i == j:
                    continue

                driver = drivers[i]
                teammate = drivers[j]

                # Skip if either DNF'd
                d_dnf = group[group["Abbreviation"] == driver[0]]["DNF"].values[0]
                t_dnf = group[group["Abbreviation"] == teammate[0]]["DNF"].values[0]
                if d_dnf == 1 or t_dnf == 1:
                    continue

                # Positive PositionDelta = driver beat teammate
                pos_delta = teammate[1] - driver[1]
                quali_delta = teammate[2] - driver[2] if pd.notna(driver[2]) and pd.notna(teammate[2]) else 0

                skill_rows.append({
                    "Year": year,
                    "Race": race,
                    "Abbreviation": driver[0],
                    "Teammate": teammate[0],
                    "TeamName": team,
                    "PositionDelta": pos_delta,
                    "QualiDelta": quali_delta,
                })

    return pd.DataFrame(skill_rows)


def compute_skill_scores(df):
    """
    Compute SkillScore (0–100 normalized) and AvgQualiDelta per driver per year.
    """
    comparisons = compute_teammate_comparisons(df)
    print(f"  Teammate comparisons: {len(comparisons)}")

    driver_skill = comparisons.groupby(["Year", "Abbreviation"]).agg(
        AvgPositionDelta=("PositionDelta", "mean"),
        AvgQualiDelta=("QualiDelta", "mean"),
        Races=("PositionDelta", "count"),
    ).reset_index()

    # Normalize to 0–100
    min_val = driver_skill["AvgPositionDelta"].min()
    max_val = driver_skill["AvgPositionDelta"].max()
    if max_val > min_val:
        driver_skill["SkillScore"] = (
            (driver_skill["AvgPositionDelta"] - min_val) / (max_val - min_val) * 100
        ).round(1)
    else:
        driver_skill["SkillScore"] = 50.0

    return driver_skill


def save_skill_scores(skill_df):
    """Save driver skill scores."""
    path = os.path.join(PROCESSED, "driver_skill.csv")
    skill_df.to_csv(path, index=False)
    print(f"✓ Saved skill scores to {path}")


if __name__ == "__main__":
    df = pd.read_csv(os.path.join(PROCESSED, "full_dataset.csv"))
    skill = compute_skill_scores(df)
    save_skill_scores(skill)
    print(f"\nSkill scores computed for {skill['Year'].nunique()} seasons, {skill['Abbreviation'].nunique()} drivers")
