"""
Authentication schemas for login, registration, and token handling.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from .user import UserResponse


class LoginRequest(BaseModel):
    """
    Schema for user login request.
    """
    email: EmailStr
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    """
    Schema for user registration request.
    """
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class TokenResponse(BaseModel):
    """
    Schema for token response.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenRefreshRequest(BaseModel):
    """
    Schema for token refresh request.
    """
    refresh_token: str


class GoogleOAuthRequest(BaseModel):
    """
    Schema for Google OAuth authentication.
    """
    authorization_code: str
    redirect_uri: str


class PasswordResetRequest(BaseModel):
    """
    Schema for password reset request.
    """
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """
    Schema for password reset confirmation.
    """
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class MessageResponse(BaseModel):
    """
    Schema for simple message responses.
    """
    message: str
    success: bool = True