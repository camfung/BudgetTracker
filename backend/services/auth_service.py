"""
Authentication service with business logic for user management.
"""

from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, Depends
import httpx

from models.user import User
from schemas.user import UserCreate, UserResponse
from schemas.auth import RegisterRequest, LoginRequest, GoogleOAuthRequest
from core.security import hash_password, verify_password, create_access_token, create_refresh_token, verify_token
from core.config import settings
from models.database import get_session

security = HTTPBearer()


class AuthService:
    """
    Authentication service for handling user registration, login, and OAuth.
    """
    
    @staticmethod
    async def create_user(user_data: RegisterRequest, db: AsyncSession) -> User:
        """
        Create a new user with email and password.
        
        Args:
            user_data (RegisterRequest): User registration data.
            db (AsyncSession): Database session.
            
        Returns:
            User: Created user object.
            
        Raises:
            HTTPException: If user already exists.
        """
        # Check if user already exists
        result = await db.execute(select(User).where(User.email == user_data.email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        db_user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            password_hash=hash_password(user_data.password)
        )
        
        db.add(db_user)
        try:
            await db.commit()
            await db.refresh(db_user)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        return db_user
    
    @staticmethod
    async def authenticate_user(login_data: LoginRequest, db: AsyncSession) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            login_data (LoginRequest): Login credentials.
            db (AsyncSession): Database session.
            
        Returns:
            Optional[User]: User object if authentication successful, None otherwise.
        """
        result = await db.execute(select(User).where(User.email == login_data.email))
        user = result.scalar_one_or_none()
        
        if not user or not user.password_hash:
            return None
        
        if not verify_password(login_data.password, user.password_hash):
            return None
        
        return user
    
    @staticmethod
    async def create_user_tokens(user: User) -> Dict[str, str]:
        """
        Create access and refresh tokens for a user.
        
        Args:
            user (User): User object.
            
        Returns:
            Dict[str, str]: Dictionary containing access and refresh tokens.
        """
        access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
        refresh_token = create_refresh_token(user.email)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    @staticmethod
    async def refresh_access_token(refresh_token: str, db: AsyncSession) -> Optional[Dict[str, str]]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token (str): Refresh token.
            db (AsyncSession): Database session.
            
        Returns:
            Optional[Dict[str, str]]: New tokens if refresh successful, None otherwise.
        """
        payload = verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        
        user_email = payload.get("sub")
        if not user_email:
            return None
        
        # Get user from database
        result = await db.execute(select(User).where(User.email == user_email))
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        return await AuthService.create_user_tokens(user)
    
    @staticmethod
    async def google_oauth_login(oauth_data: GoogleOAuthRequest, db: AsyncSession) -> User:
        """
        Handle Google OAuth login.
        
        Args:
            oauth_data (GoogleOAuthRequest): OAuth authorization data.
            db (AsyncSession): Database session.
            
        Returns:
            User: User object (created or existing).
            
        Raises:
            HTTPException: If OAuth validation fails.
        """
        # Exchange authorization code for access token
        token_data = await AuthService._exchange_oauth_code(
            oauth_data.authorization_code, 
            oauth_data.redirect_uri
        )
        
        # Get user info from Google
        user_info = await AuthService._get_google_user_info(token_data["access_token"])
        
        # Check if user exists
        result = await db.execute(select(User).where(User.email == user_info["email"]))
        user = result.scalar_one_or_none()
        
        if user:
            # Update Google ID if not set
            if not user.google_id:
                user.google_id = user_info["id"]
                await db.commit()
        else:
            # Create new user
            user = User(
                email=user_info["email"],
                first_name=user_info["given_name"],
                last_name=user_info["family_name"],
                google_id=user_info["id"]
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        return user
    
    @staticmethod
    async def _exchange_oauth_code(authorization_code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange OAuth authorization code for access token.
        
        Args:
            authorization_code (str): Authorization code from OAuth flow.
            redirect_uri (str): Redirect URI used in OAuth flow.
            
        Returns:
            Dict[str, Any]: Token data from Google.
            
        Raises:
            HTTPException: If token exchange fails.
        """
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "code": authorization_code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=token_data)
            
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code for token"
            )
        
        return response.json()
    
    @staticmethod
    async def _get_google_user_info(access_token: str) -> Dict[str, Any]:
        """
        Get user information from Google using access token.
        
        Args:
            access_token (str): Google access token.
            
        Returns:
            Dict[str, Any]: User information from Google.
            
        Raises:
            HTTPException: If user info retrieval fails.
        """
        user_info_url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(user_info_url)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user information from Google"
            )
        
        return response.json()
    
    @staticmethod
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_session)
    ) -> User:
        """
        Get current user from JWT token.
        
        Args:
            credentials (HTTPAuthorizationCredentials): Authorization header.
            db (AsyncSession): Database session.
            
        Returns:
            User: Current user object.
            
        Raises:
            HTTPException: If token is invalid or user not found.
        """
        token = credentials.credentials
        payload = verify_token(token)
        
        if not payload or payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_email = payload.get("sub")
        if not user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        result = await db.execute(select(User).where(User.email == user_email))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user