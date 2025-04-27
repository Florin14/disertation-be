from fastapi import Depends
from sqlalchemy.orm import Session

from extensions import get_db
from .router import router
from ..models import ListingModel, ListingAdd, ListingResponse


@router.post("", response_model=ListingResponse)
async def add_listing(data: ListingAdd, db: Session = Depends(get_db)):
    listing = ListingModel(**data.dict())

    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing
