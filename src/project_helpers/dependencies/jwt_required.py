from typing import List
from fastapi import Depends
from extensions.auth_jwt import AuthJWT
from constants import PlatformRoles
from project_helpers.error import Error
from project_helpers.exceptions import ErrorException


class JwtRequired:
    def __init__(self, roles: List[PlatformRoles] = None):
        self.roles = roles

    def __call__(self, auth: AuthJWT = Depends()):
        auth.jwt_required()
        claims = auth.get_raw_jwt()
        role = claims and claims.get("role") or "Unknown"
        if self.roles:
            if role not in self.roles:
                raise ErrorException(
                    error=Error.USER_UNAUTHORIZED,
                    statusCode=403,
                    message=f"User must have one of following roles: {self.roles} "
                    f"to use this operation but you have {role}!",
                )
