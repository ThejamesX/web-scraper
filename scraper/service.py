"""Web scraping service using Playwright."""

import re
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page, Playwright
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
            await page.goto(url, timeout=settings.scraper_timeout)
            
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
            dict: Dictionary with 'name' and 'price' keys
        """
        # Wait for product name
        await page.wait_for_selector("h1", timeout=10000)
        
        # Extract product name
        name_element = await page.query_selector("h1")
        name = await name_element.inner_text() if name_element else "Unknown"
        name = name.strip()
        
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
                # Extract numeric price value
                price_match = re.search(r'([\d\s]+)', price_text.replace(',', '').replace(' ', ''))
                if price_match:
                    price = float(price_match.group(1).strip())
                    break
        
        if price is None:
            raise ValueError("Could not extract price from page")
        
        return {
            "name": name,
            "price": price
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
            return await self._search_alza(query, limit)
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
            await page.goto("https://www.alza.cz/", timeout=settings.scraper_timeout)
            
            # Find and fill search input
            search_input = await page.wait_for_selector('input[type="text"][name="extext"]', timeout=10000)
            await search_input.fill(query)
            
            # Submit search
            await search_input.press("Enter")
            
            # Wait for results page
            await page.wait_for_selector('.box.browsingitem, .browsingitem', timeout=15000)
            
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
                    
                    # Parse price
                    price_match = re.search(r'([\d\s]+)', price_text.replace(',', '').replace(' ', ''))
                    if not price_match:
                        continue
                    price = float(price_match.group(1).strip())
                    
                    # Extract image URL
                    image_url = None
                    img_element = await box.query_selector('img')
                    if img_element:
                        image_url = await img_element.get_attribute('src')
                        if not image_url:
                            image_url = await img_element.get_attribute('data-src')
                    
                    results.append(SearchResultItem(
                        name=name,
                        price=price,
                        product_url=product_url,
                        image_url=image_url
                    ))
                except Exception as e:
                    # Skip problematic items
                    continue
            
            return results
        finally:
            await page.close()


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
