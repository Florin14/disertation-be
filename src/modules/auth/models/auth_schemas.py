
from typing import Optional
from constants import PlatformRoles
from project_helpers.schemas import BaseSchema


class LoginBody(BaseSchema):
    email: str = "cicada.cws@gmail.com"
    password: str = "Cicada@2016"
    recaptchaToken: Optional[str] = None


class LoginResponse(BaseSchema):
    id: int
    name: str
    role: PlatformRoles
    isDeleted: bool
    hasDefaultPassword: bool
    isAvailable: bool
    companyName: Optional[str] = None
