# # app/routers/predict.py
# import os
# import joblib
# import numpy as np
# import pandas as pd
# from fastapi import Depends, HTTPException
# from sqlalchemy.orm import Session
#
# from extensions import get_db
# from modules.prediction.models.prediction_schemas import PredictionBase, PredictionResponse
# from .model_path import MODEL_PATH
# from .router import router
# from ..utils import prepare_input_for_prediction
#
# if not os.path.isfile(MODEL_PATH):
#     raise RuntimeError(f"Modelul nu a fost găsit la: {MODEL_PATH}. Rulează mai întâi /train.")
#
# try:
#     model_pipeline = joblib.load(MODEL_PATH)
# except Exception as e:
#     raise RuntimeError(f"Eroare la încărcarea modelului: {e}")
#
# @router.post("-predict", response_model=PredictionResponse)
# async def make_prediction(
#     payload: PredictionBase,
#     db: Session = Depends(get_db)
# ):
#     # 1) Pregătirea input-ului
#     try:
#         df_input = prepare_input_for_prediction(payload.dict())
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Eroare la pregătirea input-ului: {e}")
#
#     # 2) Predict
#     try:
#         y_pred = model_pipeline.predict(df_input)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Eroare la execuția predict: {e}")
#
#     if len(y_pred) == 0:
#         raise HTTPException(status_code=500, detail="Modelul nu a returnat nicio valoare.")
#
#     predicted_price = float(y_pred[0])
#
#     # 3) Calculul procentului de acuratețe, dacă s-a furnizat price în payload
#     accuracy_pct = None
#     if payload.price is not None and payload.price > 0:
#         actual_price = payload.price
#         error = abs(predicted_price - actual_price)
#         accuracy_pct = max(0.0, 100.0 * (1 - error / actual_price))
#
#     # 4) (Opțional) Salvează predicția în DB
#     # db_entry = create_prediction(db, payload, predicted_price)
#
#     # 5) Returnează răspunsul
#     return PredictionResponse(
#         predicted_price=predicted_price,
#         accuracy_pct=accuracy_pct
#     )


import os

import joblib
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from extensions import get_db
from modules.prediction.models.prediction_schemas import PredictionBase, PredictionResponse, SimilarListing
from modules.prediction.routes.helpers import load_listings_as_dataframe
from .model_path import MODEL_PATH
from .router import router
from ..utils import prepare_input_for_prediction
from ...listing.models.performance_schemas import HistoryCreate
from ...listing.routes.helpers import create_history

# ─── ÎNCARCĂ MODELUL ─────────────────────────────────────────────────────────
if not os.path.isfile(MODEL_PATH):
    raise RuntimeError(f"Model not found: {MODEL_PATH}. Run /train first.")
model = joblib.load(MODEL_PATH)

# ─── LOAD FULL LISTINGS FOR similarity ───────────────────────────────────────
df_all = load_listings_as_dataframe()


# compute price_per_sqm and POI distances for df_all (similar to training)
# TODO: reuse same POI code as above in training

@router.post("-predict", response_model=PredictionResponse)
async def make_prediction(payload: PredictionBase, db: Session = Depends(get_db)):
    # 1) Prepare single‐row df_input
    print(payload.dict())
    try:
        df_input = prepare_input_for_prediction(payload.dict())
    except Exception as e:
        raise HTTPException(400, f"Input prep error: {e}")

    # 2) Predict price
    y_pred = model.predict(df_input)[0]
    # 3) Compute accuracy if payload.price
    accuracy = None
    if payload.price:
        err = abs(y_pred - payload.price)
        accuracy = max(0.0, 100.0 * (1 - err / payload.price))

    # 4) Find top5 similar listings
    # Compute features for df_all and df_input for similarity keys:
    #   price_per_sqm within ±10, num_rooms ±1
    df_all["price_per_sqm"] = df_all.price / df_all.useful_area
    df_all["diff_price"] = abs(df_all.price_per_sqm - y_pred)
    df_all["diff_rooms"] = abs(df_all.num_rooms - (payload.num_rooms or 0))
    # filter by tolerances
    candidates = df_all[
        (df_all["diff_price"] <= 10) &
        (df_all["diff_rooms"] <= 1)
        ].copy()
    # sort by combined diff
    candidates["score"] = candidates["diff_price"] + candidates["diff_rooms"]
    top5 = candidates.nsmallest(5, "score")

    initialLocation = payload.city + " " + payload.address or ""
    similar = []
    for _, row in top5.iterrows():
        similar.append(SimilarListing(
            external_id=row.external_id,
            price_per_sqm=row.price_per_sqm,
            num_rooms=row.num_rooms,
            city=row.city,
            score=float(row.score),
            location_raw=row.location_raw,
            useful_area=row.useful_area_total,
            total_price=row.price,
            latitude=row.latitude,
            longitude=row.longitude,
        ))

        history = HistoryCreate(
            base_location=initialLocation,
            price_per_sqm=row.price_per_sqm,
            predicted_price=y_pred * payload.useful_area,
            location_raw=row.location_raw,
            num_rooms=row.num_rooms,
            city=row.city,
            useful_area=row.useful_area,
            total_price=row.price,
            latitude=row.latitude,
            longitude=row.longitude,
            user_id=payload.user_id or None,
        )
        create_history(history)

    return PredictionResponse(
        predicted_price=y_pred * payload.useful_area,
        accuracy_pct=accuracy,
        similar_listings=similar,
        location_raw=payload.address,
    )
