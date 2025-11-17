"""Site-specific handlers for web scraping.

This module contains handlers for different e-commerce sites, each implementing
site-specific logic for product extraction.
"""

import logging
import re
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)


class BaseSiteHandler(ABC):
    """Base class for site-specific scrapers."""
    
    def __init__(self, page: Page):
        """Initialize the handler with a Playwright page."""
        self.page = page
    
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
        
        # Remove common currency symbols and whitespace
        cleaned_text = (price_text.replace(',', '.')  # Handle comma as decimal separator
                                  .replace(' ', '')
                                  .replace('\xa0', '')  # Non-breaking space
                                  .replace('Kč', '')
                                  .replace('CZK', '')
                                  .replace('zł', '')
                                  .replace('PLN', ''))
        
        # Extract numeric value - handle both dot and comma as decimal separators
        # First, try to find a number with decimal point
        price_match = re.search(r'([\d]+\.[\d]+|[\d]+)', cleaned_text)
        if price_match:
            try:
                return float(price_match.group(1))
            except ValueError:
                return None
        return None
    
    @abstractmethod
    async def extract_product_details(self) -> Dict[str, Any]:
        """
        Extract product details from the current page.
        
        Returns:
            dict: Dictionary with 'name', 'price', 'is_on_sale', and 'original_price' keys
        """
        pass
    
    @abstractmethod
    async def search_products(self, query: str, limit: int = 10) -> list:
        """
        Search for products on the site.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            list: List of search results
        """
        pass


class AlzaHandler(BaseSiteHandler):
    """Handler for Alza.cz e-commerce site."""
    
    async def extract_product_details(self) -> Dict[str, Any]:
        """Extract product details from Alza.cz product page."""
        try:
            await self.page.wait_for_selector("h1", timeout=10000)
        except PlaywrightTimeoutError:
            raise ValueError(
                "The product page did not load correctly. "
                "This might be because the page structure has changed or the product is no longer available. "
                "Please verify the URL and try again."
            )
        
        # Extract product name
        name_element = await self.page.query_selector("h1")
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
            price_element = await self.page.query_selector(selector)
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
        strikethrough_selectors = [
            ".price-box__old-price",
            ".old-price",
            "[class*='old-price']",
            "[class*='strikethrough']",
            "del",
            "s"
        ]
        
        for selector in strikethrough_selectors:
            old_price_element = await self.page.query_selector(selector)
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
                "[class*='akce']"
            ]
            
            for selector in sale_indicators:
                sale_element = await self.page.query_selector(selector)
                if sale_element:
                    sale_text = await sale_element.inner_text()
                    sale_text = sale_text.lower()
                    if any(word in sale_text for word in ['sale', 'sleva', 'akce', 'discount', 'akční']):
                        is_on_sale = True
                        break
        
        return {
            "name": name,
            "price": price,
            "is_on_sale": is_on_sale,
            "original_price": original_price
        }
    
    async def search_products(self, query: str, limit: int = 10) -> list:
        """Search Alza.cz for products."""
        from api.schemas import SearchResultItem
        
        try:
            # Navigate to Alza.cz if not already there
            if "alza.cz" not in self.page.url:
                await self.page.goto("https://www.alza.cz/", timeout=30000)
            
            # Find and fill search input
            try:
                search_input = await self.page.wait_for_selector('input[type="text"][name="extext"]', timeout=10000)
                await search_input.fill(query)
                await search_input.press("Enter")
                await self.page.wait_for_selector('.box.browsingitem, .browsingitem', timeout=15000)
            except PlaywrightTimeoutError:
                raise ValueError(
                    "Unable to perform search on Alza.cz. "
                    "The website layout may have changed or the search is taking too long."
                )
            
            # Get all product boxes
            product_boxes = await self.page.query_selector_all('.box.browsingitem, .browsingitem')
            
            results = []
            for box in product_boxes[:limit]:
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
                    
                    old_price_element = await box.query_selector('.price-box__old-price, .old-price, del, s')
                    if old_price_element:
                        old_price_text = await old_price_element.inner_text()
                        original_price = self._extract_price_from_text(old_price_text)
                        if original_price:
                            is_on_sale = True
                    
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
                except Exception:
                    continue
            
            return results
        except Exception as e:
            logger.error(f"Error searching Alza.cz: {e}")
            raise


class SmartyHandler(BaseSiteHandler):
    """Handler for Smarty.cz e-commerce site."""
    
    async def extract_product_details(self) -> Dict[str, Any]:
        """Extract product details from Smarty.cz product page."""
        try:
            # Wait for product name - Smarty uses h1 for product titles
            await self.page.wait_for_selector("h1", timeout=10000)
        except PlaywrightTimeoutError:
            raise ValueError(
                "The Smarty.cz product page did not load correctly. "
                "Please verify the URL and try again."
            )
        
        # Extract product name
        name_element = await self.page.query_selector("h1")
        name = await name_element.inner_text() if name_element else "Unknown"
        name = name.strip()
        
        # Initialize sale status
        is_on_sale = False
        original_price = None
        
        # Extract price - try multiple selectors for Smarty
        price = None
        price_selectors = [
            ".price-final",
            ".price-current",
            ".product-price",
            "[class*='price']",
            ".price"
        ]
        
        for selector in price_selectors:
            price_element = await self.page.query_selector(selector)
            if price_element:
                price_text = await price_element.inner_text()
                price = self._extract_price_from_text(price_text)
                if price:
                    break
        
        if price is None:
            raise ValueError(
                "Unable to find the product price on Smarty.cz. "
                "The page layout may have changed or the product might not be available."
            )
        
        # Check for sale/discount indicators
        strikethrough_selectors = [
            ".price-old",
            ".price-original",
            "[class*='old-price']",
            "[class*='original-price']",
            "del",
            "s"
        ]
        
        for selector in strikethrough_selectors:
            old_price_element = await self.page.query_selector(selector)
            if old_price_element:
                old_price_text = await old_price_element.inner_text()
                original_price = self._extract_price_from_text(old_price_text)
                if original_price:
                    is_on_sale = True
                    break
        
        # Check for sale badges
        if not is_on_sale:
            sale_indicators = [
                ".badge-sale",
                ".label-sale",
                "[class*='sale']",
                "[class*='discount']",
                "[class*='sleva']",
                "[class*='akce']"
            ]
            
            for selector in sale_indicators:
                sale_element = await self.page.query_selector(selector)
                if sale_element:
                    sale_text = await sale_element.inner_text()
                    sale_text = sale_text.lower()
                    if any(word in sale_text for word in ['sale', 'sleva', 'akce', 'discount', 'akční']):
                        is_on_sale = True
                        break
        
        return {
            "name": name,
            "price": price,
            "is_on_sale": is_on_sale,
            "original_price": original_price
        }
    
    async def search_products(self, query: str, limit: int = 10) -> list:
        """Search Smarty.cz for products."""
        from api.schemas import SearchResultItem
        
        try:
            # Navigate to Smarty.cz
            await self.page.goto("https://www.smarty.cz/", timeout=30000)
            
            # Find and fill search input
            try:
                search_input = await self.page.wait_for_selector('input[type="search"], input[name="q"], input[name="search"]', timeout=10000)
                await search_input.fill(query)
                await search_input.press("Enter")
                await self.page.wait_for_selector('.product-item, .product, [class*="product"]', timeout=15000)
            except PlaywrightTimeoutError:
                raise ValueError(
                    "Unable to perform search on Smarty.cz. "
                    "The website layout may have changed."
                )
            
            # Get all product boxes
            product_boxes = await self.page.query_selector_all('.product-item, .product, [class*="product-box"]')
            
            results = []
            for box in product_boxes[:limit]:
                try:
                    # Extract product name
                    name_element = await box.query_selector('a[class*="name"], .product-name, h3 a, h2 a')
                    if not name_element:
                        continue
                    name = await name_element.inner_text()
                    name = name.strip()
                    
                    # Extract product URL
                    product_url = await name_element.get_attribute('href')
                    if product_url and not product_url.startswith('http'):
                        product_url = f"https://www.smarty.cz{product_url}"
                    
                    # Extract price
                    price_element = await box.query_selector('.price-final, .price, [class*="price"]')
                    if not price_element:
                        continue
                    price_text = await price_element.inner_text()
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
                    
                    old_price_element = await box.query_selector('.price-old, .price-original, del, s')
                    if old_price_element:
                        old_price_text = await old_price_element.inner_text()
                        original_price = self._extract_price_from_text(old_price_text)
                        if original_price:
                            is_on_sale = True
                    
                    if not is_on_sale:
                        sale_badge = await box.query_selector('.badge-sale, .label-sale, [class*="sale"]')
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
                except Exception:
                    continue
            
            return results
        except Exception as e:
            logger.error(f"Error searching Smarty.cz: {e}")
            raise


class AllegroHandler(BaseSiteHandler):
    """Handler for Allegro.pl marketplace."""
    
    async def extract_product_details(self) -> Dict[str, Any]:
        """Extract product details from Allegro.pl product page."""
        try:
            # Wait for product name
            await self.page.wait_for_selector("h1", timeout=10000)
        except PlaywrightTimeoutError:
            raise ValueError(
                "The Allegro.pl product page did not load correctly. "
                "Please verify the URL and try again."
            )
        
        # Extract product name
        name_element = await self.page.query_selector("h1")
        name = await name_element.inner_text() if name_element else "Unknown"
        name = name.strip()
        
        # Initialize sale status
        is_on_sale = False
        original_price = None
        
        # Extract price - Allegro uses specific selectors
        price = None
        price_selectors = [
            "[data-role='price']",
            "[class*='price']",
            ".price",
            "meta[property='product:price:amount']"
        ]
        
        for selector in price_selectors:
            price_element = await self.page.query_selector(selector)
            if price_element:
                if selector.startswith("meta"):
                    price_text = await price_element.get_attribute("content")
                else:
                    price_text = await price_element.inner_text()
                price = self._extract_price_from_text(price_text)
                if price:
                    break
        
        if price is None:
            raise ValueError(
                "Unable to find the product price on Allegro.pl. "
                "The page layout may have changed or the product might not be available."
            )
        
        # Check for sale/discount indicators
        strikethrough_selectors = [
            "[data-role='old-price']",
            ".price-old",
            "[class*='old-price']",
            "del",
            "s"
        ]
        
        for selector in strikethrough_selectors:
            old_price_element = await self.page.query_selector(selector)
            if old_price_element:
                old_price_text = await old_price_element.inner_text()
                original_price = self._extract_price_from_text(old_price_text)
                if original_price:
                    is_on_sale = True
                    break
        
        # Check for sale badges
        if not is_on_sale:
            sale_indicators = [
                "[class*='badge']",
                "[class*='promocja']",
                "[class*='sale']",
                "[class*='discount']"
            ]
            
            for selector in sale_indicators:
                sale_element = await self.page.query_selector(selector)
                if sale_element:
                    sale_text = await sale_element.inner_text()
                    sale_text = sale_text.lower()
                    if any(word in sale_text for word in ['sale', 'promocja', 'obniżka', 'discount']):
                        is_on_sale = True
                        break
        
        return {
            "name": name,
            "price": price,
            "is_on_sale": is_on_sale,
            "original_price": original_price
        }
    
    async def search_products(self, query: str, limit: int = 10) -> list:
        """Search Allegro.pl for products."""
        from api.schemas import SearchResultItem
        
        try:
            # Navigate to Allegro.pl
            await self.page.goto("https://allegro.pl/", timeout=30000)
            
            # Find and fill search input
            try:
                search_input = await self.page.wait_for_selector('input[type="search"], input[name="string"]', timeout=10000)
                await search_input.fill(query)
                await search_input.press("Enter")
                await self.page.wait_for_selector('[data-role="offer"], article, [class*="offer"]', timeout=15000)
            except PlaywrightTimeoutError:
                raise ValueError(
                    "Unable to perform search on Allegro.pl. "
                    "The website layout may have changed."
                )
            
            # Get all product boxes
            product_boxes = await self.page.query_selector_all('[data-role="offer"], article, [class*="offer-item"]')
            
            results = []
            for box in product_boxes[:limit]:
                try:
                    # Extract product name
                    name_element = await box.query_selector('a[class*="name"], h2 a, [data-role="offer-title"]')
                    if not name_element:
                        continue
                    name = await name_element.inner_text()
                    name = name.strip()
                    
                    # Extract product URL
                    product_url = await name_element.get_attribute('href')
                    if product_url and not product_url.startswith('http'):
                        product_url = f"https://allegro.pl{product_url}"
                    
                    # Extract price
                    price_element = await box.query_selector('[data-role="price"], .price, [class*="price"]')
                    if not price_element:
                        continue
                    price_text = await price_element.inner_text()
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
                    
                    old_price_element = await box.query_selector('[data-role="old-price"], .price-old, del')
                    if old_price_element:
                        old_price_text = await old_price_element.inner_text()
                        original_price = self._extract_price_from_text(old_price_text)
                        if original_price:
                            is_on_sale = True
                    
                    if not is_on_sale:
                        sale_badge = await box.query_selector('[class*="badge"], [class*="promocja"]')
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
                except Exception:
                    continue
            
            return results
        except Exception as e:
            logger.error(f"Error searching Allegro.pl: {e}")
            raise


def get_site_handler(url: str, page: Page) -> Optional[BaseSiteHandler]:
    """
    Get the appropriate site handler for a given URL.
    
    Args:
        url: Product or site URL
        page: Playwright page object
        
    Returns:
        BaseSiteHandler: Site-specific handler or None if unsupported
    """
    url_lower = url.lower()
    
    if "alza.cz" in url_lower:
        return AlzaHandler(page)
    elif "smarty.cz" in url_lower:
        return SmartyHandler(page)
    elif "allegro.pl" in url_lower:
        return AllegroHandler(page)
    
    return None
