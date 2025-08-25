"""
User schemas for API input/output validation.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """
    Base user schema with common fields.
    """
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    """
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    google_id: Optional[str] = None


class UserUpdate(BaseModel):
    """
    Schema for updating user information.
    """
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)


class UserResponse(UserBase):
    """
    Schema for user responses (without sensitive data).
    """
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    """
    Schema for user data including sensitive fields (internal use only).
    """
    password_hash: Optional[str]
    google_id: Optional[str]