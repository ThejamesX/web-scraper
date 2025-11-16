"""Integration tests for scraper service against live websites.

These tests make real network requests and are marked as 'slow'.
They will break if the target websites change their structure.
"""

import pytest
from scraper.service import ScraperService


@pytest.mark.slow
@pytest.mark.asyncio
async def test_search_alza_real():
    """Test real search on Alza.cz (integration test)."""
    scraper = ScraperService()
    
    try:
        await scraper.initialize()
        
        # Search for a common product
        results = await scraper.search_site(
            site="alza",
            query="iphone",
            limit=5
        )
        
        # Verify we got results
        assert len(results) > 0
        assert len(results) <= 5
        
        # Verify first result has required fields
        first_result = results[0]
        assert first_result.name
        assert first_result.price > 0
        assert first_result.product_url
        assert "alza.cz" in first_result.product_url
        
        print(f"\nFound {len(results)} results for 'iphone':")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.name} - {result.price} Kč")
            print(f"   URL: {result.product_url}")
    
    finally:
        await scraper.close()


@pytest.mark.slow
@pytest.mark.asyncio
async def test_fetch_alza_product_details_real():
    """Test fetching real product details from Alza.cz (integration test)."""
    scraper = ScraperService()
    
    try:
        await scraper.initialize()
        
        # First, search for a product to get a real URL
        search_results = await scraper.search_site(
            site="alza",
            query="samsung galaxy",
            limit=1
        )
        
        assert len(search_results) > 0
        product_url = search_results[0].product_url
        
        # Now fetch details for that product
        details = await scraper.fetch_product_details(product_url)
        
        # Verify details
        assert "name" in details
        assert "price" in details
        assert details["name"]
        assert details["price"] > 0
        
        print(f"\nProduct details for {product_url}:")
        print(f"Name: {details['name']}")
        print(f"Price: {details['price']} Kč")
    
    finally:
        await scraper.close()


@pytest.mark.slow
@pytest.mark.asyncio
async def test_scraper_unsupported_site():
    """Test that scraper raises error for unsupported site."""
    scraper = ScraperService()
    
    try:
        await scraper.initialize()
        
        with pytest.raises(ValueError) as exc_info:
            await scraper.search_site(
                site="unsupported_shop",
                query="test",
                limit=10
            )
        
        assert "Unsupported site" in str(exc_info.value)
    
    finally:
        await scraper.close()


@pytest.mark.slow
@pytest.mark.asyncio
async def test_scraper_invalid_url():
    """Test that scraper handles invalid URLs gracefully."""
    scraper = ScraperService()
    
    try:
        await scraper.initialize()
        
        with pytest.raises(ValueError) as exc_info:
            await scraper.fetch_product_details("https://www.example.com/product")
        
        assert "Unsupported e-shop" in str(exc_info.value)
    
    finally:
        await scraper.close()
