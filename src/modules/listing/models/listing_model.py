from sqlalchemy import Column, Integer, String, Float

from extensions import BaseModel


class ListingModel(BaseModel):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    price = Column(Float)
    minimum_nights = Column(Integer)
