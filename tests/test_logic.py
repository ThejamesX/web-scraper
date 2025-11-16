"""Unit tests for business logic."""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from scheduler.jobs import check_all_product_prices
from db.models import Product, PriceHistory


@pytest.mark.asyncio
async def test_check_all_product_prices_no_products():
    """Test price check job when no products exist."""
    
    # Mock database session
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_db.execute.return_value = mock_result
    
    # Mock scraper service
    mock_scraper = AsyncMock()
    
    with patch('scheduler.jobs.AsyncSessionLocal') as mock_session:
        mock_session.return_value.__aenter__.return_value = mock_db
        
        with patch('scheduler.jobs.get_scraper_service', return_value=mock_scraper):
            await check_all_product_prices()
            
            # Verify database was queried but no scraping occurred
            mock_db.execute.assert_called_once()
            mock_scraper.fetch_product_details.assert_not_called()


@pytest.mark.asyncio
async def test_check_all_product_prices_unchanged_price():
    """Test price check job when price hasn't changed."""
    
    # Create mock product
    mock_product = Product(
        id=1,
        url="https://www.alza.cz/test",
        name="Test Product",
        eshop="alza",
        last_known_price=999.99,
        last_check_time=datetime.now(timezone.utc),
        is_tracked=True
    )
    
    # Mock database session
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_product]
    mock_db.execute.return_value = mock_result
    
    # Mock scraper service to return same price
    mock_scraper = AsyncMock()
    mock_scraper.fetch_product_details.return_value = {
        "name": "Test Product",
        "price": 999.99  # Same as last_known_price
    }
    
    with patch('scheduler.jobs.AsyncSessionLocal') as mock_session:
        mock_session.return_value.__aenter__.return_value = mock_db
        
        with patch('scheduler.jobs.get_scraper_service', return_value=mock_scraper):
            await check_all_product_prices()
            
            # Verify scraper was called
            mock_scraper.fetch_product_details.assert_called_once_with(mock_product.url)
            
            # Verify no price history was added (price unchanged)
            # Check that db.add was not called with PriceHistory
            calls_with_price_history = [
                call for call in mock_db.add.call_args_list
                if isinstance(call[0][0], PriceHistory)
            ]
            assert len(calls_with_price_history) == 0
            
            # Verify commit was called
            mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_check_all_product_prices_changed_price():
    """Test price check job when price has changed."""
    
    # Create mock product
    mock_product = Product(
        id=1,
        url="https://www.alza.cz/test",
        name="Test Product",
        eshop="alza",
        last_known_price=999.99,
        last_check_time=datetime.now(timezone.utc),
        is_tracked=True
    )
    
    # Mock database session
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_product]
    mock_db.execute.return_value = mock_result
    
    # Mock scraper service to return different price
    mock_scraper = AsyncMock()
    mock_scraper.fetch_product_details.return_value = {
        "name": "Test Product",
        "price": 899.99  # Changed price
    }
    
    with patch('scheduler.jobs.AsyncSessionLocal') as mock_session:
        mock_session.return_value.__aenter__.return_value = mock_db
        
        with patch('scheduler.jobs.get_scraper_service', return_value=mock_scraper):
            await check_all_product_prices()
            
            # Verify scraper was called
            mock_scraper.fetch_product_details.assert_called_once_with(mock_product.url)
            
            # Verify product's last_known_price was updated
            assert mock_product.last_known_price == 899.99
            
            # Verify price history entry was added
            mock_db.add.assert_called()
            
            # Verify commit was called
            mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_check_all_product_prices_handles_errors():
    """Test price check job handles errors gracefully."""
    
    # Create mock products
    mock_product1 = Product(
        id=1,
        url="https://www.alza.cz/test1",
        name="Test Product 1",
        eshop="alza",
        last_known_price=999.99,
        last_check_time=datetime.now(timezone.utc),
        is_tracked=True
    )
    
    mock_product2 = Product(
        id=2,
        url="https://www.alza.cz/test2",
        name="Test Product 2",
        eshop="alza",
        last_known_price=799.99,
        last_check_time=datetime.now(timezone.utc),
        is_tracked=True
    )
    
    # Mock database session
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_product1, mock_product2]
    mock_db.execute.return_value = mock_result
    
    # Mock scraper service to fail on first product but succeed on second
    mock_scraper = AsyncMock()
    mock_scraper.fetch_product_details.side_effect = [
        Exception("Network error"),  # First call fails
        {"name": "Test Product 2", "price": 799.99}  # Second call succeeds
    ]
    
    with patch('scheduler.jobs.AsyncSessionLocal') as mock_session:
        mock_session.return_value.__aenter__.return_value = mock_db
        
        with patch('scheduler.jobs.get_scraper_service', return_value=mock_scraper):
            # Should not raise exception
            await check_all_product_prices()
            
            # Verify both products were attempted
            assert mock_scraper.fetch_product_details.call_count == 2
            
            # Verify commit was still called despite error
            mock_db.commit.assert_called_once()
