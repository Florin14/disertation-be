import os

import joblib
import numpy as np
from fastapi import Depends, HTTPException
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sqlalchemy.orm import Session

from extensions import get_db
from modules.prediction.routes.helpers import load_listings_as_dataframe
from project_helpers.responses import ConfirmationResponse
from .router import router
from ..models import PredictionAdd, GridResultResponse

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models_saved")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH_RF = os.path.join(MODEL_DIR, "price_model_rf.joblib")
MODEL_PATH_GB = os.path.join(MODEL_DIR, "price_model_gb.joblib")


@router.post("-v2", response_model=ConfirmationResponse)
async def add_prediction2(data: PredictionAdd, db: Session = Depends(get_db)):
    """
    1) Calculăm ținta price_per_sqm = price / useful_area.
    2) Construim noi caracteristici (ratios etc.).
    3) Definim pipeline + GridSearchCV pentru RF și GB.
    4) Antrenăm, evaluăm, salvăm modelele optime.
    """
    test_size: float = 0.2
    random_state: int = 42

    # 1) Încărcăm datele
    try:
        df = load_listings_as_dataframe()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare la load_listings_as_dataframe: {e}")

    # 2) Dropping rows where price sau useful_area lipsesc / utile_area <= 0
    df = df.dropna(subset=["price", "useful_area"])
    df = df[df["useful_area"] > 0]
    if df.shape[0] < 50:
        raise HTTPException(status_code=400, detail="Nu există suficiente date pentru antrenament după filtrare.")

    # 3) Calculăm noua țintă: price_per_sqm
    df["price_per_sqm"] = df["price"] / df["useful_area"]

    # 4) Generăm FEATURE‐URI suplimentare (raporturi între suprafețe):
    #    * built/useful, yard/useful, terrace/useful, balcony/useful
    df["ratio_built_useful"] = df["built_area"].fillna(0) / df["useful_area"]
    df["ratio_yard_useful"] = df["yard_area"].fillna(0) / df["useful_area"]
    df["ratio_terrace_useful"] = df["terrace_area"].fillna(0) / df["useful_area"]
    df["ratio_balcony_useful"] = df["balcony_area"].fillna(0) / df["useful_area"]

    # 5) Separăm ținta (y) de features (X)
    y = df["price_per_sqm"].values
    X = df.drop(columns=["price", "price_per_sqm"])

    # 6) Definim lista de coloane numerice și categorice
    numeric_features = [
        "useful_area",
        "built_area",
        "yard_area",
        "terrace_area",
        "balcony_area",
        "num_rooms",
        "num_bathrooms",
        "num_garages",
        "floor",
        "street_frontage",
        # + rapoartele create mai sus:
        "ratio_built_useful",
        "ratio_yard_useful",
        "ratio_terrace_useful",
        "ratio_balcony_useful",
    ]
    categorical_features = [
        "classification",
        "land_classification",
        "city",
        # poți include și „condominium”, „structural_system”, „terraces”, „comfort” dacă au sens
        "condominium",
        "structural_system",
        "terraces",
        "comfort",
    ]

    # 7) Construim TRANSFORMER‐ul
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
            # poți adăuga StandardScaler() după imputare
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
        remainder="drop"  # abandonează restul coloanelor (inclusiv id, external_id, url etc.)
    )

    # 8) Construim doi regiștri: RF și GB (fără hiperparametri fixați)
    model_rf = RandomForestRegressor(random_state=random_state)
    clf_rf = Pipeline(steps=[("preprocessor", preprocessor), ("regressor", model_rf)])

    model_gb = GradientBoostingRegressor(random_state=random_state)
    clf_gb = Pipeline(steps=[("preprocessor", preprocessor), ("regressor", model_gb)])

    # 9) Împărțim în train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    # ────────────────────────────────────────────────────────────
    # 10) GRID SEARCH pentru RandomForestRegressor
    # ────────────────────────────────────────────────────────────
    param_grid_rf = {
        "regressor__n_estimators": [50, 100, 200],
        "regressor__max_depth": [None, 10, 20, 30],
        "regressor__min_samples_split": [2, 5, 10],
        "regressor__min_samples_leaf": [1, 2, 4],
        "regressor__max_features": ["auto", "sqrt"],
    }
    grid_rf = GridSearchCV(
        estimator=clf_rf,
        param_grid=param_grid_rf,
        cv=5,
        scoring="neg_mean_absolute_error",
        n_jobs=-1,
        verbose=1,
    )
    grid_rf.fit(X_train, y_train)

    best_rf: Pipeline = grid_rf.best_estimator_
    best_params_rf = grid_rf.best_params_
    y_pred_rf = best_rf.predict(X_test)
    mae_rf = mean_absolute_error(y_test, y_pred_rf)
    rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
    print(f"[RF – BEST] Params: {best_params_rf}")
    print(f"[RF – BEST] MAE(ppsm) = {mae_rf:.2f}, RMSE(ppsm) = {rmse_rf:.2f}")

    # 11) GRID SEARCH pentru GradientBoostingRegressor
    param_grid_gb = {
        "regressor__n_estimators": [50, 100, 200],
        "regressor__learning_rate": [0.01, 0.1, 0.2],
        "regressor__max_depth": [3, 5, 7],
        "regressor__min_samples_split": [2, 5],
        "regressor__min_samples_leaf": [1, 2],
        "regressor__subsample": [0.7, 0.8, 1.0],
    }
    grid_gb = GridSearchCV(
        estimator=clf_gb,
        param_grid=param_grid_gb,
        cv=5,
        scoring="neg_mean_absolute_error",
        n_jobs=-1,
        verbose=1,
    )
    grid_gb.fit(X_train, y_train)

    best_gb: Pipeline = grid_gb.best_estimator_
    best_params_gb = grid_gb.best_params_
    y_pred_gb = best_gb.predict(X_test)
    mae_gb = mean_absolute_error(y_test, y_pred_gb)
    rmse_gb = np.sqrt(mean_squared_error(y_test, y_pred_gb))
    print(f"[GB – BEST] Params: {best_params_gb}")
    print(f"[GB – BEST] MAE(ppsm) = {mae_gb:.2f}, RMSE(ppsm) = {rmse_gb:.2f}")

    # 12) Comparație și salvare a modelului câștigător
    #    Să zicem că alegem pe cel cu MAE(ppsm) mai mic:
    if mae_rf <= mae_gb:
        winner = "RF"
        model_to_save = best_rf
        save_path = MODEL_PATH_RF
    else:
        winner = "GB"
        model_to_save = best_gb
        save_path = MODEL_PATH_GB

    try:
        joblib.dump(model_to_save, save_path)
        print(f"[WINNER] Model {winner} salvat la: {save_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare la salvarea modelului câștigător: {e}")

    return GridResultResponse(
        best_model=winner,
        rf_mae_ppsm=mae_rf,
        rf_rmse_ppsm=rmse_rf,
        gb_mae_ppsm=mae_gb,
        gb_rmse_ppsm=rmse_gb,
    )
