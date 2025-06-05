from datetime import datetime

from sqlalchemy import Column, BigInteger, Integer, DateTime, Float, Text

from extensions import BaseModel


class PredictionsModel(BaseModel):
    __tablename__ = "predictions"

    id = Column(BigInteger, primary_key=True, index=True)
    # 1) Salvăm toate câmpurile folosite pentru predicție
    #    – folosește exact aceleași tipuri ca în ListingModel,
    #      pentru a fi ușor de mapat din JSON → obiect SQLAlchemy
    useful_area = Column(Float, nullable=True)
    num_rooms = Column(Integer, nullable=True)
    num_bathrooms = Column(Integer, nullable=True)
    num_garages = Column(Integer, nullable=True)
    floor = Column(Integer, nullable=True)
    # … adaugă orice alte câmpuri relevante pe care
    #    le-ai folosit în antrenament (ex.: classification,
    #    land_classification, city, address etc.) …
    classification = Column(Text, nullable=True)
    land_classification = Column(Text, nullable=True)
    city = Column(Text, nullable=True)

    built_area = Column(Float, nullable=True)
    # … alte câmpuri (la fel cum ai definit în ListingModel) …

    # 2) Rezultatul predicției
    predicted_price = Column(Float, nullable=False)

    # 3) Păstrează timestamp‐ul la care s-a făcut predicția
    created_at = Column(DateTime, default=lambda: datetime.now())
