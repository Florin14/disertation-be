from typing import List, Optional

from fastapi import Query
from pydantic import field_validator, Field

from project_helpers.schemas import BaseSchema, FilterSchema


class ListingAdd(BaseSchema):
    companyName: str = Field(..., min_length=1)
    cui: str = Field(..., min_length=1)
    registrationNumber: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    phoneNumber: str = Field(..., min_length=1)
    bankAccount: str = Field(..., min_length=1)
    bankName: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    county: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)


class ListingUpdate(BaseSchema):
    companyName: Optional[str] = Field(None, min_length=1)
    cui: Optional[str] = Field(None, min_length=1)
    registrationNumber: Optional[str] = Field(None, min_length=1)
    address: Optional[str] = Field(None, min_length=1)
    bankName: Optional[str] = Field(None, min_length=1)
    bankAccount: Optional[str] = Field(None, min_length=1)
    name: Optional[str] = Field(None, min_length=1)
    phoneNumber: Optional[str] = Field(None, min_length=1)
    county: Optional[str] = Field(None, min_length=1)
    city: Optional[str] = Field(None, min_length=1)


class ListingFilter(FilterSchema):
    sortBy: str = "companyName"


class ListingResponse(BaseSchema):
    id: int
    companyName: str
    cui: str
    registrationNumber: str
    bankName: str
    bankAccount: str
    address: str
    name: str
    phoneNumber: str
    email: str
    city: str
    county: str


class ListingItem(BaseSchema):
    id: int
    companyName: str
    cui: str
    registrationNumber: str
    address: str
    name: str
    email: str
    county: str
    city: str
    phoneNumber: str
    bankAccount: str
    bankName: str


class ListingListResponse(BaseSchema):
    quantity: int
    items: List[ListingItem]
