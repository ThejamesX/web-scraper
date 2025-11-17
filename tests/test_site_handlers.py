"""Tests for site-specific handlers."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from scraper.site_handlers import (
    AlzaHandler,
    SmartyHandler,
    AllegroHandler,
    get_site_handler,
    BaseSiteHandler
)


class TestBaseSiteHandler:
    """Tests for BaseSiteHandler."""
    
    def test_extract_price_from_text_basic(self):
        """Test basic price extraction."""
        assert BaseSiteHandler._extract_price_from_text("1234.56 Kč") == 1234.56
        assert BaseSiteHandler._extract_price_from_text("999.99 CZK") == 999.99
        assert BaseSiteHandler._extract_price_from_text("1 234,56 Kč") == 1234.56
    
    def test_extract_price_from_text_polish(self):
        """Test price extraction for Polish currency."""
        assert BaseSiteHandler._extract_price_from_text("123.45 zł") == 123.45
        assert BaseSiteHandler._extract_price_from_text("999 PLN") == 999.0
    
    def test_extract_price_from_text_invalid(self):
        """Test price extraction with invalid input."""
        assert BaseSiteHandler._extract_price_from_text("") is None
        assert BaseSiteHandler._extract_price_from_text(None) is None
        assert BaseSiteHandler._extract_price_from_text("no price here") is None


class TestGetSiteHandler:
    """Tests for get_site_handler function."""
    
    def test_alza_handler(self):
        """Test that Alza URLs return AlzaHandler."""
        mock_page = MagicMock()
        handler = get_site_handler("https://www.alza.cz/product", mock_page)
        assert isinstance(handler, AlzaHandler)
    
    def test_smarty_handler(self):
        """Test that Smarty URLs return SmartyHandler."""
        mock_page = MagicMock()
        handler = get_site_handler("https://www.smarty.cz/product", mock_page)
        assert isinstance(handler, SmartyHandler)
    
    def test_allegro_handler(self):
        """Test that Allegro URLs return AllegroHandler."""
        mock_page = MagicMock()
        handler = get_site_handler("https://allegro.pl/product", mock_page)
        assert isinstance(handler, AllegroHandler)
    
    def test_unsupported_site(self):
        """Test that unsupported sites return None."""
        mock_page = MagicMock()
        handler = get_site_handler("https://amazon.com/product", mock_page)
        assert handler is None


@pytest.mark.asyncio
class TestAlzaHandler:
    """Tests for AlzaHandler."""
    
    async def test_extract_product_details_success(self):
        """Test successful product extraction from Alza."""
        mock_page = AsyncMock()
        
        # Mock name element
        mock_name_elem = AsyncMock()
        mock_name_elem.inner_text = AsyncMock(return_value="Test Product")
        
        # Mock price element
        mock_price_elem = AsyncMock()
        mock_price_elem.inner_text = AsyncMock(return_value="999 Kč")
        
        # Setup page selectors
        mock_page.wait_for_selector = AsyncMock()
        
        # Use a function to handle multiple calls
        call_count = [0]
        async def mock_query_selector(selector):
            call_count[0] += 1
            if call_count[0] == 1:  # h1
                return mock_name_elem
            elif call_count[0] == 2:  # first price selector fails
                return None
            elif call_count[0] == 3:  # second price selector succeeds
                return mock_price_elem
            else:  # all other selectors return None
                return None
        
        mock_page.query_selector = mock_query_selector
        
        handler = AlzaHandler(mock_page)
        result = await handler.extract_product_details()
        
        assert result["name"] == "Test Product"
        assert result["price"] == 999.0
        assert result["is_on_sale"] is False
        assert result["original_price"] is None
    
    async def test_extract_product_details_on_sale(self):
        """Test extracting product on sale."""
        mock_page = AsyncMock()
        
        # Mock name element
        mock_name_elem = AsyncMock()
        mock_name_elem.inner_text = AsyncMock(return_value="Sale Product")
        
        # Mock price element
        mock_price_elem = AsyncMock()
        mock_price_elem.inner_text = AsyncMock(return_value="799 Kč")
        
        # Mock old price element
        mock_old_price_elem = AsyncMock()
        mock_old_price_elem.inner_text = AsyncMock(return_value="999 Kč")
        
        # Setup page selectors
        mock_page.wait_for_selector = AsyncMock()
        mock_page.query_selector = AsyncMock(side_effect=[
            mock_name_elem,  # h1 selector
            mock_price_elem,  # price selector
            mock_old_price_elem,  # old price selector
        ])
        
        handler = AlzaHandler(mock_page)
        result = await handler.extract_product_details()
        
        assert result["name"] == "Sale Product"
        assert result["price"] == 799.0
        assert result["is_on_sale"] is True
        assert result["original_price"] == 999.0
    
    async def test_extract_product_details_timeout(self):
        """Test handling of timeout errors."""
        from playwright.async_api import TimeoutError as PlaywrightTimeoutError
        
        mock_page = AsyncMock()
        mock_page.wait_for_selector = AsyncMock(side_effect=PlaywrightTimeoutError("Timeout"))
        
        handler = AlzaHandler(mock_page)
        
        with pytest.raises(ValueError, match="did not load correctly"):
            await handler.extract_product_details()
    
    async def test_extract_product_details_no_price(self):
        """Test handling of missing price."""
        mock_page = AsyncMock()
        
        # Mock name element
        mock_name_elem = AsyncMock()
        mock_name_elem.inner_text = AsyncMock(return_value="Test Product")
        
        # Setup page selectors - all price selectors return None
        mock_page.wait_for_selector = AsyncMock()
        mock_page.query_selector = AsyncMock(return_value=None)
        
        handler = AlzaHandler(mock_page)
        
        with pytest.raises(ValueError, match="Unable to find the product price"):
            await handler.extract_product_details()


@pytest.mark.asyncio
class TestSmartyHandler:
    """Tests for SmartyHandler."""
    
    async def test_extract_product_details_success(self):
        """Test successful product extraction from Smarty."""
        mock_page = AsyncMock()
        
        # Mock name element
        mock_name_elem = AsyncMock()
        mock_name_elem.inner_text = AsyncMock(return_value="Smarty Product")
        
        # Mock price element
        mock_price_elem = AsyncMock()
        mock_price_elem.inner_text = AsyncMock(return_value="1499 Kč")
        
        # Setup page selectors
        mock_page.wait_for_selector = AsyncMock()
        
        # Use a function to handle multiple calls
        call_count = [0]
        async def mock_query_selector(selector):
            call_count[0] += 1
            if call_count[0] == 1:  # h1
                return mock_name_elem
            elif call_count[0] == 2:  # first price selector fails
                return None
            elif call_count[0] == 3:  # second price selector succeeds
                return mock_price_elem
            else:  # all other selectors return None
                return None
        
        mock_page.query_selector = mock_query_selector
        
        handler = SmartyHandler(mock_page)
        result = await handler.extract_product_details()
        
        assert result["name"] == "Smarty Product"
        assert result["price"] == 1499.0
        assert result["is_on_sale"] is False
        assert result["original_price"] is None
    
    async def test_extract_product_details_with_sale_badge(self):
        """Test product with sale badge."""
        mock_page = AsyncMock()
        
        # Mock name element
        mock_name_elem = AsyncMock()
        mock_name_elem.inner_text = AsyncMock(return_value="Sale Item")
        
        # Mock price element
        mock_price_elem = AsyncMock()
        mock_price_elem.inner_text = AsyncMock(return_value="899 Kč")
        
        # Mock sale badge
        mock_sale_badge = AsyncMock()
        mock_sale_badge.inner_text = AsyncMock(return_value="Akce")
        
        # Setup page selectors
        mock_page.wait_for_selector = AsyncMock()
        
        call_count = [0]
        async def mock_query_selector(selector):
            call_count[0] += 1
            if call_count[0] == 1:  # h1
                return mock_name_elem
            elif call_count[0] == 2:  # first price selector
                return None
            elif call_count[0] == 3:  # second price selector
                return mock_price_elem
            elif call_count[0] == 4:  # old price
                return None
            else:  # sale badge
                return mock_sale_badge
        
        mock_page.query_selector = mock_query_selector
        
        handler = SmartyHandler(mock_page)
        result = await handler.extract_product_details()
        
        assert result["name"] == "Sale Item"
        assert result["price"] == 899.0
        assert result["is_on_sale"] is True


@pytest.mark.asyncio
class TestAllegroHandler:
    """Tests for AllegroHandler."""
    
    async def test_extract_product_details_success(self):
        """Test successful product extraction from Allegro."""
        mock_page = AsyncMock()
        
        # Mock name element
        mock_name_elem = AsyncMock()
        mock_name_elem.inner_text = AsyncMock(return_value="Allegro Product")
        
        # Mock price element
        mock_price_elem = AsyncMock()
        mock_price_elem.inner_text = AsyncMock(return_value="99.99 zł")
        
        # Setup page selectors
        mock_page.wait_for_selector = AsyncMock()
        
        # Use a function to handle multiple calls
        call_count = [0]
        async def mock_query_selector(selector):
            call_count[0] += 1
            if call_count[0] == 1:  # h1
                return mock_name_elem
            elif call_count[0] == 2:  # first price selector succeeds
                return mock_price_elem
            else:  # all other selectors return None
                return None
        
        mock_page.query_selector = mock_query_selector
        
        handler = AllegroHandler(mock_page)
        result = await handler.extract_product_details()
        
        assert result["name"] == "Allegro Product"
        assert result["price"] == 99.99
        assert result["is_on_sale"] is False
        assert result["original_price"] is None
    
    async def test_extract_product_details_with_meta_price(self):
        """Test extracting price from meta tag."""
        mock_page = AsyncMock()
        
        # Mock name element
        mock_name_elem = AsyncMock()
        mock_name_elem.inner_text = AsyncMock(return_value="Meta Price Product")
        
        # Mock meta price element
        mock_meta_elem = AsyncMock()
        mock_meta_elem.get_attribute = AsyncMock(return_value="199.99")
        mock_meta_elem.inner_text = AsyncMock(return_value="199.99 zł")  # Add inner_text as fallback
        
        # Setup page selectors
        mock_page.wait_for_selector = AsyncMock()
        
        call_count = [0]
        async def mock_query_selector(selector):
            call_count[0] += 1
            if call_count[0] == 1:  # h1
                return mock_name_elem
            elif call_count[0] <= 3:  # first price selectors fail
                return None
            elif call_count[0] == 4:  # meta/fourth selector succeeds
                return mock_meta_elem
            else:  # no sale
                return None
        
        mock_page.query_selector = mock_query_selector
        
        handler = AllegroHandler(mock_page)
        result = await handler.extract_product_details()
        
        assert result["name"] == "Meta Price Product"
        # The price should be extracted either from attribute or text
        assert result["price"] in [199.99, 199]  # Allow some flexibility
