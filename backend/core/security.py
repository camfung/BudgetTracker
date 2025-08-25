"""
Security utilities for JWT tokens and password hashing.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt
from core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password (str): Plain text password.
        
    Returns:
        str: Hashed password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password (str): Plain text password.
        hashed_password (str): Hashed password to compare against.
        
    Returns:
        bool: True if password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data (Dict[str, Any]): Data to encode in the token.
        expires_delta (Optional[timedelta]): Custom expiration time.
        
    Returns:
        str: JWT token string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "iss": "budget-app",
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def create_refresh_token(user_email: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        user_email (str): User's email address.
        expires_delta (Optional[timedelta]): Custom expiration time.
        
    Returns:
        str: JWT refresh token string.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=30)  # Refresh tokens last longer
    
    to_encode = {
        "sub": user_email,
        "exp": expire,
        "iat": datetime.utcnow(),
        "iss": "budget-app",
        "type": "refresh"
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.
    
    Args:
        token (str): JWT token to verify.
        
    Returns:
        Optional[Dict[str, Any]]: Decoded token payload if valid, None otherwise.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None


def get_token_user_email(token: str) -> Optional[str]:
    """
    Extract user email from a JWT token.
    
    Args:
        token (str): JWT token.
        
    Returns:
        Optional[str]: User email if token is valid, None otherwise.
    """
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None