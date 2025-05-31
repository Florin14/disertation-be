from http.client import HTTPException

from fastapi import Depends
from sqlalchemy.orm import Session

from extensions import get_db
from modules.prediction.models.prediction_schemas import PredictionResponse
from modules.prediction.routes.helpers import get_prediction

from .router import router


@router.get(
    "/{id}",
    response_model=PredictionResponse,
    summary="Returnează o predicție existentă după ID"
)
async def read_prediction(
        id: int,
        db: Session = Depends(get_db)
):
    db_pred = get_prediction(db, id)
    if db_pred is None:
        raise HTTPException(status_code=404, detail="Predicirea nu a fost găsită.")
    return db_pred
