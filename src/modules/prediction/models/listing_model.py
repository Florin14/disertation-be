from datetime import datetime

from sqlalchemy import Column, BigInteger, Integer, DateTime, Float, Text, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from constants import ListingSource
from extensions import BaseModel


class ListingModel(BaseModel):
    __tablename__ = "listings"

    id = Column(BigInteger, primary_key=True, index=True)
    external_id = Column(Text, unique=True, index=True)
    source = Column(Enum(ListingSource))
    location_id = Column(Integer, ForeignKey("locations.id"))
    listing_type = Column(Enum("SALE", "RENT", name="listing_type_enum"))
    property_type = Column(Enum("APARTMENT", "HOUSE", "LAND", "OFFICE", name="property_type_enum"))
    surface = Column(Float)
    rooms = Column(Integer)
    year_built = Column(Integer)
    raw_payload = Column(JSONB)  # tot XML/JSON brut pt. debugging
    inserted_at = Column(DateTime, default=lambda: datetime.now())

    location = relationship("LocationModel", backref="listings")
