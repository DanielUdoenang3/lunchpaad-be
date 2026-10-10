from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    username: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    username: str

    class Config:
        from_attributes = True


class AuthSuccessResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"


# ── Magic Link ────────────────────────────────────────────────────────────────

class EmailRequest(BaseModel):
    """Generic single-email payload — used for resend-verification and forgot-password."""
    email: EmailStr = Field(..., example="user@example.com")


class PasswordResetCompleteRequest(BaseModel):
    """Payload for completing a password reset via magic link."""
    token: str = Field(..., description="Token received from the password-reset email link")
    new_password: str = Field(..., min_length=8, example="SecureNewPass1!")
