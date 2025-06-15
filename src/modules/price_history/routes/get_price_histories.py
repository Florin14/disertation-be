from fastapi import Depends
from sqlalchemy.orm import Session

from extensions import get_db
from modules.price_history.models.price_history_model import PriceHistoryModel
from modules.price_history.models.price_history_schemas import PriceHistoryListResponse, PriceHistoryFilter
from .router import router


@router.get("", response_model=PriceHistoryListResponse)
async def get_all_price_histories(query: PriceHistoryFilter = Depends(), db: Session = Depends(get_db)):
    priceHistoryQuery = db.query(PriceHistoryModel).filter(PriceHistoryModel.user_id == query.user_id)

    priceHistoryQuery = priceHistoryQuery.order_by(getattr(getattr(PriceHistoryModel, query.sortBy), query.sortType)())
    if None not in [query.offset, query.limit]:
        priceHistoryQuery = priceHistoryQuery.offset(query.offset).limit(query.limit)
    return PriceHistoryListResponse(items=priceHistoryQuery.all())
