"""Pytest configuration and fixtures."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from db.models import Base


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create a test database for each test."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    session = async_session()
    
    yield session
    
    await session.close()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


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
