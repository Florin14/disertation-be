
from typing import List
from typing import Optional

from fastapi import Query
from pydantic import EmailStr
from pydantic import Field
from pydantic import field_validator

from constants.platform_roles import PlatformRoles
from project_helpers.schemas import BaseSchema
from project_helpers.schemas import FilterSchema


class ClientAdd(BaseSchema):
    email: EmailStr = Field(..., min_length=1, max_length=40, example="florin.zimbru@gmail.com")
    name: str = Field(..., min_length=1, max_length=50, example="Zimbru Florin")
    phoneNumber: str = Field(..., min_length=1, max_length=40, example="0742412344")


class ClientItem(BaseSchema):
    id: int
    email: str
    name: str
    phoneNumber: Optional[str]
    role: PlatformRoles
    isAvailable: bool


class ClientsListResponse(BaseSchema):
    quantity: int
    items: List[ClientItem]


class ClientUpdate(BaseSchema):
    name: Optional[str] = None
    phoneNumber: Optional[str] = None
    agentId: Optional[int] = None


class ClientsFilter(FilterSchema):
    sortBy: Optional[str] = "name"


class ClientRegister(BaseSchema):
    email: str = Field(..., min_length=1, max_length=40, example="zimbru.florin.4@gmail.com")
    name: str = Field(..., min_length=1, max_length=50, example="Zimbru Florin")
    phoneNumber: str = Field(..., min_length=1, max_length=40, example="0742412344")
    password: str = Field(..., min_length=1, max_length=40, example="pass")
    confirmPassword: str = Field(...)


class ClientResponse(BaseSchema):
    id: int
    email: str
    name: str
    phoneNumber: Optional[str]
