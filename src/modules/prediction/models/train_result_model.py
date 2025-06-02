from datetime import datetime

from sqlalchemy import Column, BigInteger, Integer, DateTime, Float, Text

from extensions import BaseModel


class TrainResultModel(BaseModel):
    __tablename__ = "train_results"

    id = Column(BigInteger, primary_key=True, index=True)
    mae = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now())
