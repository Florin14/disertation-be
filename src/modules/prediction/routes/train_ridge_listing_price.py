"""
Script: train_ridge_listing_price.py

Descriere:
    - Se conectează la baza de date, citește toate rândurile din tabela `listings`
      (model SQLAlchemy: ListingModel).
    - Construiește un DataFrame pandas cu feature-urile esențiale și target-ul (`price`).
    - Aplică preprocessing: imputare valori lipsă, crearea unor feature-uri noi (ex: age),
      encoding categorice și scalare numerică.
    - Antrenează un model de regresie Ridge (sklearn), cu căutare de hiperparametri
      (GridSearchCV pe `alpha`).
    - La final, afișează MAE și RMSE pe un set de test.
    - Fișierul poate fi rulat direct: python train_ridge_listing_price.py

Instrucțiuni:
    1. Setează corect conexiunea la baza de date în `DATABASE_URL`.
    2. Instalează dependențele minime: sqlalchemy, pandas, scikit-learn, psycopg2 (sau alt driver).
"""

import os
import re
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError


from sklearn.model_selection import train_test_split, GridSearchCV, KFold
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error

from modules import load_listings_from_db

# 2. Funcții auxiliare de transformare (preluate/adaptate din codul tău)
# ────────────────────────────────────────────────────────────────────

def isna(x):
    """Suport pentru pandas.isna în cazul în care nu ai importat explicit."""
    try:
        return pd.isna(x)
    except:
        return x is None

def extract_number(value, as_int=False):
    """
    Primește un `value` posibil string ce conține o valoare numerică
    și un sufix (ex: "55.00 mp", "549€"), plus și valori float/int.
    - Dacă `value` e NaN sau None → returnează None.
    - Dacă e deja float/int → direct returnează (eventual cast la int dacă as_int=True).
    - Dacă e string:
        * Caută (prin regex) primul număr (cu virgulă sau punct).
        * Dacă as_int=True: returnează int(parsed).
        * Altfel: returnează float(parsed).
    Ex: extract_number("55.00 mp") → 55.0
        extract_number("549€", as_int=True) → 549
    """

    # 1) Dacă e pandas NaN / None
    if value is None or isna(value):
        return None

    # 2) Dacă e deja numeric
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if as_int:
            try:
                return int(value)
            except (ValueError, TypeError):
                return None
        return float(value)

    # 3) Când e string (ex: "55.00 mp", "549€")
    if isinstance(value, str):
        # Eliminăm spații inutile
        s = value.strip()

        # Înlocuim virgula cu punct, ca să putem face float("12.345")
        s = s.replace(",", ".")

        # Folosim regex pentru a găsi prima apariție a unui număr (ex: '55.00', '549')
        match = re.search(r"([0-9]+(?:\.[0-9]+)?)", s)
        if match:
            num_str = match.group(1)
            try:
                num = float(num_str)
                if as_int:
                    return int(num)
                return num
            except ValueError:
                return None

    # Dacă nu se potrivește niciun caz de mai sus
    return None



def main():
    # ─── 1. Încărcare date ─────────────────────────────────────────────
    df = load_listings_from_db()
    if df.empty:
        print("Nu există date suficiente în DB sau a apărut o eroare.")
        return

    # ─── 2. Pregătirea setului X și y ─────────────────────────────────
    # Target-ul este 'price'. Eliminăm rândurile unde price e None sau zero.
    df = df[df["price"].notnull() & (df["price"] > 0)].copy()

    # Separăm target-ul
    y = df["price"].astype(float)
    X = df.drop(columns=["price", "built_year"])  # built_year l-am transformat în 'age'

    # ─── 3. Împărțire train/validation/test ──────────────────────────
    # 70% train, 15% validare, 15% test
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42
    )

    # ─── 4. Definirea feature-urilor și a pipeline-ului de preprocesare ───
    # Numerice (continuous)
    numeric_features = [
        "useful_area_total", "useful_area", "yard_area", "built_area",
        "land_area", "age", "num_kitchens", "num_rooms", "num_bathrooms", "floor"
    ]

    # Boolean (0/1) – le putem lăsa ca atare (passthrough), dar le vom include în ColumnTransformer
    boolean_features = [
        "has_parking_space", "has_garage", "has_balconies", "has_terrace", "for_sale"
    ]

    # Categoriale (text)
    categorical_features = [
        "classification", "land_classification", "city", "structure",
        "property_type", "condominium", "comfort"
    ]

    # 4.1. Pipeline pentru feature-urile numerice: imputare mediană + scalare
    numeric_transformer = Pipeline(
        steps=[
            ("imputer_num", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ]
    )

    # 4.2. Pipeline pentru feature-urile categorice: imputare constantă + one-hot encoding
    categorical_transformer = Pipeline(
        steps=[
            ("imputer_cat", SimpleImputer(strategy="constant", fill_value="missing")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ]
    )

    # 4.3. ColumnTransformer care combină cele două
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("bool", "passthrough", boolean_features),
            ("cat", categorical_transformer, categorical_features),
        ],
        remainder="drop"  # elimină orice coloană neincluse
    )

    # ─── 5. Definirea modelului și pipeline-ului complet ──────────────────
    # Aici adăugăm și GridSearchCV pentru tuning-ul lui alpha (hiperparametrul Ridge)
    ridge = Ridge(random_state=42)

    pipe = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("regressor", ridge)
        ]
    )

    # Parametri pentru GridSearch: încercăm câteva valori de alpha
    param_grid = {
        "regressor__alpha": [0.01, 0.1, 1.0, 10.0, 50.0]
    }

    # Folosim 5-fold cross-validation pentru a găsi cel mai bun alpha
    grid_search = GridSearchCV(
        pipe,
        param_grid=param_grid,
        cv=KFold(n_splits=15, shuffle=True, random_state=52),
        scoring="neg_mean_absolute_error",  # optimizăm MAE
        n_jobs=-1,
        verbose=2
    )

    # ─── 6. Antrenare ─────────────────────────────────────────────────
    print("\n[INFO] Încep antrenamentul cu GridSearchCV pentru Ridge...\n")
    grid_search.fit(X_train, y_train)

    print(f"\n[INFO] Cel mai bun parametru alpha: {grid_search.best_params_['regressor__alpha']}")
    print(f"[INFO] Cel mai bun scor MAE (pe CV): {-grid_search.best_score_:.2f}")

    # ─── 7. Evaluare pe setul de validare și test ───────────────────────
    best_model = grid_search.best_estimator_

    # Evaluare pe validare
    y_val_pred = best_model.predict(X_val)
    mae_val = mean_absolute_error(y_val, y_val_pred)
    rmse_val = np.sqrt(mean_squared_error(y_val, y_val_pred))
    print(f"\n[VALIDARE] MAE: {mae_val:.2f}, RMSE: {rmse_val:.2f}")

    # Evaluare pe test
    y_test_pred = best_model.predict(X_test)
    mae_test = mean_absolute_error(y_test, y_test_pred)
    rmse_test = np.sqrt(mean_squared_error(y_test, y_test_pred))
    print(f"[TEST] MAE: {mae_test:.2f}, RMSE: {rmse_test:.2f}\n")

    # ─── 8. Salvarea modelului antrenat ─────────────────────────────────
    # Opțional – dacă vrei să-l încarci ulterior într-un microserviciu
    import joblib
    output_model_path = "ridge_listing_price_pipeline.pkl"
    joblib.dump(best_model, output_model_path)
    print(f"[INFO] Modelul salvat în: {output_model_path}")

    # ─── 9. Recomandări pentru îmbunătățirea preciziei ───────────────────
    """
    1. Feature engineering suplimentar:
       - price_per_sqm: poți transforma ținta în preț pe mp (price / useful_area_total) 
         și, ulterior, să reconvertesti la preț total. Uneori modelele liniare sunt mai stabile pe 
         preț/mp decât pe preț total.
       - distance_to_center: dacă ai lat/lon, calculează distanța față de centrul orașului.
       - zoning_features: dacă poți grupa `city` în zone (cartiere) cu prețuri similare, folosește clustering.
       - interaction terms: (useful_area_total × num_rooms), (age × city), etc.

    2. Imputarea mai avansată a valorilor lipsă:
       - În loc de mediană, poți încerca KNN Imputer pentru variabile numerice.
       - Pentru categorice, target encoding în loc de one-hot encoding (mai ales când există multe categorii unice).

    3. Alte modele de referință:
       - RandomForestRegressor, LightGBM și CatBoost. De regulă, aceste modele non-liniare vor scoate un
         RMSE/MAE mai bun decât o regresie liniară pe date imobiliare.
         Dacă ai coloană `city` cu multe valori distincte (>30), target encoding (scikit-learn's OrdinalEncoder
         + impact coding manual) poate ajuta Ridge să prindă efectele de zonă.

    4. Tuning mai amplu al hiperparametrilor:
       - În loc de GridSearchCV, poți folosi RandomizedSearchCV sau Optuna pentru a căuta `alpha` și 
         eventual parametri noi (ex: `solver="saga"` la Ridge și `max_iter`).
    """

main()