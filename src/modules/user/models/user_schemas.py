from typing import List, Optional

from pydantic import Field

from constants.platform_roles import PlatformRoles
from project_helpers.schemas import BaseSchema, FilterSchema


class UserAdd(BaseSchema):
    email: str = Field(..., max_length=40, example="zimbru.florin.4@gmail.com")
    name: str = Field(..., max_length=50, example="Zimbru Florin")
    role: PlatformRoles = Field(..., example=PlatformRoles.ADMIN)
    password: str

class UserItem(BaseSchema):
    id: int
    name: str
    role: str
    email: str


class UserFilter(FilterSchema):
    sortBy: str = "companyName"


class UserResponse(BaseSchema):
    id: int
    name: str
    role: str
    email: str


class UserListResponse(BaseSchema):
    data: List[UserItem] = []
