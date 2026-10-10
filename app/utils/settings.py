from pydantic_settings import BaseSettings
from decouple import config
from pathlib import Path

# Project root (two levels up from this file: utils/ → app/ → project root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    """Class to hold application's config values."""

    SECRET_KEY: str = config("SECRET_KEY")
    BASE_DIR:str = config("BASE_DIR")
    JWT_ALGORITHM: str = config("JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRES_IN: int = config("ACCESS_TOKEN_EXPIRES_IN")
    REFRESH_TOKEN_EXPIRES_IN: int = config("REFRESH_TOKEN_EXPIRES_IN")

    FE_URL: str = config("FE_URL")

    # Database configurations
    DB_HOST: str = config("DB_HOST")
    DB_PORT: int = config("DB_PORT", cast=int)
    DB_USER: str = config("DB_USER")
    DB_PASSWORD: str = config("DB_PASSWORD")
    DB_NAME: str = config("DB_NAME")
    DB_TYPE: str = config("DB_TYPE")
    DB_URL: str = config("DB_URL")

    # Email (Resend)
    RESEND_API_KEY: str = config("RESEND_API_KEY")
    RESEND_EMAIL: str = config("RESEND_EMAIL")

    # Magic link frontend redirect URLs
    VERIFY_LINK: str = config("VERIFY_LINK")
    FORGOT_PWD_LINK: str = config("FORGOT_PWD_LINK")

settings = Settings()