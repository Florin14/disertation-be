from sqlalchemy.orm import Session
from .router import router
from fastapi import Depends
from extensions import get_db
from ..models import ListingModel, ListingFilter, ListingListResponse


@router.get("", response_model=ListingListResponse)
async def get_all_listing(query: ListingFilter = Depends(), db: Session = Depends(get_db)):
    listingQuery = db.query(ListingModel)

    listingQuery = listingQuery.order_by(getattr(getattr(ListingModel, query.sortBy), query.sortType)())
    qty = listingQuery.count()
    if None not in [query.offset, query.limit]:
        listingQuery = listingQuery.offset(query.offset).limit(query.limit)
    return ListingListResponse(quantity=qty, items=listingQuery.all())
