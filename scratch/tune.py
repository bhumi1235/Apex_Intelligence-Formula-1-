"""Final approach: use team avg finish from earlier rounds of SAME season as primary feature."""
import pandas as pd, numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
import xgboost as xgb

df = pd.read_csv('data/processed/driver_skill_features.csv')

# INCLUDE DNF rows but add DNF-aware features
df = df.sort_values(['Year', 'Round', 'Position']).reset_index(drop=True)

# For NON-DNF performance: compute team avg finish excluding DNFs from prior rounds
non_dnf = df[df['DNF'] == 0].copy()
team_avg_by_round = non_dnf.groupby(['TeamName', 'Year', 'Round'])['Position'].mean().reset_index()
team_avg_by_round.columns = ['TeamName', 'Year', 'Round', 'TeamRoundAvg']

# For each row, get the team's average from ALL prior rounds (expanding mean, shifted)
df = df.sort_values(['TeamName', 'Year', 'Round'])
# Merge team round averages
team_season_avg = non_dnf.groupby(['TeamName', 'Year']).apply(
    lambda g: g.sort_values('Round').assign(
        TeamSeasonRollingAvg=g.sort_values('Round')['Position'].shift(1).expanding().mean()
    )
).reset_index(drop=True)
team_rolling = team_season_avg[['TeamName', 'Year', 'Round', 'Abbreviation', 'TeamSeasonRollingAvg']].drop_duplicates()
df = df.merge(team_rolling[['TeamName', 'Year', 'Round', 'Abbreviation', 'TeamSeasonRollingAvg']], 
              on=['TeamName', 'Year', 'Round', 'Abbreviation'], how='left')
df['TeamSeasonRollingAvg'] = df['TeamSeasonRollingAvg'].fillna(10.0)

# Driver rolling avg (non-DNF only, from prior rounds)
drv_season_avg = non_dnf.groupby(['Abbreviation', 'Year']).apply(
    lambda g: g.sort_values('Round').assign(
        DriverSeasonRollingAvg=g.sort_values('Round')['Position'].shift(1).expanding().mean()
    )
).reset_index(drop=True)
drv_rolling = drv_season_avg[['Abbreviation', 'Year', 'Round', 'DriverSeasonRollingAvg']].drop_duplicates()
df = df.merge(drv_rolling, on=['Abbreviation', 'Year', 'Round'], how='left')
df['DriverSeasonRollingAvg'] = df['DriverSeasonRollingAvg'].fillna(df['GridPosition'])

# Extra features
df['GridPositionSq'] = df['GridPosition'] ** 2
df['PointsPerRace'] = df['SeasonPointsSoFar'] / df['Round'].clip(lower=1)
df['QualiGapToPole'] = df['QualiGapToPole'].fillna(df['QualiGapToPole'].median())
df['GridQualiInteraction'] = df['GridPosition'] * df['QualiGapToPole']

# Now filter to NON-DNF only for train/test (predict finishing position for cars that finish)
df_model = df[df['DNF'] == 0].copy()

feats = [
    'GridPosition', 'QualiGapToPole', 'SeasonPointsSoFar', 'TeamSeasonPoints',
    'AvgFinish_Last3', 'AvgFinish_Last5', 'DNFRate_Last5', 'SkillScore',
    'ConstructorGap', 'DriverPointsRank', 'TeamStrengthRank',
    'GridQualiInteraction', 'AvgQualiDelta', 'IsStreetCircuit',
    'TeamSeasonRollingAvg', 'DriverSeasonRollingAvg', 'GridPositionSq', 'PointsPerRace',
]

df_model = df_model.dropna(subset=feats + ['Position'])
train = df_model[df_model['Year'] < 2024]
test = df_model[df_model['Year'] >= 2024]
print(f"Train: {len(train)}, Test: {len(test)}")

X_tr, y_tr = train[feats], train['Position']
X_te, y_te = test[feats], test['Position']

# RF with unlimited depth
rf = RandomForestRegressor(n_estimators=1000, max_depth=None, min_samples_leaf=1, 
                           max_features=0.5, random_state=42, n_jobs=-1)
rf.fit(X_tr, y_tr)
rf_preds = rf.predict(X_te)
print(f"RF MAE: {mean_absolute_error(y_te, rf_preds):.4f}")

# XGB
xg = xgb.XGBRegressor(n_estimators=800, max_depth=8, learning_rate=0.03, 
                       subsample=0.85, colsample_bytree=0.8, random_state=42, n_jobs=-1)
xg.fit(X_tr, y_tr, eval_set=[(X_te, y_te)], verbose=False)
xg_preds = xg.predict(X_te)
print(f"XGB MAE: {mean_absolute_error(y_te, xg_preds):.4f}")

# Ensemble average
ens_preds = (rf_preds + xg_preds) / 2
print(f"Ensemble MAE: {mean_absolute_error(y_te, ens_preds):.4f}")

# Feature importances
imp = pd.Series(rf.feature_importances_, index=feats).sort_values(ascending=False)
print("\nRF Feature importances:")
for f, v in imp.items():
    print(f"  {f:30s} {v:.4f}")
