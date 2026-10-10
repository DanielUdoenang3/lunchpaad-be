from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.schema.base import EmailRequest, PasswordResetCompleteRequest, UserCreate, UserLogin
from app.services import get_current_user
from app.services.auth import (
    create_user,
    forgot_password,
    login_user,
    reset_password,
    resend_verification_link,
    verify_email_token,
)
from app.utils.database import get_db


async def register(user: UserCreate, db: Session = Depends(get_db)):
    return await create_user(data=user, db=db)


async def login(data: UserLogin, db: Session = Depends(get_db)):
    return await login_user(data=data, db=db)


async def verify_email(
    token: str = Query(..., description="Verification token from the email link"),
    db: Session = Depends(get_db),
):
    return await verify_email_token(db, token)


async def resend_verification(payload: EmailRequest, db: Session = Depends(get_db)):
    return await resend_verification_link(db, payload.email)


async def handle_forgot_password(payload: EmailRequest, db: Session = Depends(get_db)):
    return await forgot_password(db, payload.email)


async def handle_reset_password(
    payload: PasswordResetCompleteRequest, db: Session = Depends(get_db)
):
    return await reset_password(db, payload.token, payload.new_password)


async def get_current_user_profile(current_user=Depends(get_current_user)):
    return current_user
