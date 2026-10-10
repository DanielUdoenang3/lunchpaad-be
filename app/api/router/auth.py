from fastapi import APIRouter

from app.api.controller.auth import (
    get_current_user_profile,
    handle_forgot_password,
    handle_reset_password,
    login,
    register,
    resend_verification,
    verify_email,
)

user_router = APIRouter(prefix="/auth", tags=["Auth"])

user_router.add_api_route(
    "/register",
    endpoint=register,
    methods=["POST"],
    response_model=None,
    summary="Register a new user",
    description="Creates a new account and sends an email-verification magic link. The user must verify their email before they can log in.",
)

user_router.add_api_route(
    "/login",
    endpoint=login,
    methods=["POST"],
    response_model=None,
    summary="Login with email & password",
    description="Returns a 403 with a clear message if the email has not been verified yet.",
)

user_router.add_api_route(
    "/verify-email",
    endpoint=verify_email,
    methods=["GET"],
    response_model=None,
    summary="Verify email via magic link",
    description="The frontend hits this URL when the user clicks the link in their inbox. Accepts ?token= as a query parameter.",
)

user_router.add_api_route(
    "/resend-verification",
    endpoint=resend_verification,
    methods=["POST"],
    response_model=None,
    summary="Resend verification email",
    description="Allows the frontend to offer a 'Resend verification email' option.",
)

user_router.add_api_route(
    "/forgot-password",
    endpoint=handle_forgot_password,
    methods=["POST"],
    response_model=None,
    summary="Request a password-reset link",
)

user_router.add_api_route(
    "/reset-password",
    endpoint=handle_reset_password,
    methods=["POST"],
    response_model=None,
    summary="Reset password via magic link token",
)

user_router.add_api_route(
    "/me",
    endpoint=get_current_user_profile,
    methods=["GET"],
    response_model=None,
    summary="Get the current authenticated user",
)
