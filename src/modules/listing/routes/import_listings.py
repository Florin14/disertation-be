from pathlib import Path

import pandas as pd
from fastapi import Depends
from sqlalchemy.orm import Session

from extensions import get_db
from .router import router
from ..models import ListingModel, ListingAdd


@router.post("-import")
async def import_listings(data: ListingAdd, db: Session = Depends(get_db)):
    routes_dir = Path(__file__).resolve().parent  # .../routes
    listing_dir = routes_dir.parent  # .../modules/listing
    csv_path = listing_dir / "data" / "housing_price_prediction_boston.csv"

    if not csv_path.exists():
        raise RuntimeError(f"CSV not found at {csv_path}")
    df = pd.read_csv(csv_path)
    for _, row in df.iterrows():
        print(df.get('name'))
    #     listing = ListingModel(
    #         name=row["name"],
    #         neighbourhood=row["neighbourhood"],
    #         latitude=row["latitude"],
    #         longitude=row["longitude"],
    #         price=row["price"],
    #         room_type=row["room_type"],
    #         minimum_nights=row["minimum_nights"],
    #     )
    #     db.add(listing)
    # db.commit()
    db.close()
