"""
User model for authentication and user management.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    """
    User model for storing user information and authentication data.
    
    Args:
        id (int): Primary key, auto-incremented.
        email (str): User's email address, unique.
        first_name (str): User's first name.
        last_name (str): User's last name.
        password_hash (str): Hashed password (nullable for OAuth users).
        google_id (str): Google OAuth ID (nullable for email/password users).
        created_at (datetime): Timestamp when user was created.
        updated_at (datetime): Timestamp when user was last updated.
    """
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    password_hash = Column(Text, nullable=True)  # Nullable for OAuth users
    google_id = Column(String(255), nullable=True, unique=True)  # Nullable for email/password users
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    pay_periods = relationship("PayPeriod", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', name='{self.first_name} {self.last_name}')>"