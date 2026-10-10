import secrets
from datetime import datetime, timedelta

from fastapi import status
from sqlalchemy.orm import Session

from app.models import base as models
from app.models.base import User
from app.schema.base import UserCreate, UserLogin
from app.services.email_services import send_verification_email, send_password_reset_email
from app.utils.custom_response import error_response, success_response
from app.utils.pass_hash import hash_password, verify_password
from app.utils.token import create_access_token

# How long a magic link remains valid
MAGIC_LINK_EXPIRY_MINUTES = 30


# ── Internal helpers ──────────────────────────────────────────────────────────

def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_magic_token(db: Session, token: str) -> models.User | None:
    return db.query(models.User).filter(models.User.magic_link_token == token).first()


def _generate_and_send_magic_link(db: Session, user: models.User, purpose: str) -> None:
    """
    Generate a cryptographically secure token, persist it, and dispatch the email.

    purpose: "verify" → email verification link
             "reset"  → password reset link
    """
    token = secrets.token_urlsafe(32)
    expiry = datetime.utcnow() + timedelta(minutes=MAGIC_LINK_EXPIRY_MINUTES)

    user.magic_link_token = token
    user.magic_link_token_expiry = expiry
    db.add(user)
    db.commit()
    db.refresh(user)

    if purpose == "verify":
        send_verification_email(
            to_email=user.email,
            name=user.first_name,
            token=token,
        )
    else:
        send_password_reset_email(
            to_email=user.email,
            token=token,
        )


async def create_user(data: UserCreate, db: Session):
    existing_user = db.query(User).filter(
        (User.email == data.email) | (User.username == data.username)
    ).first()

    if existing_user:
        return error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="A user with this email or username already exists.",
        )

    password_hashed = hash_password(data.password)
    if not password_hashed:
        return error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Password hashing failed.",
        )

    new_user = User(
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        username=data.username,
        hashed_password=password_hashed,
        is_email_verified=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    _generate_and_send_magic_link(db=db, user=new_user, purpose="verify")

    return success_response(
        status_code=status.HTTP_201_CREATED,
        message="Account created successfully. Please check your email to verify your account before logging in.",
        data={
            "email": new_user.email,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "username": new_user.username,
            "is_email_verified": new_user.is_email_verified,
        },
    )


async def login_user(data: UserLogin, db: Session):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.hashed_password):
        return error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid email or password.",
        )

    if not user.is_email_verified:
        return error_response(
            status_code=status.HTTP_403_FORBIDDEN,
            message="Your email address is not verified. Please check your inbox for the verification link.",
        )

    access_token = create_access_token({"email": user.email})

    return success_response(
        status_code=status.HTTP_200_OK,
        message="Login successful.",
        data={
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "is_active": user.is_active,
            "is_email_verified": user.is_email_verified,
            "access_token": access_token,
        },
    )


async def verify_email_token(db: Session, token: str):
    """Consume a verification token and mark the account as verified."""
    user = get_user_by_magic_token(db, token)

    if not user or not user.magic_link_token_expiry or user.magic_link_token_expiry < datetime.utcnow():
        return error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="This verification link is invalid or has expired. Please request a new one.",
        )

    user.is_email_verified = True
    user.magic_link_token = None
    user.magic_link_token_expiry = None
    db.add(user)
    db.commit()

    return success_response(
        status_code=status.HTTP_200_OK,
        message="Email verified successfully. You can now log in.",
        data=None,
    )


async def resend_verification_link(db: Session, email: str):
    """Re-send a verification magic link."""
    user = get_user_by_email(db, email)

    if user and user.is_email_verified:
        return success_response(
            status_code=status.HTTP_200_OK,
            message="Your email is already verified. You can log in.",
            data=None,
        )

    # Send only when the user exists and is not verified.
    # Return the same message regardless to avoid account enumeration.
    if user:
        _generate_and_send_magic_link(db, user, purpose="verify")

    return success_response(
        status_code=status.HTTP_200_OK,
        message="If an unverified account with that email exists, a new verification link has been sent.",
        data=None,
    )


# ── Password Reset ────────────────────────────────────────────────────────────

async def forgot_password(db: Session, email: str):
    """
    Send a password-reset magic link.
    Returns the same response whether the email exists or not to prevent enumeration.
    """
    user = get_user_by_email(db, email)
    if user:
        _generate_and_send_magic_link(db, user, purpose="reset")

    return success_response(
        status_code=status.HTTP_200_OK,
        message="If an account with that email exists, a password reset link has been sent.",
        data=None,
    )


async def reset_password(db: Session, token: str, new_password: str):
    """Consume a password-reset token and update the user's password."""
    user = get_user_by_magic_token(db, token)

    if not user or not user.magic_link_token_expiry or user.magic_link_token_expiry < datetime.utcnow():
        return error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="This reset link is invalid or has expired. Please request a new one.",
        )

    user.hashed_password = hash_password(new_password)
    user.magic_link_token = None
    user.magic_link_token_expiry = None
    db.add(user)
    db.commit()

    return success_response(
        status_code=status.HTTP_200_OK,
        message="Password reset successfully. You can now log in.",
        data=None,
    )
