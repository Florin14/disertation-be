from datetime import datetime
from typing import Optional

from project_helpers.schemas import BaseSchema


class PerformanceCreate(BaseSchema):
    model_name: str
    mae: float
    rmse: float
    r2: float
    created_at: Optional[datetime] = None
