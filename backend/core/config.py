"""
Configuration settings using Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings from environment variables.
    
    Args:
        database_url (str): Database connection URL.
        jwt_secret (str): JWT secret key for signing tokens.
        jwt_algorithm (str): JWT algorithm for signing.
        access_token_expire_minutes (int): Token expiration time in minutes.
        google_client_id (Optional[str]): Google OAuth client ID.
        google_client_secret (Optional[str]): Google OAuth client secret.
        frontend_url (str): Frontend URL for CORS.
        environment (str): Application environment.
    """
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./budget_app.db"
    
    # JWT Configuration
    jwt_secret: str = "your-super-secret-jwt-key-here-change-this-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OAuth Configuration
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    
    # CORS
    frontend_url: str = "http://localhost:5173"
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create global settings instance
settings = Settings()