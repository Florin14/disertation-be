from pydantic import Field
from pydantic_settings import BaseSettings
from constants import PlatformEnvs


class PlatformConfig(BaseSettings):
    ENV: PlatformEnvs = Field(PlatformEnvs.LOCAL, env="ENV")
    PLATFORM_NAME: str = Field("template", env="PLATFORM_NAME")
    SECRET_KEY: str = Field("c7482ee1fd8f4c2a802dfca49e29e076", env="JWT_SECRET_KEY")
    BASE_URL: str = Field("http://localhost:8002", env="BASE_URL")
    FRONTEND_URL: str = Field("http://localhost:8002", env="FRONTEND_URL")
    TEMPORARY_PASSWORD_EXPIRATION_SECONDS: int = 172800


platformConfig = PlatformConfig()
