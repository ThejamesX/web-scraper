"""
Frontend integration tests for the complete site functionality.

Tests all buttons, search actions, and user workflows through API endpoints
that the frontend would call.
"""

import pytest
from httpx import AsyncClient
from main import app
from tests.conftest import MockScraperService
from db.session import get_db
from scraper.service import get_scraper_service


@pytest.mark.asyncio
async def test_dashboard_load_empty(test_db):
    """Test dashboard loads correctly when no products are tracked."""
    async def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Simulate loading dashboard - get all tracked products
            response = await client.get("/track")
            assert response.status_code == 200
            products = response.json()
            assert isinstance(products, list)
            assert len(products) == 0
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_dashboard_load_with_products(test_db):
    """Test dashboard loads correctly with tracked products."""
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
            # Add some products
            await client.post("/track", json={"url": "https://www.alza.cz/test-1"})
            await client.post("/track", json={"url": "https://www.alza.cz/test-2"})
            await client.post("/track", json={"url": "https://www.alza.cz/test-on-sale"})
            
            # Load dashboard
            response = await client.get("/track")
            assert response.status_code == 200
            products = response.json()
            assert len(products) == 3
            
            # Verify each product has all required fields for display
            for product in products:
                assert "id" in product
                assert "name" in product
                assert "last_known_price" in product
                assert "is_on_sale" in product
                assert "alert_price" in product
                assert "alert_triggered" in product
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_search_button_action(test_db):
    """Test search button functionality (search form submission)."""
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
            # Simulate clicking search button with a query
            response = await client.post(
                "/search",
                json={
                    "site": "alza",
                    "query": "laptop"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "results" in data
            assert len(data["results"]) > 0
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_track_button_action(test_db):
    """Test track button functionality (adding product to tracked list)."""
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
            # First search for products
            search_response = await client.post(
                "/search",
                json={"site": "alza", "query": "test"}
            )
            results = search_response.json()["results"]
            
            # Click "Track" button on first result
            track_response = await client.post(
                "/track",
                json={"url": results[0]["product_url"]}
            )
            
            assert track_response.status_code == 201
            tracked = track_response.json()
            assert tracked["is_tracked"] is True
            assert tracked["url"] == results[0]["product_url"]
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_set_alert_button_action(test_db):
    """Test set alert button functionality."""
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
            track_response = await client.post(
                "/track",
                json={"url": "https://www.alza.cz/test-product"}
            )
            product_id = track_response.json()["id"]
            
            # Click "Set Alert" button
            alert_response = await client.put(
                f"/track/{product_id}/alert",
                json={"target_price": 500.0}
            )
            
            assert alert_response.status_code == 200
            data = alert_response.json()
            assert data["status"] == "success"
            assert data["item"]["alert_price"] == 500.0
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_clear_alert_button_action(test_db):
    """Test clear alert button functionality."""
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
            # Track product and set alert
            track_response = await client.post(
                "/track",
                json={"url": "https://www.alza.cz/test-product"}
            )
            product_id = track_response.json()["id"]
            await client.put(f"/track/{product_id}/alert", json={"target_price": 500.0})
            
            # Click "Clear Alert" button
            clear_response = await client.delete(f"/track/{product_id}/alert")
            
            assert clear_response.status_code == 200
            assert clear_response.json()["status"] == "success"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_filter_tabs_all_products(test_db):
    """Test 'All Products' filter tab."""
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
            # Add some products
            await client.post("/track", json={"url": "https://www.alza.cz/test-1"})
            await client.post("/track", json={"url": "https://www.alza.cz/test-on-sale"})
            
            # Get all products (simulates clicking "All" tab)
            response = await client.get("/track")
            assert response.status_code == 200
            products = response.json()
            assert len(products) == 2
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_filter_tabs_on_sale(test_db):
    """Test 'On Sale' filter tab functionality."""
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
            # Add mix of regular and sale products
            await client.post("/track", json={"url": "https://www.alza.cz/test-1"})
            await client.post("/track", json={"url": "https://www.alza.cz/test-on-sale-1"})
            await client.post("/track", json={"url": "https://www.alza.cz/test-on-sale-2"})
            
            # Get all products and filter on sale (frontend would do this)
            response = await client.get("/track")
            assert response.status_code == 200
            products = response.json()
            
            # Count sale products
            on_sale_count = sum(1 for p in products if p["is_on_sale"])
            assert on_sale_count == 2
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_filter_tabs_triggered_alerts(test_db):
    """Test 'Triggered Alerts' filter tab functionality."""
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
            # Track products and set alerts
            track1 = await client.post("/track", json={"url": "https://www.alza.cz/test-1"})
            track2 = await client.post("/track", json={"url": "https://www.alza.cz/test-on-sale"})
            
            product1_id = track1.json()["id"]
            product2_id = track2.json()["id"]
            
            # Set alert on product 2 that should trigger (price is 799.99)
            await client.put(f"/track/{product2_id}/alert", json={"target_price": 800.0})
            
            # Get all products and filter triggered alerts
            response = await client.get("/track")
            products = response.json()
            
            # Frontend would filter, but we can verify data is available
            assert any(p["alert_price"] is not None for p in products)
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_navigation_between_pages(test_db):
    """Test navigation actions between Dashboard, Search, and Categories."""
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
            # Simulate navigation to Dashboard (get tracked products)
            dashboard_response = await client.get("/track")
            assert dashboard_response.status_code == 200
            
            # Simulate navigation to Search page (search for products)
            search_response = await client.post(
                "/search",
                json={"site": "alza", "query": "test"}
            )
            assert search_response.status_code == 200
            
            # Categories are handled client-side, so no API call needed
            # But we can verify product data includes necessary fields
            products = dashboard_response.json()
            # Each product can be assigned to categories (client-side)
            assert isinstance(products, list)
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_product_detail_view(test_db):
    """Test viewing product details (clicking on a product card)."""
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
            track_response = await client.post(
                "/track",
                json={"url": "https://www.alza.cz/test-product"}
            )
            product_id = track_response.json()["id"]
            
            # Click on product to view details
            detail_response = await client.get(f"/track/{product_id}")
            assert detail_response.status_code == 200
            product = detail_response.json()
            
            # Verify all detail fields are present
            assert "name" in product
            assert "last_known_price" in product
            assert "url" in product
            assert "is_on_sale" in product
            
            # Get price history
            history_response = await client.get(f"/track/product/{product_id}/history")
            assert history_response.status_code == 200
            history = history_response.json()
            assert isinstance(history, list)
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_stats_calculation(test_db):
    """Test statistics displayed on dashboard."""
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
            # Add various products
            await client.post("/track", json={"url": "https://www.alza.cz/test-1"})
            await client.post("/track", json={"url": "https://www.alza.cz/test-on-sale-1"})
            await client.post("/track", json={"url": "https://www.alza.cz/test-on-sale-2"})
            
            # Get products to calculate stats
            response = await client.get("/track")
            products = response.json()
            
            # Calculate stats (as frontend would)
            total_tracked = len(products)
            on_sale_count = sum(1 for p in products if p["is_on_sale"])
            
            assert total_tracked == 3
            assert on_sale_count == 2
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_check_endpoint(test_db):
    """Test health check endpoint for system status."""
    async def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_error_handling_invalid_product_id(test_db):
    """Test error handling for invalid product ID."""
    async def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Try to get non-existent product
            response = await client.get("/track/99999")
            assert response.status_code == 404
            
            # Try to set alert on non-existent product
            alert_response = await client.put(
                "/track/99999/alert",
                json={"target_price": 100.0}
            )
            assert alert_response.status_code == 404
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_error_handling_duplicate_tracking(test_db):
    """Test error handling for tracking same product twice."""
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
            url = "https://www.alza.cz/duplicate-test"
            
            # Track once
            first_response = await client.post("/track", json={"url": url})
            assert first_response.status_code == 201
            
            # Try to track again
            second_response = await client.post("/track", json={"url": url})
            assert second_response.status_code == 400
            assert "already being tracked" in second_response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_complete_user_workflow(test_db):
    """Test complete user workflow from search to alert."""
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
            # 1. User navigates to Dashboard (empty state)
            dashboard = await client.get("/track")
            assert len(dashboard.json()) == 0
            
            # 2. User clicks "Search Products" button
            # 3. User searches for "laptop"
            search = await client.post(
                "/search",
                json={"site": "alza", "query": "laptop"}
            )
            assert search.status_code == 200
            results = search.json()["results"]
            
            # 4. User clicks "Track" on a product
            track = await client.post(
                "/track",
                json={"url": results[0]["product_url"]}
            )
            assert track.status_code == 201
            product_id = track.json()["id"]
            
            # 5. User navigates back to Dashboard
            dashboard = await client.get("/track")
            assert len(dashboard.json()) == 1
            
            # 6. User clicks on product to view details
            detail = await client.get(f"/track/{product_id}")
            assert detail.status_code == 200
            
            # 7. User views price history chart
            history = await client.get(f"/track/product/{product_id}/history")
            assert history.status_code == 200
            
            # 8. User sets a price alert
            alert = await client.put(
                f"/track/{product_id}/alert",
                json={"target_price": 500.0}
            )
            assert alert.status_code == 200
            
            # 9. User verifies alert is set
            verify = await client.get(f"/track/{product_id}")
            assert verify.json()["alert_price"] == 500.0
    finally:
        app.dependency_overrides.clear()
