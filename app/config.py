from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    db_hostname: Optional[str] = None
    db_port: Optional[str] = None
    db_password: Optional[str] = None
    db_name: Optional[str] = None
    db_username: Optional[str] = None

    debug: bool
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: Optional[str] = None

    gemini_api_key: str

    class Config:
        env_file = ".env"


settings = Settings()
