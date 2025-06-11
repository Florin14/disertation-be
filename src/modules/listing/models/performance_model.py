from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, Float, String

from extensions import BaseModel


class PerformanceModel(BaseModel):
    __tablename__ = "model_performances"
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    mae = Column(Float, nullable=False)
    rmse = Column(Float, nullable=False)
    r2 = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(), nullable=False)
