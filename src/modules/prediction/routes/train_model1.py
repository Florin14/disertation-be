import os
import joblib
import numpy as np

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from extensions import get_db
from modules.prediction.routes.helpers import load_listings_as_dataframe
from .router import router
from ..models import PredictionAdd, GridResultResponseTrain1

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models_saved")
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "price_model.joblib")


MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models_saved")
os.makedirs(MODEL_DIR, exist_ok=True)

# Vom salva câte un fișier pentru fiecare model
MODEL_PATH_RF = os.path.join(MODEL_DIR, "price_model_rf.joblib")
MODEL_PATH_GB = os.path.join(MODEL_DIR, "price_model_gb.joblib")


@router.post("", response_model=GridResultResponseTrain1)
async def add_prediction(data: PredictionAdd, db: Session = Depends(get_db)):

    # ──────────────────────────────────
    # 1) Configurări inițiale
    # ──────────────────────────────────
    test_size: float = 0.2
    random_state: int = 42

    # 1.1) Încarcă DataFrame-ul din baza de date
    try:
        df = load_listings_as_dataframe()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare la load_listings_as_dataframe: {e}")

    # 2) Scoatem rândurile care nu au price
    df = df.dropna(subset=["price"])
    if df.shape[0] < 10:
        # Dacă nu avem suficiente date, nu merită antrenat
        raise HTTPException(status_code=400, detail="Nu există suficient de multe rânduri cu preț pentru antrenament.")

    # 3) Separăm target-ul (preț) de features
    y = df["price"].values
    X = df.drop(columns=["price"])

    # ──────────────────────────────────
    # 2) Definim preprocesarea (SI + OHE)
    # ──────────────────────────────────
    numeric_features = [
        "useful_area",
        "num_rooms",
        "num_bathrooms",
        "num_garages",
        "floor",
        "street_frontage",
        "built_area",
        # … adaugă aici orice alte coloane numerice pe care le folosești …
    ]
    categorical_features = [
        "classification",
        "land_classification",
        "city",
        # … adaugă aici orice alte coloane categorice pe care le folosești …
    ]

    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
            # poți adăuga StandardScaler() dacă vrei să scalezi
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
        ]
    )

    # ──────────────────────────────────
    # 3) Construim pipeline-uri pentru ambele modele
    # ──────────────────────────────────

    # 3.1) RandomForest
    model_rf = RandomForestRegressor(n_estimators=100, random_state=random_state)
    clf_rf = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", model_rf),
        ]
    )

    # 3.2) GradientBoosting
    model_gb = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=random_state)
    clf_gb = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", model_gb),
        ]
    )

    # ──────────────────────────────────
    # 4) Împărțim în train / test
    # ──────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    # ──────────────────────────────────
    # 5) Antrenăm RF
    # ──────────────────────────────────
    clf_rf.fit(X_train, y_train)
    y_pred_rf = clf_rf.predict(X_test)
    mae_rf = mean_absolute_error(y_test, y_pred_rf)
    rmse_rf = np.sqrt(mean_squared_error(y_test, y_pred_rf))
    print(f"[RF] MAE = {mae_rf:.2f}, RMSE = {rmse_rf:.2f}")

    # ──────────────────────────────────
    # 6) Antrenăm GB
    # ──────────────────────────────────
    clf_gb.fit(X_train, y_train)
    y_pred_gb = clf_gb.predict(X_test)
    mae_gb = mean_absolute_error(y_test, y_pred_gb)
    rmse_gb = np.sqrt(mean_squared_error(y_test, y_pred_gb))
    print(f"[GB] MAE = {mae_gb:.2f}, RMSE = {rmse_gb:.2f}")

    # ──────────────────────────────────
    # 7) Salvăm ambele modele pe disc
    # ──────────────────────────────────
    try:
        joblib.dump(clf_rf, MODEL_PATH_RF)
        print(f"Modelul RF a fost salvat la: {MODEL_PATH_RF}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare la salvarea modelului RF: {e}")

    try:
        joblib.dump(clf_gb, MODEL_PATH_GB)
        print(f"Modelul GB a fost salvat la: {MODEL_PATH_GB}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare la salvarea modelului GB: {e}")

    # ──────────────────────────────────
    # 8) (Opțional) Poți decide ce faci mai departe:
    #    - returnezi doar confirmarea
    #    - sau extinzi ConfirmationResponse ca să includă și metrica
    # ──────────────────────────────────
    return GridResultResponseTrain1(
        rf_mae=mae_rf,
        rf_rmse=rmse_rf,
        gb_mae=mae_gb,
        gb_rmse=rmse_gb,
        message="Modele antrenate cu succes"
    )

