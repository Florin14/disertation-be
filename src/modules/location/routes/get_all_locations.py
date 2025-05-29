from sqlalchemy.orm import Session
from .router import router
from fastapi import Depends
from extensions import get_db

from modules.location.models.location_model import LocationModel
from modules.location.models.location_schemas import LocationFilter, LocationListResponse

@router.get("", response_model=LocationListResponse)
async def get_all_location(query: LocationFilter = Depends(), db: Session = Depends(get_db)):
    locationQuery = db.query(LocationModel)

    locationQuery = locationQuery.order_by(getattr(getattr(LocationModel, query.sortBy), query.sortType)())
    qty = locationQuery.count()
    if None not in [query.offset, query.limit]:
        locationQuery = locationQuery.offset(query.offset).limit(query.limit)
    return LocationListResponse(quantity=qty, items=locationQuery.all())
