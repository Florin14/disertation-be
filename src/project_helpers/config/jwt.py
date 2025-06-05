from extensions.auth_jwt import AuthJWT
from typing import List
import os
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from datetime import timedelta
from pathlib import Path
BASE_DIR = Path(__file__).parent  # the folder containing jwt.py


class JwtConfig(BaseSettings):
    authjwt_secret_key: str = Field("c7482ee1fdaa4c2a802dfca49e29e077", env="JWT_SECRET_KEY")
    authjwt_token_location: List[str] = ["cookies"]
    authjwt_cookie_csrf_protect: bool = False
    # point at the absolute PEM files
    authjwt_public_key: str = Field(str(BASE_DIR / "public-key.pem"), env="JWT_PUBLIC_KEY")
    authjwt_private_key: str = Field(str(BASE_DIR / "private-key.pem"), env="JWT_PRIVATE_KEY")
    authjwt_access_token_expires: timedelta = Field(
        timedelta(seconds=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 7200))),
        env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    authjwt_refresh_token_expires: timedelta = Field(
        timedelta(seconds=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_MINUTES", 84600))),
        env="JWT_REFRESH_TOKEN_EXPIRE_MINUTES",
    )
    authjwt_cookie_secure: bool = Field(True, env="JWT_COOKIE_SECURE")
    authjwt_cookie_samesite: str = Field("none", env="JWT_COOKIE_SAMESITE")
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: List[str] = ["access", "refresh"]

    @validator("authjwt_public_key", "authjwt_private_key")
    def keys_validator(cls, path):
        with open(path, "r") as file:
            return file.read()


@AuthJWT.load_config
def jwt_config():
    config = JwtConfig()
    return config
