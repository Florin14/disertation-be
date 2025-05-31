from sqlalchemy.orm import Session
from .router import router
from fastapi import Depends
from extensions import get_db
from ..models import PredictionsModel, PredictionFilter, PredictionListResponse


@router.get("", response_model=PredictionListResponse)
async def get_all_predictions(query: PredictionFilter = Depends(), db: Session = Depends(get_db)):
    predictionQuery = db.query(PredictionsModel)

    predictionQuery = predictionQuery.order_by(getattr(getattr(PredictionsModel, query.sortBy), query.sortType)())
    qty = predictionQuery.count()
    if None not in [query.offset, query.limit]:
        predictionQuery = predictionQuery.offset(query.offset).limit(query.limit)
    return PredictionListResponse(quantity=qty, items=predictionQuery.all())
