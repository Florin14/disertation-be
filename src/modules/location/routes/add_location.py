from fastapi import Depends
from sqlalchemy.orm import Session

from extensions import get_db
from .router import router
from modules.location.models.location_model import LocationModel
from modules.location.models.location_schemas import LocationAdd, LocationResponse


@router.post("", response_model=LocationResponse)
async def add_location(data: LocationAdd, db: Session = Depends(get_db)):
    location = LocationModel(**data.dict())

    db.add(location)
    db.commit()
    db.refresh(location)
    return location
