import os
import re
from datetime import datetime

import joblib
import numpy as np
from fastapi import HTTPException
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from modules.prediction.routes.helpers import load_listings_as_dataframe


def get_next_model_path(model_dir, base_name):
    # Obține toate fișierele din directorul model_dir
    files = os.listdir(model_dir)

    # Filtrează fișierele care corespund modelului specific
    pattern = re.compile(rf"{base_name}(\d+)\.joblib")
    indices = [
        int(match.group(1)) for file in files if (match := pattern.match(file))
    ]

    # Determină următorul index
    next_index = max(indices, default=0) + 1

    # Returnează calea completă pentru următorul fișier
    return os.path.join(model_dir, f"{base_name}{next_index}.joblib")


# Unde salvăm modelele
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models_saved")
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH_RF = get_next_model_path(MODEL_DIR, "price_model_rf")
MODEL_PATH_GB = get_next_model_path(MODEL_DIR, "price_model_gb")

test_size = 0.2
random_state = 42

print("starttime:")
print(datetime.now())

# 1) Încarcă datele și filtrează
df = load_listings_as_dataframe()
df = df.dropna(subset=["price", "useful_area"])
df = df[df["useful_area"] > 0]
if df.shape[0] < 50:
    raise HTTPException(status_code=400, detail="Date insuficiente pentru antrenament.")

# 2) Ținta: price_per_sqm
df["price_per_sqm"] = df["price"] / df["useful_area"]

# 3) Calculăm rapoartele noi (dacă există coloane)
df["ratio_built_useful"] = df["built_area"].fillna(0) / df["useful_area"]
df["ratio_yard_useful"] = df["yard_area"].fillna(0) / df["useful_area"]

# 4) Separăm y (target) de X (features)
y = df["price_per_sqm"].values
X = df.drop(columns=["price", "price_per_sqm"])

# 5) Definim caracteristicile
numeric_features = [
    "useful_area", "built_area", "yard_area",
    "num_rooms", "num_bathrooms", "has_garage", "floor",
    "ratio_built_useful", "ratio_yard_useful", "ratio_terrace_useful", "ratio_balcony_useful",
]
categorical_features = [
    "classification", "land_classification", "city",
    "condominium", "has_terrace", "comfort",
]

# 6) Construim preprocesorul
numeric_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
    # opțional: ("scaler", StandardScaler())
])
categorical_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
    ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
])
preprocessor = ColumnTransformer([
    ("num", numeric_transformer, numeric_features),
    ("cat", categorical_transformer, categorical_features),
], remainder="drop")

# 7) Construim pipeline‐uri
pipe_rf = Pipeline([
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor(random_state=random_state)),
])
pipe_gb = Pipeline([
    ("preprocessor", preprocessor),
    ("regressor", GradientBoostingRegressor(random_state=random_state)),
])

# 8) Param distribution pentru RandomizedSearch – RF
param_dist_rf = {
    "regressor__n_estimators": [50, 100, 200],
    "regressor__max_depth": [10, 20, None],
    "regressor__min_samples_split": [2, 5],
    "regressor__min_samples_leaf": [1, 2],
    # doar valori valide: "sqrt", "log2" sau un float
    "regressor__max_features": ["sqrt", "log2"],
}
rand_rf = RandomizedSearchCV(
    estimator=pipe_rf,
    param_distributions=param_dist_rf,
    n_iter=20,  # testează 20 combinații random
    cv=3,  # 3‐fold CV
    scoring="neg_mean_absolute_error",
    n_jobs=-1,
    random_state=random_state,
    verbose=1,
    error_score="raise"  # dacă apare o combinație invalidă, oprește eroarea
)

# 9) Param distribution pentru RandomizedSearch – GB
param_dist_gb = {
    "regressor__n_estimators": [50, 100, 200],
    "regressor__learning_rate": [0.01, 0.1, 0.2],
    "regressor__max_depth": [3, 5],
    "regressor__min_samples_split": [2, 5],
    "regressor__min_samples_leaf": [1, 2],
    "regressor__subsample": [0.7, 1.0],
}
rand_gb = RandomizedSearchCV(
    estimator=pipe_gb,
    param_distributions=param_dist_gb,
    n_iter=20,
    cv=3,
    scoring="neg_mean_absolute_error",
    n_jobs=-1,
    random_state=random_state,
    verbose=1,
    error_score="raise"
)

# 10) Împărțim în train/test pe întregul set pentru evaluarea finală
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=test_size, random_state=random_state
)

# 11) Antrenare Randomized RF
print(">>> Încep RandomizedSearchCV pentru RF …")
rand_rf.fit(X_train, y_train)
best_rf = rand_rf.best_estimator_
y_pred_rf = best_rf.predict(X_test)
mae_rf = mean_absolute_error(y_test, y_pred_rf)
rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
print(f"[RF] Best params: {rand_rf.best_params_}")
print(f"[RF] MAE(ppsm)={mae_rf:.2f}, RMSE(ppsm)={rmse_rf:.2f}")

print("starttime rf:")
print(datetime.now())
# 12) Antrenare Randomized GB
print(">>> Încep RandomizedSearchCV pentru GB …")
rand_gb.fit(X_train, y_train)
best_gb = rand_gb.best_estimator_
y_pred_gb = best_gb.predict(X_test)
mae_gb = mean_absolute_error(y_test, y_pred_gb)
rmse_gb = np.sqrt(mean_squared_error(y_test, y_pred_gb))
print(f"[GB] Best params: {rand_gb.best_params_}")
print(f"[GB] MAE(ppsm)={mae_gb:.2f}, RMSE(ppsm)={rmse_gb:.2f}")
print("endtime rf:")
print(datetime.now())
# 13) Alege modelul câștigător
if mae_rf <= mae_gb:
    winner = "RF"
    model_to_save = best_rf
    save_path = MODEL_PATH_RF
else:
    winner = "GB"
    model_to_save = best_gb
    save_path = MODEL_PATH_GB

joblib.dump(model_to_save, save_path)
print(f"[WINNER] {winner} salvat la {save_path}")
