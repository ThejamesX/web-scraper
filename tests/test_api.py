"""API endpoint tests with mocked dependencies."""

import pytest
from httpx import AsyncClient
from scraper.service import get_scraper_service
from main import app
from tests.conftest import MockScraperService


@pytest.mark.asyncio
async def test_root_endpoint(test_client: AsyncClient):
    """Test root endpoint returns API information."""
    response = await test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_health_check(test_client: AsyncClient):
    """Test health check endpoint."""
    response = await test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_search_endpoint_with_mock(test_client: AsyncClient, mock_scraper):
    """Test search endpoint with mocked scraper."""
    # Override scraper dependency
    async def override_get_scraper():
        return mock_scraper
    
    app.dependency_overrides[get_scraper_service] = override_get_scraper
    
    try:
        response = await test_client.post(
            "/search",
            json={
                "site": "alza",
                "query": "laptop"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "laptop"
        assert data["site"] == "alza"
        assert "results" in data
        assert len(data["results"]) == 3
        assert data["results"][0]["name"] == "Test Product 1"
        assert data["results"][0]["price"] == 100.0
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_search_endpoint_validation():
    """Test search endpoint validates input."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test missing fields
        response = await client.post("/search", json={})
        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_track_product_endpoint_with_mock(test_client: AsyncClient, mock_scraper):
    """Test track product endpoint with mocked scraper."""
    # Override scraper dependency
    async def override_get_scraper():
        return mock_scraper
    
    app.dependency_overrides[get_scraper_service] = override_get_scraper
    
    try:
        response = await test_client.post(
            "/track",
            json={
                "url": "https://www.alza.cz/test-product-123"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["url"] == "https://www.alza.cz/test-product-123"
        assert data["name"] == "Test Product"
        assert data["last_known_price"] == 999.99
        assert data["eshop"] == "alza"
        assert data["is_tracked"] is True
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_track_duplicate_product(test_client: AsyncClient, mock_scraper):
    """Test tracking the same product twice returns error."""
    # Override scraper dependency
    async def override_get_scraper():
        return mock_scraper
    
    app.dependency_overrides[get_scraper_service] = override_get_scraper
    
    try:
        # First request should succeed
        response1 = await test_client.post(
            "/track",
            json={
                "url": "https://www.alza.cz/unique-product-456"
            }
        )
        assert response1.status_code == 201
        
        # Second request with same URL should fail
        response2 = await test_client.post(
            "/track",
            json={
                "url": "https://www.alza.cz/unique-product-456"
            }
        )
        assert response2.status_code == 400
        assert "already being tracked" in response2.json()["detail"]
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_product_history(test_client: AsyncClient, mock_scraper):
    """Test getting product price history."""
    # Override scraper dependency
    async def override_get_scraper():
        return mock_scraper
    
    app.dependency_overrides[get_scraper_service] = override_get_scraper
    
    try:
        # First track a product
        track_response = await test_client.post(
            "/track",
            json={
                "url": "https://www.alza.cz/history-test-789"
            }
        )
        assert track_response.status_code == 201
        product_id = track_response.json()["id"]
        
        # Get history
        history_response = await test_client.get(f"/track/product/{product_id}/history")
        assert history_response.status_code == 200
        history = history_response.json()
        assert isinstance(history, list)
        assert len(history) == 1  # Should have initial price entry
        assert history[0]["price"] == 999.99
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_nonexistent_product_history(test_client: AsyncClient):
    """Test getting history for non-existent product returns 404."""
    response = await test_client.get("/track/product/99999/history")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
