"""
Authentication API endpoints for registration, login, and OAuth.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import get_session
from models.user import User
from schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse, TokenRefreshRequest,
    GoogleOAuthRequest, MessageResponse
)
from schemas.user import UserResponse
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_session)
):
    """
    Register a new user with email and password.
    
    Args:
        user_data (RegisterRequest): User registration data.
        db (AsyncSession): Database session.
        
    Returns:
        TokenResponse: Access and refresh tokens with user data.
    """
    # Create user
    user = await AuthService.create_user(user_data, db)
    
    # Generate tokens
    tokens = await AuthService.create_user_tokens(user)
    
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_session)
):
    """
    Login with email and password.
    
    Args:
        login_data (LoginRequest): Login credentials.
        db (AsyncSession): Database session.
        
    Returns:
        TokenResponse: Access and refresh tokens with user data.
        
    Raises:
        HTTPException: If credentials are invalid.
    """
    # Authenticate user
    user = await AuthService.authenticate_user(login_data, db)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate tokens
    tokens = await AuthService.create_user_tokens(user)
    
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        user=UserResponse.model_validate(user)
    )


@router.post("/google", response_model=TokenResponse)
async def google_oauth(
    oauth_data: GoogleOAuthRequest,
    db: AsyncSession = Depends(get_session)
):
    """
    Login or register with Google OAuth.
    
    Args:
        oauth_data (GoogleOAuthRequest): OAuth authorization data.
        db (AsyncSession): Database session.
        
    Returns:
        TokenResponse: Access and refresh tokens with user data.
    """
    # Handle Google OAuth
    user = await AuthService.google_oauth_login(oauth_data, db)
    
    # Generate tokens
    tokens = await AuthService.create_user_tokens(user)
    
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        user=UserResponse.model_validate(user)
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: TokenRefreshRequest,
    db: AsyncSession = Depends(get_session)
):
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_data (TokenRefreshRequest): Refresh token data.
        db (AsyncSession): Database session.
        
    Returns:
        TokenResponse: New access and refresh tokens.
        
    Raises:
        HTTPException: If refresh token is invalid.
    """
    tokens = await AuthService.refresh_access_token(refresh_data.refresh_token, db)
    
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Get user for response
    from core.security import get_token_user_email
    from sqlalchemy.future import select
    
    user_email = get_token_user_email(tokens["access_token"])
    result = await db.execute(select(User).where(User.email == user_email))
    user = result.scalar_one_or_none()
    
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        user=UserResponse.model_validate(user) if user else None
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(AuthService.get_current_user)
):
    """
    Get current authenticated user information.
    
    Args:
        current_user (User): Current authenticated user.
        
    Returns:
        UserResponse: Current user data.
    """
    return UserResponse.model_validate(current_user)


@router.post("/logout", response_model=MessageResponse)
async def logout():
    """
    Logout endpoint (token invalidation handled client-side).
    
    Returns:
        MessageResponse: Success message.
    """
    return MessageResponse(message="Successfully logged out")


@router.get("/test", response_model=MessageResponse)
async def test_auth(
    current_user: User = Depends(AuthService.get_current_user)
):
    """
    Test authentication endpoint.
    
    Args:
        current_user (User): Current authenticated user.
        
    Returns:
        MessageResponse: Test success message.
    """
    return MessageResponse(
        message=f"Authentication successful for {current_user.email}"
    )