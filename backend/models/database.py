"""
Database configuration and session management.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./budget_app.db")

# Create async engine with better error handling
try:
    if DATABASE_URL.startswith("sqlite"):
        # Ensure aiosqlite is installed for async SQLite operations
        try:
            import aiosqlite
        except ImportError:
            print("ERROR: aiosqlite is required for async SQLite operations.")
            print("Install it with: pip install aiosqlite")
            sys.exit(1)
            
        engine = create_async_engine(
            DATABASE_URL,
            echo=False,  # Set to False in production
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )
    else:
        engine = create_async_engine(DATABASE_URL, echo=False)
        
except Exception as e:
    print(f"ERROR: Failed to create database engine: {e}")
    print(f"DATABASE_URL: {DATABASE_URL}")
    print("Make sure all required packages are installed:")
    print("- pip install sqlalchemy[asyncio]")
    print("- pip install aiosqlite (for SQLite)")
    sys.exit(1)

# Create session maker
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Create base class for models
Base = declarative_base()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.
    
    Yields:
        AsyncSession: Database session.
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """
    Create all tables in the database.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """
    Drop all tables in the database (for testing).
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)