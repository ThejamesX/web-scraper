"""Pytest configuration and fixtures."""

import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient

from main import app
from db.models import Base
from db.session import get_db
from scraper.service import get_scraper_service, ScraperService


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db_engine():
    """Create a test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = async_sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
async def test_client(test_db_session):
    """Create a test client with mocked dependencies."""
    
    # Mock database dependency
    async def override_get_db():
        yield test_db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


class MockScraperService:
    """Mock scraper service for testing."""
    
    async def initialize(self):
        """Mock initialize."""
        pass
    
    async def close(self):
        """Mock close."""
        pass
    
    async def fetch_product_details(self, url: str) -> dict:
        """Mock fetch product details."""
        return {
            "name": "Test Product",
            "price": 999.99
        }
    
    async def search_site(self, site: str, query: str, limit: int = 10):
        """Mock search site."""
        from api.schemas import SearchResultItem
        return [
            SearchResultItem(
                name=f"Test Product {i+1}",
                price=100.0 * (i + 1),
                product_url=f"https://www.alza.cz/test-product-{i+1}",
                image_url=f"https://cdn.alza.cz/test-{i+1}.jpg"
            )
            for i in range(min(3, limit))
        ]


@pytest.fixture
def mock_scraper():
    """Create a mock scraper service."""
    return MockScraperService()
