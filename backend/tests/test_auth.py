"""
Tests for authentication functionality.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User
from ..core.security import hash_password, verify_password, create_access_token
from ..services.auth_service import AuthService
from ..schemas.auth import RegisterRequest, LoginRequest


class TestPasswordHashing:
    """Test password hashing functions."""
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 20  # Bcrypt hashes are long
    
    def test_verify_password(self):
        """Test password verification."""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)


class TestJWTTokens:
    """Test JWT token creation and verification."""
    
    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long
    
    def test_verify_token(self):
        """Test JWT token verification."""
        from ..core.security import verify_token
        
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 1
    
    def test_invalid_token(self):
        """Test invalid token verification."""
        from ..core.security import verify_token
        
        payload = verify_token("invalid-token")
        assert payload is None


@pytest.mark.asyncio
class TestAuthService:
    """Test authentication service methods."""
    
    async def test_create_user(self, db_session: AsyncSession):
        """Test user creation."""
        user_data = RegisterRequest(
            email="test@example.com",
            password="testpassword123",
            first_name="Test",
            last_name="User"
        )
        
        user = await AuthService.create_user(user_data, db_session)
        
        assert user.email == user_data.email
        assert user.first_name == user_data.first_name
        assert user.last_name == user_data.last_name
        assert user.password_hash is not None
        assert user.password_hash != user_data.password
    
    async def test_authenticate_user(self, db_session: AsyncSession):
        """Test user authentication."""
        # Create user first
        user_data = RegisterRequest(
            email="test@example.com",
            password="testpassword123",
            first_name="Test",
            last_name="User"
        )
        await AuthService.create_user(user_data, db_session)
        
        # Test authentication
        login_data = LoginRequest(
            email="test@example.com",
            password="testpassword123"
        )
        
        user = await AuthService.authenticate_user(login_data, db_session)
        assert user is not None
        assert user.email == "test@example.com"
    
    async def test_authenticate_user_invalid(self, db_session: AsyncSession):
        """Test user authentication with invalid credentials."""
        login_data = LoginRequest(
            email="nonexistent@example.com",
            password="wrongpassword"
        )
        
        user = await AuthService.authenticate_user(login_data, db_session)
        assert user is None
    
    async def test_create_user_tokens(self, db_session: AsyncSession):
        """Test token creation for user."""
        user_data = RegisterRequest(
            email="test@example.com",
            password="testpassword123",
            first_name="Test",
            last_name="User"
        )
        user = await AuthService.create_user(user_data, db_session)
        
        tokens = await AuthService.create_user_tokens(user)
        
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert len(tokens["access_token"]) > 50
        assert len(tokens["refresh_token"]) > 50


@pytest.mark.asyncio
class TestAuthEndpoints:
    """Test authentication API endpoints."""
    
    async def test_register_endpoint(self, client: AsyncClient):
        """Test user registration endpoint."""
        user_data = {
            "email": "newuser@example.com",
            "password": "testpassword123",
            "first_name": "New",
            "last_name": "User"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == user_data["email"]
    
    async def test_login_endpoint(self, client: AsyncClient):
        """Test user login endpoint."""
        # Register user first
        user_data = {
            "email": "loginuser@example.com",
            "password": "testpassword123",
            "first_name": "Login",
            "last_name": "User"
        }
        await client.post("/api/auth/register", json=user_data)
        
        # Test login
        login_data = {
            "email": "loginuser@example.com",
            "password": "testpassword123"
        }
        
        response = await client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == login_data["email"]
    
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = await client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert response.json()["message"] == "Invalid email or password"
    
    async def test_get_current_user(self, client: AsyncClient, auth_headers: dict):
        """Test getting current user information."""
        response = await client.get("/api/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "first_name" in data
        assert "last_name" in data
    
    async def test_protected_endpoint_without_auth(self, client: AsyncClient):
        """Test protected endpoint without authentication."""
        response = await client.get("/api/auth/me")
        
        assert response.status_code == 401
    
    async def test_protected_endpoint_invalid_token(self, client: AsyncClient):
        """Test protected endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = await client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 401


@pytest.mark.asyncio
class TestAuthEdgeCases:
    """Test authentication edge cases and error scenarios."""
    
    async def test_register_duplicate_email(self, client: AsyncClient):
        """Test registering with duplicate email."""
        user_data = {
            "email": "duplicate@example.com",
            "password": "testpassword123",
            "first_name": "First",
            "last_name": "User"
        }
        
        # Register first user
        response1 = await client.post("/api/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Try to register with same email
        user_data["first_name"] = "Second"
        response2 = await client.post("/api/auth/register", json=user_data)
        
        assert response2.status_code == 400
        assert "already exists" in response2.json()["message"]
    
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registering with invalid email format."""
        user_data = {
            "email": "invalid-email",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation error
    
    async def test_register_short_password(self, client: AsyncClient):
        """Test registering with password too short."""
        user_data = {
            "email": "shortpass@example.com",
            "password": "123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation error