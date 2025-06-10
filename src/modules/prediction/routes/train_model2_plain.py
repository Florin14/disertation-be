import os
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from fastapi import HTTPException
from scipy.stats import randint as sp_randint  # alias clar pentru scipy.stats.randint
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    RandomForestRegressor,
    HistGradientBoostingRegressor,
    StackingRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler

from modules.prediction.routes.helpers import load_listings_as_dataframe

# ─── DIRECTOARE ──────────────────────────────────────────────────────────────
BASEDIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASEDIR, "..", "models_saved")
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "price_model_best_2.joblib")
MODEL_PATH_2 = os.path.join(MODEL_DIR, "price_model_best_2_hgb.joblib")

# ─── PARAMETRI ───────────────────────────────────────────────────────────────
TEST_SIZE = 0.2
RANDOM_STATE = 42
N_ITER = 50
CV_FOLDS = 5

print("START TRAIN:", datetime.now())

# ─── 1) ÎNCARCĂ DATELE ───────────────────────────────────────────────────────
try:
    df = load_listings_as_dataframe()
except Exception as e:
    raise HTTPException(status_code=500, detail=f"load_listings error: {e}")

df = df.dropna(subset=["price", "useful_area", "latitude", "longitude"])
df = df[df["useful_area"] > 0]
if df.shape[0] < 50:
    raise HTTPException(status_code=400, detail="Insufficient data")

# ─── 2) FEATURE ENGINEERING ─────────────────────────────────────────────────
built = df["built_area"].fillna(0)
yard = df["yard_area"].fillna(0)
terr = df.get("terrace_area", pd.Series(0, index=df.index)).fillna(0)
balc = df.get("balcony_area", pd.Series(0, index=df.index)).fillna(0)

df["ratio_built_useful"] = built / df["useful_area"]
df["ratio_yard_useful"] = yard / df["useful_area"]
df["ratio_terrace_useful"] = terr / df["useful_area"]
df["ratio_balcony_useful"] = balc / df["useful_area"]

# ─── 3) PREGĂTEȘTE X, y ─────────────────────────────────────────────────────
df["price_per_sqm"] = df["price"] / df["useful_area"]
y = df["price_per_sqm"].values

numeric_features = [
    "useful_area", "built_area", "yard_area",
    "num_rooms", "num_bathrooms",
    "has_garage", "has_balconies", "has_terrace",
    "built_year",
    "ratio_built_useful", "ratio_yard_useful",
    "ratio_terrace_useful", "ratio_balcony_useful"
]
categorical_features = [
    "classification", "land_classification", "city",
    "condominium", "comfort", "property_type", "structure"
]

X = df[numeric_features + categorical_features].copy()

# ─── 4) PREPROCESSOR ────────────────────────────────────────────────────────
pre_num = Pipeline([
    ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
    ("scaler", MinMaxScaler())
])
pre_cat = Pipeline([
    ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
    ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
])
preprocessor = ColumnTransformer([
    ("num", pre_num, numeric_features),
    ("cat", pre_cat, categorical_features)
], remainder="drop")

# ─── 5) SEARCH RF & HGB ─────────────────────────────────────────────────────
pipeline_rf = Pipeline([
    ("pre", preprocessor),
    ("reg", RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=-1))
])
param_rf = {
    "reg__n_estimators": sp_randint(200, 500),  # folosește scipy.stats.randint
    "reg__max_depth": [None, 20, 30, 40],
    "reg__min_samples_split": sp_randint(2, 10),
    "reg__min_samples_leaf": sp_randint(1, 5),
    "reg__max_features": ["sqrt", "log2", 0.7]
}
search_rf = RandomizedSearchCV(
    pipeline_rf, param_rf, n_iter=N_ITER, cv=CV_FOLDS,
    scoring="neg_mean_absolute_error", random_state=RANDOM_STATE,
    verbose=1, n_jobs=-1
)

pipeline_hgb = Pipeline([
    ("pre", preprocessor),
    ("reg", HistGradientBoostingRegressor(
        random_state=RANDOM_STATE,
        early_stopping=True,
        validation_fraction=0.1
    ))
])
param_hgb = {
    "reg__max_iter": sp_randint(200, 600),
    "reg__learning_rate": [0.01, 0.03, 0.05, 0.1],
    "reg__max_depth": [None, 5, 10, 15],
    "reg__l2_regularization": [0.0, 0.1, 0.5, 1.0]
}
search_hgb = RandomizedSearchCV(
    pipeline_hgb, param_hgb, n_iter=N_ITER, cv=CV_FOLDS,
    scoring="neg_mean_absolute_error", random_state=RANDOM_STATE,
    verbose=1, n_jobs=-1
)

# ─── 6) SPLIT & TRAIN ───────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
)
print("Training Random Forest…")
search_rf.fit(X_train, y_train)
print("Training HistGradientBoosting…")
search_hgb.fit(X_train, y_train)

# ─── 7) STACKING ────────────────────────────────────────────────────────────
rf_best = search_rf.best_estimator_
hgb_best = search_hgb.best_estimator_
stack = StackingRegressor(
    estimators=[("rf", rf_best), ("hgb", hgb_best)],
    final_estimator=RandomForestRegressor(random_state=RANDOM_STATE, n_estimators=200),
    n_jobs=-1
)
print("Training StackingRegressor…")
stack.fit(X_train, y_train)

# ─── 8) EVALUARE ───────────────────────────────────────────────────────────
for name, mdl in [("RF", rf_best), ("HGB", hgb_best), ("STACK", stack)]:
    y_pred = mdl.predict(X_test)
    print(f"{name}: MAE={mean_absolute_error(y_test, y_pred):.3f}, "
          f"RMSE={np.sqrt(mean_squared_error(y_test, y_pred)):.3f}, "
          f"R2={r2_score(y_test, y_pred):.3f}")

# ─── 9) SELECT & SALVEAZĂ ───────────────────────────────────────────────────
best_model = min(
    [rf_best, hgb_best, stack],
    key=lambda m: mean_absolute_error(y_test, m.predict(X_test))
)
joblib.dump(rf_best, MODEL_PATH)
joblib.dump(hgb_best, MODEL_PATH_2)
print("Saved best model to", MODEL_PATH)
print("END TRAIN:", datetime.now())

# 11) (Opțional) RANDOMIZED SEARCH pentru GradientBoostingRegressor
# ────────────────────────────────────────────────────────────
# from sklearn.ensemble import GradientBoostingRegressor
# param_dist_gb = {
#     "regressor__n_estimators": randint(50, 200),
#     "regressor__learning_rate": uniform(0.01, 0.19),  # 0.01–0.20
#     "regressor__max_depth": [3, 5, 7],
#     "regressor__min_samples_split": randint(2, 6),
#     "regressor__min_samples_leaf": randint(1, 3),
#     "regressor__subsample": [0.7, 0.8, 1.0],
# }
# model_gb = GradientBoostingRegressor(random_state=random_state)
# clf_gb = Pipeline([("preprocessor", preprocessor), ("regressor", model_gb)])
# random_search_gb = RandomizedSearchCV(
#     estimator=clf_gb,
#     param_distributions=param_dist_gb,
#     n_iter=25,
#     cv=3,
#     scoring="neg_mean_absolute_error",
#     n_jobs=-1,
#     random_state=random_state,
#     verbose=2
# )
# random_search_gb.fit(X_train, y_train)
# best_gb = random_search_gb.best_estimator_
# y_pred_gb = best_gb.predict(X_test)
# mae_gb  = mean_absolute_error(y_test, y_pred_gb)
# rmse_gb = np.sqrt(mean_squared_error(y_test, y_pred_gb))
# print(f"[GB – BEST] MAE(ppsm) = {mae_gb:.2f}, RMSE(ppsm) = {rmse_gb:.2f}")
