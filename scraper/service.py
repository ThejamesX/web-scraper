"""Web scraping service using Playwright."""

import re
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page, Playwright, Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError
from core.config import settings
from api.schemas import SearchResultItem


class ScraperService:
    """Service for scraping e-commerce sites using Playwright."""
    
    def __init__(self):
        """Initialize the scraper service."""
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
    
    async def initialize(self):
        """Launch Playwright and browser."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=settings.scraper_headless
        )
    
    async def close(self):
        """Close browser and Playwright."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    @staticmethod
    def _extract_price_from_text(price_text: str) -> Optional[float]:
        """
        Extract numeric price value from text.
        
        Args:
            price_text: Text containing price
            
        Returns:
            float: Extracted price or None if not found
        """
        if not price_text:
            return None
        
        # Remove common currency symbols and separators
        cleaned_text = price_text.replace(',', '').replace(' ', '').replace('Kč', '').replace('CZK', '')
        
        # Extract numeric value
        price_match = re.search(r'([\d]+(?:\.[\d]+)?)', cleaned_text)
        if price_match:
            try:
                return float(price_match.group(1))
            except ValueError:
                return None
        return None
    
    async def fetch_product_details(self, url: str) -> dict:
        """
        Fetch product details from a product page URL.
        
        Args:
            url: Product page URL
            
        Returns:
            dict: Dictionary with 'name' and 'price' keys
            
        Raises:
            Exception: If product details cannot be extracted
        """
        if not self.browser:
            await self.initialize()
        
        page = await self.browser.new_page()
        try:
            try:
                await page.goto(url, timeout=settings.scraper_timeout)
            except PlaywrightError as e:
                error_msg = str(e)
                if "ERR_NAME_NOT_RESOLVED" in error_msg or "net::" in error_msg:
                    # If mock mode is enabled, return mock data
                    if settings.scraper_mock_mode:
                        await page.close()
                        return self._get_mock_product_details(url)
                    raise ValueError(
                        f"Cannot reach the website at {url}. "
                        "Please check your internet connection or try again later. "
                        "The website might be temporarily unavailable."
                    )
                elif "Timeout" in error_msg or "timeout" in error_msg:
                    raise ValueError(
                        f"The website at {url} is taking too long to respond. "
                        "This could be due to slow internet connection or high server load. "
                        "Please try again in a few moments."
                    )
                else:
                    raise ValueError(f"Unable to load product page: {error_msg}")
            
            # Determine which e-shop and use appropriate selectors
            if "alza.cz" in url:
                return await self._fetch_alza_product_details(page)
            else:
                raise ValueError(f"Unsupported e-shop URL: {url}")
        finally:
            await page.close()
    
    async def _fetch_alza_product_details(self, page: Page) -> dict:
        """
        Extract product details from Alza.cz product page.
        
        Args:
            page: Playwright page object
            
        Returns:
            dict: Dictionary with 'name', 'price', 'is_on_sale', and 'original_price' keys
        """
        # Wait for product name
        try:
            await page.wait_for_selector("h1", timeout=10000)
        except PlaywrightTimeoutError:
            raise ValueError(
                "The product page did not load correctly. "
                "This might be because the page structure has changed or the product is no longer available. "
                "Please verify the URL and try again."
            )
        
        # Extract product name
        name_element = await page.query_selector("h1")
        name = await name_element.inner_text() if name_element else "Unknown"
        name = name.strip()
        
        # Initialize sale status
        is_on_sale = False
        original_price = None
        
        # Extract price - try multiple selectors
        price = None
        price_selectors = [
            ".price-box__price",
            ".price",
            "[class*='price']"
        ]
        
        for selector in price_selectors:
            price_element = await page.query_selector(selector)
            if price_element:
                price_text = await price_element.inner_text()
                price = self._extract_price_from_text(price_text)
                if price:
                    break
        
        if price is None:
            raise ValueError(
                "Unable to find the product price on this page. "
                "The page layout may have changed or the product might not be available. "
                "Please check the product URL and try again."
            )
        
        # Check for sale/discount indicators
        # Look for crossed-out original price
        strikethrough_selectors = [
            ".price-box__old-price",
            ".old-price",
            "[class*='old-price']",
            "[class*='strikethrough']",
            "del",
            "s"
        ]
        
        for selector in strikethrough_selectors:
            old_price_element = await page.query_selector(selector)
            if old_price_element:
                old_price_text = await old_price_element.inner_text()
                original_price = self._extract_price_from_text(old_price_text)
                if original_price:
                    is_on_sale = True
                    break
        
        # If no strikethrough price found, check for sale badges/labels
        if not is_on_sale:
            sale_indicators = [
                ".badge-sale",
                ".sale-badge",
                "[class*='sale']",
                "[class*='discount']",
                "[class*='akce']"  # Czech for "sale/action"
            ]
            
            for selector in sale_indicators:
                sale_element = await page.query_selector(selector)
                if sale_element:
                    sale_text = await sale_element.inner_text()
                    sale_text = sale_text.lower()
                    # Check if text contains sale indicators
                    if any(word in sale_text for word in ['sale', 'sleva', 'akce', 'discount', 'akční']):
                        is_on_sale = True
                        break
        
        return {
            "name": name,
            "price": price,
            "is_on_sale": is_on_sale,
            "original_price": original_price
        }
    
    async def search_site(self, site: str, query: str, limit: int = 10) -> list[SearchResultItem]:
        """
        Search an e-commerce site for products.
        
        Args:
            site: E-commerce site name (e.g., 'alza')
            query: Search query
            limit: Maximum number of results to return (default: 10)
            
        Returns:
            list[SearchResultItem]: List of search results
            
        Raises:
            ValueError: If site is not supported
        """
        if not self.browser:
            await self.initialize()
        
        if site.lower() == "alza":
            try:
                return await self._search_alza(query, limit)
            except ValueError as e:
                # If mock mode is enabled, return mock data instead of failing
                if settings.scraper_mock_mode:
                    return self._get_mock_search_results(query, limit)
                raise
        else:
            raise ValueError(f"Unsupported site: {site}")
    
    async def _search_alza(self, query: str, limit: int = 10) -> list[SearchResultItem]:
        """
        Search Alza.cz for products.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            list[SearchResultItem]: Search results
        """
        page = await self.browser.new_page()
        try:
            # Navigate to Alza.cz
            try:
                await page.goto("https://www.alza.cz/", timeout=settings.scraper_timeout)
            except PlaywrightError as e:
                error_msg = str(e)
                if "ERR_NAME_NOT_RESOLVED" in error_msg or "net::" in error_msg:
                    raise ValueError(
                        "Cannot connect to Alza.cz. "
                        "Please check your internet connection and try again."
                    )
                elif "Timeout" in error_msg or "timeout" in error_msg:
                    raise ValueError(
                        "Alza.cz is not responding. The site may be experiencing high traffic. "
                        "Please try again in a few moments."
                    )
                else:
                    raise ValueError(f"Failed to access Alza.cz: {error_msg}")
            
            # Find and fill search input
            try:
                search_input = await page.wait_for_selector('input[type="text"][name="extext"]', timeout=10000)
                await search_input.fill(query)
                
                # Submit search
                await search_input.press("Enter")
                
                # Wait for results page
                await page.wait_for_selector('.box.browsingitem, .browsingitem', timeout=15000)
            except PlaywrightTimeoutError:
                raise ValueError(
                    "Unable to perform search on Alza.cz. "
                    "The website layout may have changed or the search is taking too long. "
                    "Please try a different search term or try again later."
                )
            
            # Get all product boxes
            product_boxes = await page.query_selector_all('.box.browsingitem, .browsingitem')
            
            results = []
            for i, box in enumerate(product_boxes[:limit]):
                try:
                    # Extract product name
                    name_element = await box.query_selector('a.name, .name a')
                    if not name_element:
                        continue
                    name = await name_element.inner_text()
                    name = name.strip()
                    
                    # Extract product URL
                    product_url = await name_element.get_attribute('href')
                    if product_url and not product_url.startswith('http'):
                        product_url = f"https://www.alza.cz{product_url}"
                    
                    # Extract price
                    price_element = await box.query_selector('.price-box__price, .price')
                    if not price_element:
                        continue
                    price_text = await price_element.inner_text()
                    
                    # Parse price using helper method
                    price = self._extract_price_from_text(price_text)
                    if not price:
                        continue
                    
                    # Extract image URL
                    image_url = None
                    img_element = await box.query_selector('img')
                    if img_element:
                        image_url = await img_element.get_attribute('src')
                        if not image_url:
                            image_url = await img_element.get_attribute('data-src')
                    
                    # Check for sale status
                    is_on_sale = False
                    original_price = None
                    
                    # Look for old/strikethrough price
                    old_price_element = await box.query_selector('.price-box__old-price, .old-price, del, s')
                    if old_price_element:
                        old_price_text = await old_price_element.inner_text()
                        original_price = self._extract_price_from_text(old_price_text)
                        if original_price:
                            is_on_sale = True
                    
                    # If no strikethrough price, check for sale badge
                    if not is_on_sale:
                        sale_badge = await box.query_selector('.badge-sale, .sale-badge, [class*="sale"], [class*="akce"]')
                        if sale_badge:
                            is_on_sale = True
                    
                    results.append(SearchResultItem(
                        name=name,
                        price=price,
                        product_url=product_url,
                        image_url=image_url,
                        is_on_sale=is_on_sale,
                        original_price=original_price
                    ))
                except Exception as e:
                    # Skip problematic items
                    continue
            
            return results
        finally:
            await page.close()
    
    def _get_mock_search_results(self, query: str, limit: int = 10) -> list[SearchResultItem]:
        """
        Generate mock search results for testing/demo purposes.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            list[SearchResultItem]: Mock search results
        """
        results = []
        for i in range(min(5, limit)):
            results.append(SearchResultItem(
                name=f"{query.title()} - Product {i+1}",
                price=999.99 + (i * 100),
                product_url=f"https://www.alza.cz/mock-product-{i+1}",
                image_url=f"https://cdn.alza.cz/mock-image-{i+1}.jpg",
                is_on_sale=(i % 2 == 0),  # Every other product is on sale
                original_price=(999.99 + (i * 100) + 200) if i % 2 == 0 else None
            ))
        return results
    
    def _get_mock_product_details(self, url: str) -> dict:
        """
        Generate mock product details for testing/demo purposes.
        
        Args:
            url: Product URL
            
        Returns:
            dict: Mock product details
        """
        # Extract a product identifier from URL if possible
        product_id = url.split('/')[-1] if '/' in url else 'unknown'
        
        return {
            "name": f"Mock Product - {product_id}",
            "price": 12999.00,
            "is_on_sale": False,
            "original_price": None
        }


# Global scraper service instance
_scraper_service: Optional[ScraperService] = None


async def get_scraper_service() -> ScraperService:
    """
    Dependency function to get scraper service.
    
    Returns:
        ScraperService: Scraper service instance
    """
    global _scraper_service
    if _scraper_service is None:
        _scraper_service = ScraperService()
        await _scraper_service.initialize()
    return _scraper_service
