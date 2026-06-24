"""
model.py — Advanced Monte-Carlo Simulator & F1 Predictor.
Implements bounded grid-contextual noise loops natively aggregating probabilistic bracket targets
over time-validated tree algorithms preventing absolute structural lookup bounds.
"""
import pandas as pd
import numpy as np
import joblib
import os
import warnings
from sklearn.metrics import mean_absolute_error
from sklearn.inspection import permutation_importance
import xgboost as xgb

warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED = os.path.join(BASE_DIR, "data", "processed")

# Base Generalized Features. These will be pruned programmatically later.
INITIAL_FEATURES = [
    "GridPosition", "QualiGapToPole", "AvgFinish_Last3", "AvgFinish_Last5",
    "DNF_Probability", "SkillScore", "TeamPointsPercentile", "DriverPointsPercentile",
    "ConstructorGapPct", "TeamCategory", "GridQualiInteraction", "AvgQualiDelta",
    "IsStreetCircuit", "TrackCode", "Grid_x_Skill", "Form_x_Team"
]

TARGET = "DeltaPosition"  # Relative outcome targeting


def load_data():
    """Load structural F1 simulation dataset enforcing logical rules natively."""
    path = os.path.join(PROCESSED, "driver_skill_features.csv")
    df = pd.read_csv(path)

    # Base Delta creation natively against non-DNFs strictly for algorithmic scaling limits
    valid_df = df[df["DNF"] == 0].copy()
    valid_df["DeltaPosition"] = valid_df["Position"] - valid_df["GridPosition"]

    # Drops initial-races natively missing momentum tracking metrics securely 
    valid_df = valid_df.dropna(subset=INITIAL_FEATURES + [TARGET, "Position"]).copy()
    
    # Also return the full unaltered timeline for simulating context seamlessly 
    full_df = df.copy()

    return valid_df, full_df


def extract_contextual_noise(grid_array):
    """
    1. Grid-Aware Variance mapping physical racing limits.
    Front runners scale low variance; Midfield scale exceptionally chaotic bounds natively. 
    """
    scale_noise = np.zeros(len(grid_array))
    
    # Constraints specifically designed for asymmetric physical scaling mappings 
    scale_noise[grid_array <= 5] = 0.3      # Clean air, highly stable paces 
    scale_noise[(grid_array > 5) & (grid_array <= 12)] = 0.8  # Chaotic DRS trains
    scale_noise[grid_array > 12] = 0.5      # Restricted pacing limits  
    
    # Create shifted physical distribution (More likely to violently lose time securely than magically gain it)
    return np.random.normal(loc=0.1, scale=scale_noise)


def _train_cycle(train_df, test_df, feature_set):
    """Build bound model specifically tracking true delta physical shifts natively."""
    model = xgb.XGBRegressor(
        n_estimators=400, max_depth=4, learning_rate=0.03, 
        subsample=0.7, colsample_bytree=0.7, 
        reg_alpha=0.2, reg_lambda=2.0, min_child_weight=5,
        random_state=42, n_jobs=-1, objective="reg:squarederror"
    )
    
    X_train, y_train = train_df[feature_set], train_df[TARGET]
    X_test, y_test = test_df[feature_set], test_df[TARGET]
    
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
    
    # Delta Predictions
    preds = model.predict(X_test)
    raw_pos = test_df["GridPosition"].values + preds
    
    # Round accurately 
    bounded = np.clip(np.round(raw_pos), 1, 20)
    mae = mean_absolute_error(test_df["Position"].values, bounded)
    return model, mae


def run_time_based_cv(df):
    """
    Executes structural 3-Fold Time-Series Validation natively assessing bounds 
    generalizations reliably eliminating snapshot-memorizations securely.
    """
    print("\n" + "=" * 50)
    print(" EXECUTING TIME-BASED CROSS VALIDATION")
    print("=" * 50)
    
    splits = [
        (df[df["Year"] <= 2022], df[df["Year"] == 2023], "2020-22 → 2023"),
        (df[df["Year"] <= 2023], df[df["Year"] == 2024], "2020-23 → 2024"),
        (df[df["Year"] <= 2024], df[df["Year"] == 2025], "2020-24 → 2025")
    ]
    
    maes = []
    importances = []
    final_model = None
    
    for train_split, test_split, name in splits:
        model, mae = _train_cycle(train_split, test_split, INITIAL_FEATURES)
        maes.append(mae)
        print(f"  [CV Split] {name:15s} | Unseen MAE: {mae:.4f}")
        
        # Accumulate FI
        imp = model.feature_importances_
        importances.append(imp)
        final_model = model  # Lock final 2025 generation bounds natively 

    avg_mae = np.mean(maes)
    print(f"  -> Average CV Cross-Generational MAE: {avg_mae:.4f}")
    
    return final_model, np.mean(importances, axis=0)


def prune_features(avg_importances, top_n=12):
    """Structurally drop noise variables natively tracking absolute signal cleanly."""
    feats_df = pd.DataFrame({
        "Feature": INITIAL_FEATURES,
        "Importance": avg_importances
    }).sort_values("Importance", ascending=False)
    
    print("\n  [PRUNING] Selecting Top 12 critical algorithms:")
    active_features = feats_df.head(top_n)["Feature"].tolist()
    
    for _, row in feats_df.iterrows():
        status = "KEEP" if row['Feature'] in active_features else "DROP"
        print(f"    {status:5s} | {row['Feature']:25s}: {row['Importance']:.4f}")
        
    return active_features


def train_production_models(df, active_features):
    """
    Generate the Final Models securely bounded over exactly strictly the required dimensions.
    Returns dictionaries mapping feature schemas securely native to the algorithms.
    """
    print("\n" + "=" * 50)
    print(" COMPILING PRUNED PRODUCTION PIPELINES")
    print("=" * 50)
    
    X_pred = df[df["Year"] <= 2024]
    X_sim = df.copy()
    
    # 1. Prediction Model 
    pred_model, pred_mae = _train_cycle(X_pred, df[df["Year"] == 2025], active_features)
    print(f"  [Production Prediction] 2025 Validated MAE: {pred_mae:.4f}")
    
    # 2. Simulation Model 
    sim_xgb = xgb.XGBRegressor(
        n_estimators=500, max_depth=4, learning_rate=0.03, 
        subsample=0.7, colsample_bytree=0.7, 
        reg_alpha=0.5, reg_lambda=5.0, min_child_weight=7,
        random_state=42, n_jobs=-1, objective="reg:squarederror"
    )
    sim_xgb.fit(X_sim[active_features], X_sim[TARGET])
    
    # 3. Packaging Schemas securely 
    pred_dict = {"model": pred_model, "features": active_features}
    sim_dict = {"model": sim_xgb, "features": active_features}
    
    joblib.dump(pred_dict, os.path.join(PROCESSED, "prediction_model.pkl"))
    joblib.dump(sim_dict, os.path.join(PROCESSED, "simulation_model.pkl"))
    
    print("  -> Saved schema arrays structurally to `/processed` natively.")
    return sim_dict


def simulate_race_scenario(model_dict, race_df, runs=100):
    """
    Executes advanced Monte Carlo parallel iterations producing probabilistic arrays cleanly 
    handling DNFs natively and resolving strictly ordered 1-20 position targets. 
    """
    model = model_dict["model"]
    features = model_dict["features"]
    
    # Verify Sanity Bounds Securely 
    missing = [f for f in features if f not in race_df.columns]
    if missing:
        raise ValueError(f"CRASH: Missing features {missing}")
        
    # Baseline calculations
    base_deltas = model.predict(race_df[features])
    grids = race_df["GridPosition"].values
    
    # Safely handle NaNs inside DNF rates mapping them cleanly safely
    dnf_probs = race_df["DNF_Probability"].fillna(0.0).values 
    
    mc_results = []
    
    for _ in range(runs):
        # 1. Inject Contextually Weighted Grid Noise
        noisy_deltas = base_deltas + extract_contextual_noise(grids)
        raw_dist = grids + noisy_deltas
        
        # 2. Explicit DNF Drop Constraints
        # Probabilistically force massive drops mimicking unrecoverable damage cleanly
        crashes = np.random.random(len(raw_dist)) < (dnf_probs * 0.5)
        raw_dist[crashes] += 99  # Shunts them absolutely precisely to back of pack securely 
        
        # 3. Position Reconstruction (No Ties, Strictly 1-20 Constraints)
        ordered_positions = pd.Series(raw_dist).rank(method='first').values
        mc_results.append(ordered_positions)
        
    # Aggregate matrix structural constraints (Drivers x Runs)
    aggregate_matrix = np.vstack(mc_results).T  
    
    predictions = []
    for i in range(len(race_df)):
        dr = race_df.iloc[i]["Abbreviation"]
        driver_pos_array = aggregate_matrix[i]
        
        # Compute exact probable locations
        median_rounded = int(np.median(driver_pos_array))
        p25 = int(np.percentile(driver_pos_array, 25))
        p75 = int(np.percentile(driver_pos_array, 75))
        
        podium_pct = np.mean(driver_pos_array <= 3) * 100
        points_pct = np.mean(driver_pos_array <= 10) * 100
        
        # Determine exact confidence scalar securely tracking standard deviation stability securely
        confidence = max(0, min(100, 100 - (np.std(driver_pos_array) * 10)))
        
        predictions.append({
            "Driver": dr,
            "Grid": int(grids[i]),
            "Median": median_rounded,
            "Expected": f"P{p25}-P{p75}" if p25 != p75 else f"P{p25}",
            "Podium_%": f"{podium_pct:.1f}%",
            "Top10_%": f"{points_pct:.1f}%",
            "Confidence": f"{confidence:.0f}%"
        })
        
    return pd.DataFrame(predictions).sort_values("Median").reset_index(drop=True)


if __name__ == "__main__":
    valid_df, full_df = load_data()
    
    # 1. Pipeline execution
    _, importances = run_time_based_cv(valid_df)
    active_features = prune_features(importances, top_n=12)
    sim_dict = train_production_models(valid_df, active_features)
    
    # 2. Extract a full cohesive race safely mapping structural evaluation tracking
    print("\n" + "=" * 50)
    print(" UI MONTE-CARLO SANITY VERIFICATION")
    print("=" * 50)
    
    test_race = full_df[(full_df["Year"] == 2024) & (full_df["Race"] == "British Grand Prix")]
    
    res = simulate_race_scenario(sim_dict, test_race, runs=100)
    print(res.to_string(index=False))
