
from typing import Optional
from constants import PlatformRoles
from project_helpers.schemas import BaseSchema


class LoginBody(BaseSchema):
    email: str = "zimbru.florin.4@gmail.com"
    password: str = "Castigator1."
    recaptchaToken: Optional[str] = None


class LoginResponse(BaseSchema):
    id: int
    name: str
    role: PlatformRoles
    isDeleted: bool
    hasDefaultPassword: bool
    isAvailable: bool
    companyName: Optional[str] = None
