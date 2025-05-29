from decimal import Decimal
from typing import List, Optional

from pydantic import Field, validator

from project_helpers.schemas import BaseSchema, FilterSchema


class LocationAdd(BaseSchema):
    name: str = Field(..., min_length=1)
    county: str = Field(..., min_length=1)
    latitude: Decimal = Field(
        ...,
        ge=-90,
        le=90,
        description="Latitudine în grade, nord pozitiv, șase zecimale."
    )
    longitude: Decimal = Field(
        ...,
        ge=-180,
        le=180,
        description="Longitudine în grade, est pozitiv, șase zecimale."
    )

    @validator("latitude", "longitude", pre=True, always=True)
    def round_six_decimals(cls, v):
        return round(Decimal(v), 6)


class LocationUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1)
    county: Optional[str] = Field(None, min_length=1)
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)

    @validator("latitude", "longitude", pre=True, always=True)
    def round_six_decimals(cls, v):
        if v is None:
            return v
        return round(Decimal(v), 6)


class LocationFilter(FilterSchema):
    sortBy: str = "companyName"


class LocationResponse(BaseSchema):
    id: int
    name: str
    county: str
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]


class LocationItem(BaseSchema):
    id: int
    name: str
    county: str
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]


class LocationListResponse(BaseSchema):
    quantity: int
    items: List[LocationItem]
