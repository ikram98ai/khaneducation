from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_hostname: str
    db_port: str
    db_password: str
    db_name: str
    db_username: str

    debug: bool
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str

    gemini_api_key: str

    class Config:
        env_file = ".env"


settings = Settings()
