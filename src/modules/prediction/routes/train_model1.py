import os

import joblib
import numpy as np
from fastapi import Depends
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sqlalchemy.orm import Session

from extensions import get_db
from modules.prediction.routes.helpers import load_listings_as_dataframe
from project_helpers.responses import ConfirmationResponse
from .router import router
from ..models import PredictionAdd

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models_saved")
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "price_model.joblib")


@router.post("", response_model=ConfirmationResponse)
async def add_prediction(data: PredictionAdd, db: Session = Depends(get_db)):
    # 2) Separăm target-ul (prețul) de features
    test_size: float = 0.2
    random_state: int = 42
    df = load_listings_as_dataframe()

    # 2) Scoatem rândurile care n-au price
    df = df.dropna(subset=["price"])

    # 3) Separăm target-ul de features
    y = df["price"].values
    X = df.drop(columns=["price"])

    # 3) Identificăm tipurile de coloane:
    numeric_features = [
        "useful_area",
        "num_rooms",
        "num_bathrooms",
        "num_garages",
        "floor",
        "street_frontage",
        "built_area",
        # … orice câmp numeric ai mai vrea în model …
    ]
    categorical_features = [
        "classification",
        "land_classification",
        "city",
        # … oricare altă coloană text pe care vrei să o encodezi …
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

    # 5) Modelul de regresie (RandomForest)
    model = RandomForestRegressor(n_estimators=100, random_state=random_state)

    # 6) Pipeline final: preprocesor + model
    clf = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", model),
        ]
    )

    # 7) Împărțim în train / test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    # 8) Antrenăm
    clf.fit(X_train, y_train)

    # 9) Evaluare pe setul de test
    y_pred = clf.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    print(f"Model RandomForest: MAE = {mae:.2f}, RMSE = {rmse:.2f}")

    # 10) Salvăm întreg pipeline-ul pe disc cu joblib
    joblib.dump(clf, MODEL_PATH)
    print(f"Modelul a fost salvat la: {MODEL_PATH}")
    return ConfirmationResponse()
