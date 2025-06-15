from datetime import datetime
from typing import Optional

from project_helpers.schemas import BaseSchema


class PerformanceCreate(BaseSchema):
    model_name: str
    mae: float
    rmse: float
    r2: float
    created_at: Optional[datetime] = None


class HistoryCreate(BaseSchema):
    base_location: str
    price_per_sqm: float
    predicted_price: float
    location_raw: str
    num_rooms: int
    city: str
    useful_area: float
    total_price: float
    latitude: float
    longitude: float
    user_id: Optional[int] = None