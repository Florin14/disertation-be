from typing import List

from project_helpers.schemas import BaseSchema, FilterSchema


class PriceHistoryFilter(FilterSchema):
    user_id: int

class HistoryItem(BaseSchema):
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


class PriceHistoryListResponse(BaseSchema):
    items: List[HistoryItem]
