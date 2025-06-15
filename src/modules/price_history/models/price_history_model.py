from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, BigInteger, DateTime

from extensions import BaseModel


class PriceHistoryModel(BaseModel):
    __tablename__ = "price_history"

    id = Column(BigInteger, primary_key=True, index=True)
    base_location = Column(String)
    location_raw = Column(String)
    price_per_sqm = Column(Float)
    predicted_price = Column(Float)
    user_id = Column(BigInteger, nullable=True)  # Nullable for anonymous users

    num_rooms = Column(Integer)
    city = Column(String)
    useful_area = Column(Float)
    total_price = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(), nullable=False)

