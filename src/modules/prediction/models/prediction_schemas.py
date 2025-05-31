from datetime import datetime
from typing import List, Optional

from project_helpers.schemas import BaseSchema, FilterSchema


class PredictionAdd(BaseSchema):
    pass


class PredictionUpdate(BaseSchema):
    pass


class PredictionFilter(FilterSchema):
    sortBy: str = "companyName"


class PredictionItem(BaseSchema):
    pass


class PredictionListResponse(BaseSchema):
    quantity: int
    items: List[PredictionItem]


class PredictionBase(BaseSchema):
    # ───────────────────────────────────────────────────────────────────────────
    # Definim AICI aceleași coloane din PredictionsModel (excluzând id/predicted_price/created_at)
    # ───────────────────────────────────────────────────────────────────────────
    useful_area: Optional[float] = None
    num_rooms: Optional[int] = None
    num_bathrooms: Optional[int] = None
    num_garages: Optional[int] = None
    floor: Optional[int] = None
    street_frontage: Optional[float] = None
    built_area: Optional[float] = None
    # … adaugă aici orice altă coloană numerică de la PredictionsModel …

    classification: Optional[str] = None
    land_classification: Optional[str] = None
    city: Optional[str] = None
    # … adaugă aici orice altă coloană text de la PredictionsModel …


class PredictionResponse(PredictionBase):
    id: int
    predicted_price: float
    created_at: datetime
