"""
Global test for soundbar search functionality.

This test suite specifically validates searching for "soundbar" across the application,
testing both API endpoints and integration scenarios.
"""

import pytest
from httpx import AsyncClient
from main import app
from tests.conftest import MockScraperService
from db.session import get_db
from scraper.service import get_scraper_service


@pytest.mark.asyncio
async def test_soundbar_search_api(test_db):
    """Test soundbar search through the API."""
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
                    "query": "soundbar"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["query"] == "soundbar"
            assert data["site"] == "alza"
            assert "results" in data
            assert isinstance(data["results"], list)
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_soundbar_search_results_format(test_db):
    """Test that soundbar search results have correct format."""
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
                    "query": "soundbar"
                }
            )
            
            data = response.json()
            results = data["results"]
            
            # Validate each result has required fields
            for result in results:
                assert "name" in result
                assert "price" in result
                assert "product_url" in result
                assert "is_on_sale" in result
                assert isinstance(result["name"], str)
                assert isinstance(result["price"], (int, float))
                assert isinstance(result["product_url"], str)
                assert isinstance(result["is_on_sale"], bool)
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_soundbar_track_workflow(test_db):
    """Test the complete workflow of searching and tracking a soundbar."""
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
            # Step 1: Search for soundbar
            search_response = await client.post(
                "/search",
                json={
                    "site": "alza",
                    "query": "soundbar"
                }
            )
            assert search_response.status_code == 200
            results = search_response.json()["results"]
            assert len(results) > 0
            
            # Step 2: Track the first soundbar result
            first_soundbar_url = results[0]["product_url"]
            track_response = await client.post(
                "/track",
                json={"url": first_soundbar_url}
            )
            assert track_response.status_code == 201
            tracked_product = track_response.json()
            product_id = tracked_product["id"]
            
            # Step 3: Verify it's in tracked products
            tracked_response = await client.get("/track")
            assert tracked_response.status_code == 200
            tracked_products = tracked_response.json()
            assert any(p["id"] == product_id for p in tracked_products)
            
            # Step 4: Set a price alert
            alert_response = await client.put(
                f"/track/{product_id}/alert",
                json={"target_price": 500.0}
            )
            assert alert_response.status_code == 200
            assert alert_response.json()["item"]["alert_price"] == 500.0
            
            # Step 5: Get price history
            history_response = await client.get(f"/track/product/{product_id}/history")
            assert history_response.status_code == 200
            history = history_response.json()
            assert len(history) >= 1
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_soundbar_search_empty_query_validation():
    """Test that empty soundbar query is validated."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/search",
            json={
                "site": "alza",
                "query": ""
            }
        )
        # Empty query should be rejected with error code
        # (frontend validation should also prevent this)
        assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_soundbar_case_insensitive(test_db):
    """Test that soundbar search works with different cases."""
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
            # Test different case variations
            for query in ["soundbar", "SOUNDBAR", "SoundBar", "Soundbar"]:
                response = await client.post(
                    "/search",
                    json={
                        "site": "alza",
                        "query": query
                    }
                )
                assert response.status_code == 200
                data = response.json()
                assert data["query"] == query
    finally:
        app.dependency_overrides.clear()


@pytest.mark.slow
@pytest.mark.asyncio
async def test_soundbar_real_search():
    """Test real soundbar search on Alza.cz (integration test).
    
    This test makes actual network requests and verifies that
    the soundbar search functionality works end-to-end.
    """
    from scraper.service import ScraperService
    
    scraper = ScraperService()
    
    try:
        await scraper.initialize()
        
        # Search for soundbars
        results = await scraper.search_site(
            site="alza",
            query="soundbar",
            limit=5
        )
        
        # Verify we got results
        assert len(results) > 0, "No soundbar results found"
        assert len(results) <= 5
        
        # Verify first result has required fields
        first_result = results[0]
        assert first_result.name, "Result name is empty"
        assert first_result.price > 0, "Result price is invalid"
        assert first_result.product_url, "Result URL is empty"
        assert "alza.cz" in first_result.product_url.lower()
        
        # Verify the name contains soundbar-related terms
        # (either in English or Czech)
        name_lower = first_result.name.lower()
        assert any(term in name_lower for term in ["soundbar", "sound bar", "reproduktor"]), \
            f"Result '{first_result.name}' doesn't appear to be a soundbar"
        
        print(f"\n✓ Found {len(results)} soundbar results:")
        for i, result in enumerate(results, 1):
            sale_status = " [ON SALE]" if result.is_on_sale else ""
            print(f"  {i}. {result.name} - {result.price} Kč{sale_status}")
    
    finally:
        await scraper.close()
