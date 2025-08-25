"""
Pytest configuration and fixtures for testing.
"""

import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from ..models.database import Base, get_session
from ..models.user import User
from ..main import app
from ..services.auth_service import AuthService
from ..schemas.auth import RegisterRequest


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)

# Create test session maker
TestAsyncSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    """Override database session for testing."""
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for testing."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Get session
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user_data = RegisterRequest(
        email="testuser@example.com",
        password="testpassword123",
        first_name="Test",
        last_name="User"
    )
    
    user = await AuthService.create_user(user_data, db_session)
    return user


@pytest.fixture
async def auth_headers(test_user: User) -> dict:
    """Create authentication headers for testing."""
    tokens = await AuthService.create_user_tokens(test_user)
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create a test client."""
    # Override the dependency
    app.dependency_overrides[get_session] = override_get_session
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
async def authenticated_client(client: AsyncClient, auth_headers: dict) -> AsyncClient:
    """Create an authenticated test client."""
    # Store headers in the client for convenience
    client.headers.update(auth_headers)
    return client


# Additional test data fixtures
@pytest.fixture
def sample_pay_period_data():
    """Sample pay period data for testing."""
    from datetime import date, timedelta
    
    start_date = date.today()
    end_date = start_date + timedelta(days=14)
    
    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_income": "2000.00"
    }


@pytest.fixture
def sample_budget_categories():
    """Sample budget categories for testing."""
    return [
        {"name": "Groceries", "allocated_amount": "500.00"},
        {"name": "Rent", "allocated_amount": "1200.00"},
        {"name": "Utilities", "allocated_amount": "200.00"},
        {"name": "Entertainment", "allocated_amount": "100.00"}
    ]


@pytest.fixture
def sample_transactions():
    """Sample transaction data for testing."""
    return [
        {
            "amount": "75.50",
            "description": "Grocery shopping at Walmart",
            "source": "manual"
        },
        {
            "amount": "45.00",
            "description": "Gas station fill-up",
            "source": "manual"
        },
        {
            "amount": "12.99",
            "description": "Netflix subscription",
            "source": "api"
        }
    ]