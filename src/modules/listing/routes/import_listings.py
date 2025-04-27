from fastapi import Depends
from sqlalchemy.orm import Session
import pandas as pd
from extensions import get_db
from .router import router
from ..models import ListingModel, ListingAdd, ListingResponse


@router.post("-import")
async def import_listings(data: ListingAdd, db: Session = Depends(get_db)):
    file_path = "data/listings.csv"
    df = pd.read_csv(file_path)
    for _, row in df.iterrows():
        listing = ListingModel(
            name=row["name"],
            neighbourhood=row["neighbourhood"],
            latitude=row["latitude"],
            longitude=row["longitude"],
            price=row["price"],
            room_type=row["room_type"],
            minimum_nights=row["minimum_nights"],
        )
        db.add(listing)
    db.commit()
    db.close()
