import os
from datetime import datetime

import joblib
import numpy as np
from fastapi import HTTPException
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from modules.prediction.routes.helpers import load_listings_as_dataframe

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models_saved")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH_RF = os.path.join(MODEL_DIR, "price_model_rf_final.joblib")
# MODEL_PATH_GB = os.path.join(MODEL_DIR, "price_model_gb.joblib")

test_size: float = 0.2
random_state: int = 42

print("starttime:")
print(datetime.now())

# 1) Încărcăm datele
try:
    df = load_listings_as_dataframe()
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Eroare la load_listings_as_dataframe: {e}")

# 2) Filtrăm datele
df = df.dropna(subset=["price", "useful_area"])
df = df[df["useful_area"] > 0]
if df.shape[0] < 50:
    raise HTTPException(status_code=400, detail="Nu există suficiente date pentru antrenament după filtrare.")

# 3) Calculăm ținta
df["price_per_sqm"] = df["price"] / df["useful_area"]

# 4) (Opțional) Generăm feature-uri suplimentare, dacă ai suprafață pentru terasă/balcon:
# df["ratio_built_useful"]   = df["built_area"].fillna(0) / df["useful_area"]
# df["ratio_yard_useful"]    = df["yard_area"].fillna(0)  / df["useful_area"]

# 5) Separăm X și y
y = df["price_per_sqm"].values
X = df.drop(columns=["price", "price_per_sqm"])

# 6) Listele de coloane
numeric_features = [
    "useful_area",
    "built_area",
    "yard_area",
    "num_rooms",
    "num_bathrooms",
    "has_garage",
    "floor",
    "built_year",
    # Dacă ai rapoarte calculate, le adaugi aici, altfel le comentezi:
    # "ratio_built_useful",
    # "ratio_yard_useful",
]
categorical_features = [
    "classification",
    # "land_classification",
    "city",
    "condominium",
    "num_kitchens",
    "has_parking_space",
    "has_terrace",
    "has_balconies",
    "comfort",
    "property_type",
    "structure",
    "for_sale",
]

# 7) Preprocessor
numeric_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
        ("scaler", StandardScaler()),
    ]
)
categorical_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ]
)
preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features),
    ],
    remainder="drop"
)

# 8) Pipeline RF
model_rf = RandomForestRegressor(random_state=random_state)
clf_rf = Pipeline([("preprocessor", preprocessor), ("regressor", model_rf)])

# 9) Împărțim în train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=test_size, random_state=random_state
)

# ────────────────────────────────────────────────────────────
# 10) RANDOMIZED SEARCH pentru RandomForestRegressor
# ────────────────────────────────────────────────────────────
from scipy.stats import randint, uniform

param_dist_rf = {
    # Testăm un set restrâns de estimatori și adâncimi
    "regressor__n_estimators": randint(50, 300),        # între 50 și 300
    "regressor__max_depth": [None, 10, 20, 30],
    "regressor__min_samples_split": randint(2, 10),     # 2–10
    "regressor__min_samples_leaf": randint(1, 5),       # 1–4
    "regressor__max_features": ["sqrt", "log2", 0.5],
}

random_search_rf = RandomizedSearchCV(
    estimator=clf_rf,
    param_distributions=param_dist_rf,
    n_iter=30,                    # testăm 30 de combinații aleatorii
    cv=3,                         # folosim 3-fold CV în loc de 5
    scoring="neg_mean_absolute_error",
    n_jobs=-1,
    random_state=random_state,
    verbose=2
)
random_search_rf.fit(X_train, y_train)

best_rf: Pipeline = random_search_rf.best_estimator_
best_params_rf = random_search_rf.best_params_

# Evaluare pe setul de test
y_pred_rf = best_rf.predict(X_test)
mae_rf  = mean_absolute_error(y_test, y_pred_rf)
rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))

print(f"[RF – BEST] Params: {best_params_rf}")
print(f"[RF – BEST] MAE(ppsm) = {mae_rf:.2f}, RMSE(ppsm) = {rmse_rf:.2f}")

# Afișăm câteva feature importances rapide:
num_cols = numeric_features
cat_cols = best_rf.named_steps["preprocessor"] \
    .named_transformers_["cat"] \
    .named_steps["onehot"] \
    .get_feature_names_out(categorical_features)
all_feats = np.concatenate([num_cols, cat_cols])

importances = best_rf.named_steps["regressor"].feature_importances_
indices     = np.argsort(importances)[::-1]

print("Top 10 feature importances:")
for idx in indices[:10]:
    print(f"  {all_feats[idx]}: {importances[idx]:.4f}")

print("endtime:")
print(datetime.now())

# 12) Salvăm modelul câștigător
winner = "RF"
model_to_save = best_rf
save_path = MODEL_PATH_RF

try:
    joblib.dump(model_to_save, save_path)
    print(f"[WINNER] Model {winner} salvat la: {save_path}")
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Eroare la salvarea modelului: {e}")
