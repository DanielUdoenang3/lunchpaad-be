from sqlalchemy import Boolean, Column, DateTime, String

from app.models.base_model import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_email_verified = Column(Boolean, default=False, nullable=False)

    # Magic link fields — used for both email verification and password reset
    magic_link_token = Column(String, nullable=True, unique=True)
    magic_link_token_expiry = Column(DateTime, nullable=True)
