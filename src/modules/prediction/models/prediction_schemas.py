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


class SimilarListing(BaseSchema):
    external_id: str
    price_per_sqm: float
    num_rooms: int
    city: str
    score: float
    location_raw: str
    useful_area: float
    total_price: float
    latitude: float
    longitude: float


class PredictionListResponse(BaseSchema):
    quantity: int
    items: List[PredictionItem]


class PredictionBase(BaseSchema):
    # ─────────────────────────────────────────────────────────────────────────
    # NUMERIC features
    user_id: Optional[int] = None
    useful_area: Optional[float] = None
    built_area: Optional[float] = None
    useful_area_total: Optional[float] = None
    land_area: Optional[float] = None
    yard_area: Optional[float] = None
    num_rooms: Optional[int] = None
    num_bathrooms: Optional[int] = None
    # We receive number of garages; we’ll convert this to `has_garage` (bool) downstream.
    has_garage: Optional[bool] = False
    floor: Optional[int] = None
    built_year: Optional[int] = None

    # ─────────────────────────────────────────────────────────────────────────
    # CATEGORICAL features
    classification: Optional[str] = None
    land_classification: Optional[str] = None
    street_frontage: Optional[float] = None  # This is a numeric feature, but often treated as categorical.
    city: Optional[str] = None
    condominium: Optional[str] = None
    num_kitchens: Optional[int] = None
    # We’ll convert this to `has_parking_space` (bool) in prepare_input_for_prediction().
    num_parking_spaces: Optional[int] = None

    has_terrace: Optional[bool] = None
    has_balconies: Optional[bool] = None
    comfort: Optional[str] = None
    property_type: Optional[str] = None
    structure: Optional[str] = None
    address: Optional[str] = None
    price: Optional[float] = None
    # We’ll compute `for_sale` (bool) from a threshold on `predicted_price` or input price.
    # If you want to pass it explicitly, you can:
    for_sale: Optional[bool] = False
    has_parking_space: Optional[bool] = False
    hospital_dist_km: Optional[float] = 0.0
    subway_dist_km: Optional[float] = 0.0
    bus_stop_dist_km: Optional[float] = 0.0
    school_dist_km: Optional[float] = 0.0
    ratio_balcony_useful: Optional[float] = 60.0
    ratio_terrace_useful: Optional[float] = 60.0
    ratio_yard_useful: Optional[float] = 60.0
    ratio_built_useful: Optional[float] = 60.0


class PredictionResponse(BaseSchema):
    # id: int
    predicted_price: float
    location_raw: str
    accuracy_pct: Optional[float] = None
    # created_at: datetime
    similar_listings: List[SimilarListing] = []


class GridResultResponseTrain1(BaseSchema):
    best_model: str
    rf_mae_ppsm: float
    rf_rmse_ppsm: float
    gb_mae_ppsm: float
    gb_rmse_ppsm: float


class GridResultResponse(BaseSchema):
    best_model: str
    rf_mae_ppsm: float
    rf_rmse_ppsm: float
    # gb_mae_ppsm: float
    # gb_rmse_ppsm: float
