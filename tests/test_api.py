"""API endpoint tests with mocked dependencies."""

import pytest
from httpx import AsyncClient
from scraper.service import get_scraper_service
from main import app
from tests.conftest import MockScraperService
from db.session import get_db


@pytest.mark.asyncio
async def test_root_endpoint(test_db):
    """Test root endpoint returns API information."""
    # test_db is already the session, not a generator
    async def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"
    
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_check(test_db):
    """Test health check endpoint."""
    async def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_search_endpoint_with_mock(test_db):
    """Test search endpoint with mocked scraper."""
    mock_scraper = MockScraperService()
    
    async def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    async def override_get_scraper():
        return mock_scraper
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_scraper_service] = override_get_scraper
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
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
async def test_track_product_endpoint_with_mock(test_db):
    """Test track product endpoint with mocked scraper."""
    mock_scraper = MockScraperService()
    
    #  Create a proper async generator for the database dependency
    async def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    async def override_get_scraper():
        return mock_scraper
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_scraper_service] = override_get_scraper
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
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
async def test_track_duplicate_product(test_db):
    """Test tracking the same product twice returns error."""
    mock_scraper = MockScraperService()
    
    async def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    async def override_get_scraper():
        return mock_scraper
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_scraper_service] = override_get_scraper
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            # First request should succeed
            response1 = await client.post(
                "/track",
                json={
                    "url": "https://www.alza.cz/unique-product-456"
                }
            )
            assert response1.status_code == 201
            
            # Second request with same URL should fail
            response2 = await client.post(
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
async def test_get_product_history(test_db):
    """Test getting product price history."""
    mock_scraper = MockScraperService()
    
    async def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    async def override_get_scraper():
        return mock_scraper
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_scraper_service] = override_get_scraper
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            # First track a product
            track_response = await client.post(
                "/track",
                json={
                    "url": "https://www.alza.cz/history-test-789"
                }
            )
            assert track_response.status_code == 201
            product_id = track_response.json()["id"]
            
            # Get history
            history_response = await client.get(f"/track/product/{product_id}/history")
            assert history_response.status_code == 200
            history = history_response.json()
            assert isinstance(history, list)
            assert len(history) == 1  # Should have initial price entry
            assert history[0]["price"] == 999.99
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_nonexistent_product_history(test_db):
    """Test getting history for non-existent product returns 404."""
    async def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/track/product/99999/history")
            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_all_tracked_products(test_db):
    """Test getting all tracked products."""
    mock_scraper = MockScraperService()
    
    async def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    async def override_get_scraper():
        return mock_scraper
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_scraper_service] = override_get_scraper
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            # First, track a couple of products
            await client.post("/track", json={"url": "https://www.alza.cz/test-1"})
            await client.post("/track", json={"url": "https://www.alza.cz/test-2"})
            
            # Get all tracked products
            response = await client.get("/track")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 2
            
            # Check that new fields are present
            assert "is_on_sale" in data[0]
            assert "original_price" in data[0]
            assert "alert_price" in data[0]
            assert "alert_triggered" in data[0]
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_single_product(test_db):
    """Test getting a single tracked product."""
    mock_scraper = MockScraperService()
    
    async def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    async def override_get_scraper():
        return mock_scraper
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_scraper_service] = override_get_scraper
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Track a product
            track_response = await client.post("/track", json={"url": "https://www.alza.cz/test-product"})
            product_id = track_response.json()["id"]
            
            # Get the product
            response = await client.get(f"/track/{product_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == product_id
            assert "is_on_sale" in data
            assert "alert_price" in data
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_set_price_alert(test_db):
    """Test setting a price alert."""
    mock_scraper = MockScraperService()
    
    async def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    async def override_get_scraper():
        return mock_scraper
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_scraper_service] = override_get_scraper
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Track a product first
            track_response = await client.post("/track", json={"url": "https://www.alza.cz/test-product"})
            product_id = track_response.json()["id"]
            
            # Set an alert
            alert_response = await client.put(
                f"/track/{product_id}/alert",
                json={"target_price": 500.0}
            )
            
            assert alert_response.status_code == 200
            data = alert_response.json()
            assert data["status"] == "success"
            assert data["item"]["alert_price"] == 500.0
            assert data["item"]["alert_triggered"] is False
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_clear_price_alert(test_db):
    """Test clearing a price alert."""
    mock_scraper = MockScraperService()
    
    async def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    async def override_get_scraper():
        return mock_scraper
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_scraper_service] = override_get_scraper
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Track a product first
            track_response = await client.post("/track", json={"url": "https://www.alza.cz/test-product"})
            product_id = track_response.json()["id"]
            
            # Set an alert
            await client.put(f"/track/{product_id}/alert", json={"target_price": 500.0})
            
            # Clear the alert
            clear_response = await client.delete(f"/track/{product_id}/alert")
            assert clear_response.status_code == 200
            assert clear_response.json()["status"] == "success"
            
            # Verify alert is cleared
            product_response = await client.get(f"/track/{product_id}")
            product_data = product_response.json()
            assert product_data["alert_price"] is None
            assert product_data["alert_triggered"] is False
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_alert_on_nonexistent_product(test_db):
    """Test setting alert on non-existent product returns 404."""
    async def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.put(
                "/track/99999/alert",
                json={"target_price": 500.0}
            )
            assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_track_product_with_sale(test_db):
    """Test tracking a product that is on sale."""
    mock_scraper = MockScraperService()
    
    async def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    async def override_get_scraper():
        return mock_scraper
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_scraper_service] = override_get_scraper
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Track a product with "on-sale" in URL to trigger mock sale data
            response = await client.post(
                "/track",
                json={"url": "https://www.alza.cz/test-on-sale-product"}
            )
            
            assert response.status_code == 201
            data = response.json()
            assert data["is_on_sale"] is True
            assert data["original_price"] == 999.99
            assert data["last_known_price"] == 799.99
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_search_includes_sale_info(test_db):
    """Test that search results include sale information."""
    mock_scraper = MockScraperService()
    
    async def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    async def override_get_scraper():
        return mock_scraper
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_scraper_service] = override_get_scraper
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/search",
                json={
                    "site": "alza",
                    "query": "laptop"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            results = data["results"]
            
            # Check that sale fields are present
            assert "is_on_sale" in results[0]
            assert "original_price" in results[0]
            
            # Second product should be on sale (per mock)
            assert results[1]["is_on_sale"] is True
            assert results[1]["original_price"] == 150.0
    finally:
        app.dependency_overrides.clear()
