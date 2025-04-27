from pydantic import Field
from pydantic_settings import BaseSettings
from constants import PlatformEnvs


class PlatformConfig(BaseSettings):
    ENV: PlatformEnvs = Field(PlatformEnvs.LOCAL, env="ENV")
    PLATFORM_NAME: str = Field("template", env="PLATFORM_NAME")
    SECRET_KEY: str = Field("123", env="JWT_SECRET_KEY")
    BASE_URL: str = Field("http://localhost:8002", env="BASE_URL")
    FRONTEND_URL: str = Field("http://localhost:8002", env="FRONTEND_URL")
    TEMPORARY_PASSWORD_EXPIRATION_SECONDS: int = 172800


platformConfig = PlatformConfig()
