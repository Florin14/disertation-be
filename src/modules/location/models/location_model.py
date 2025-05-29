from sqlalchemy import Column, Integer, Text, Numeric

from extensions import BaseModel


class LocationModel(BaseModel):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    county = Column(Text)
    latitude = Column(Numeric(9, 6), index=True)
    longitude = Column(Numeric(9, 6), index=True)
