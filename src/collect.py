"""
collect.py — Load and combine all season CSVs into a clean full_dataset.csv
"""
import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED = os.path.join(BASE_DIR, "data", "processed")

SEASONS = [2020, 2021, 2022, 2023, 2024, 2025]


def load_all_seasons():
    """Load all season CSVs and combine into one DataFrame."""
    dfs = []
    for year in SEASONS:
        path = os.path.join(PROCESSED, f"season_{year}.csv")
        if not os.path.exists(path):
            print(f"⚠ Missing: {path}")
            continue
        season = pd.read_csv(path)
        print(f"✓ {year}: {season.shape[0]} rows, {season['Race'].nunique()} races")
        dfs.append(season)

    df = pd.concat(dfs, ignore_index=True)
    df = df.drop_duplicates(subset=["Abbreviation", "Year", "Race"])

    # Basic type cleaning
    df["Position"] = pd.to_numeric(df["Position"], errors="coerce")
    df["GridPosition"] = pd.to_numeric(df["GridPosition"], errors="coerce")
    df["Points"] = pd.to_numeric(df["Points"], errors="coerce").fillna(0)
    df["DNF"] = pd.to_numeric(df["DNF"], errors="coerce").fillna(0).astype(int)
    df["Round"] = pd.to_numeric(df["Round"], errors="coerce")

    # Drop rows where Position or GridPosition is null (DNS / disqualified)
    before = len(df)
    df = df.dropna(subset=["Position", "GridPosition"])
    dropped = before - len(df)
    if dropped > 0:
        print(f"  Dropped {dropped} rows with missing Position/GridPosition")

    # Sort chronologically
    df = df.sort_values(["Year", "Round", "Position"]).reset_index(drop=True)

    print(f"\n✓ Combined dataset: {df.shape[0]} rows, {df['Year'].nunique()} seasons")
    return df


def save_full_dataset(df):
    """Save the combined dataset."""
    path = os.path.join(PROCESSED, "full_dataset.csv")
    df.to_csv(path, index=False)
    print(f"✓ Saved to {path}")


if __name__ == "__main__":
    df = load_all_seasons()
    save_full_dataset(df)
