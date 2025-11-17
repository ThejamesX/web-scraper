"""Web scraping service using BeautifulSoup and httpx."""

import logging
import re
from typing import Optional
from bs4 import BeautifulSoup
import httpx
from core.config import settings
from api.schemas import SearchResultItem

# Configure logging
logger = logging.getLogger(__name__)


class ScraperService:
    """Service for scraping e-commerce sites using BeautifulSoup and httpx."""
    
    def __init__(self):
        """Initialize the scraper service."""
        self.client: Optional[httpx.AsyncClient] = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def initialize(self):
        """Initialize the HTTP client."""
        logger.info("Initializing HTTP client...")
        self.client = httpx.AsyncClient(
            headers=self.headers,
            timeout=httpx.Timeout(settings.scraper_timeout / 1000.0),  # Convert ms to seconds
            follow_redirects=True,
            verify=True
        )
        logger.info("HTTP client initialized successfully")
    
    async def close(self):
        """Close HTTP client."""
        logger.info("Closing HTTP client...")
        if self.client:
            await self.client.aclose()
        logger.info("HTTP client closed successfully")
    
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
        logger.info(f"Fetching product details from: {url}")
        if not self.client:
            await self.initialize()
        
        try:
            try:
                response = await self.client.get(url)
                response.raise_for_status()
            except httpx.ConnectError as e:
                # If mock mode is enabled, return mock data
                if settings.scraper_mock_mode:
                    return self._get_mock_product_details(url)
                raise ValueError(
                    f"Cannot reach the website at {url}. "
                    "Please check your internet connection or try again later. "
                    "The website might be temporarily unavailable."
                )
            except httpx.TimeoutException:
                raise ValueError(
                    f"The website at {url} is taking too long to respond. "
                    "This could be due to slow internet connection or high server load. "
                    "Please try again in a few moments."
                )
            except httpx.HTTPStatusError as e:
                raise ValueError(f"Unable to load product page: HTTP {e.response.status_code}")
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Detect site and extract accordingly
            if "alza.cz" in url:
                return await self._fetch_alza_product_details(soup)
            elif "smarty.cz" in url:
                return await self._fetch_smarty_product_details(soup)
            elif "allegro.pl" in url:
                return await self._fetch_allegro_product_details(soup)
            else:
                raise ValueError(
                    f"Unsupported e-shop URL: {url}. "
                    f"Currently supported sites: Alza.cz, Smarty.cz, Allegro.pl"
                )
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching product details: {e}")
            raise ValueError(f"Unable to fetch product details: {str(e)}")
    
    async def _fetch_alza_product_details(self, soup: BeautifulSoup) -> dict:
        """
        Extract product details from Alza.cz product page.
        
        Args:
            soup: BeautifulSoup parsed page
            
        Returns:
            dict: Dictionary with 'name', 'price', 'is_on_sale', and 'original_price' keys
        """
        # Extract product name
        name_element = soup.find("h1")
        if not name_element:
            raise ValueError(
                "The product page did not load correctly. "
                "This might be because the page structure has changed or the product is no longer available. "
                "Please verify the URL and try again."
            )
        name = name_element.get_text(strip=True)
        
        # Initialize sale status
        is_on_sale = False
        original_price = None
        
        # Extract price - try multiple selectors
        price = None
        price_selectors = [
            {"class_": "price-box__price"},
            {"class_": "price"},
            {"class_": lambda x: x and 'price' in x}
        ]
        
        for selector in price_selectors:
            price_element = soup.find(attrs=selector)
            if price_element:
                price_text = price_element.get_text(strip=True)
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
            soup.find(class_="price-box__old-price"),
            soup.find(class_="old-price"),
            soup.find(class_=lambda x: x and 'old-price' in x),
            soup.find("del"),
            soup.find("s")
        ]
        
        for old_price_element in strikethrough_selectors:
            if old_price_element:
                old_price_text = old_price_element.get_text(strip=True)
                original_price = self._extract_price_from_text(old_price_text)
                if original_price:
                    is_on_sale = True
                    break
        
        # If no strikethrough price found, check for sale badges/labels
        if not is_on_sale:
            sale_indicators = [
                soup.find(class_="badge-sale"),
                soup.find(class_="sale-badge"),
                soup.find(class_=lambda x: x and 'sale' in x),
                soup.find(class_=lambda x: x and 'akce' in x)
            ]
            
            for sale_element in sale_indicators:
                if sale_element:
                    sale_text = sale_element.get_text(strip=True).lower()
                    # Check if text contains sale indicators
                    if any(word in sale_text for word in ['sale', 'sleva', 'akce', 'discount', 'akční']):
                        is_on_sale = True
                        break
        
        logger.info(f"Successfully fetched product: {name}")
        return {
            "name": name,
            "price": price,
            "is_on_sale": is_on_sale,
            "original_price": original_price
        }
    
    async def _fetch_smarty_product_details(self, soup: BeautifulSoup) -> dict:
        """
        Extract product details from Smarty.cz product page.
        
        Args:
            soup: BeautifulSoup parsed page
            
        Returns:
            dict: Dictionary with 'name', 'price', 'is_on_sale', and 'original_price' keys
        """
        # Extract product name
        name_element = soup.find("h1")
        if not name_element:
            raise ValueError(
                "The Smarty.cz product page did not load correctly. "
                "Please verify the URL and try again."
            )
        name = name_element.get_text(strip=True)
        
        # Initialize sale status
        is_on_sale = False
        original_price = None
        
        # Extract price - try multiple selectors for Smarty
        price = None
        price_selectors = [
            {"class_": "price-final"},
            {"class_": "price-current"},
            {"class_": "product-price"},
            {"class_": lambda x: x and 'price' in x}
        ]
        
        for selector in price_selectors:
            price_element = soup.find(attrs=selector)
            if price_element:
                price_text = price_element.get_text(strip=True)
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
            soup.find(class_="price-old"),
            soup.find(class_="price-original"),
            soup.find(class_=lambda x: x and 'old-price' in x),
            soup.find("del"),
            soup.find("s")
        ]
        
        for old_price_element in strikethrough_selectors:
            if old_price_element:
                old_price_text = old_price_element.get_text(strip=True)
                original_price = self._extract_price_from_text(old_price_text)
                if original_price:
                    is_on_sale = True
                    break
        
        # Check for sale badges
        if not is_on_sale:
            sale_indicators = [
                soup.find(class_="badge-sale"),
                soup.find(class_="label-sale"),
                soup.find(class_=lambda x: x and 'sale' in x),
                soup.find(class_=lambda x: x and 'sleva' in x)
            ]
            
            for sale_element in sale_indicators:
                if sale_element:
                    sale_text = sale_element.get_text(strip=True).lower()
                    if any(word in sale_text for word in ['sale', 'sleva', 'akce', 'discount', 'akční']):
                        is_on_sale = True
                        break
        
        logger.info(f"Successfully fetched product: {name}")
        return {
            "name": name,
            "price": price,
            "is_on_sale": is_on_sale,
            "original_price": original_price
        }
    
    async def _fetch_allegro_product_details(self, soup: BeautifulSoup) -> dict:
        """
        Extract product details from Allegro.pl product page.
        
        Args:
            soup: BeautifulSoup parsed page
            
        Returns:
            dict: Dictionary with 'name', 'price', 'is_on_sale', and 'original_price' keys
        """
        # Extract product name
        name_element = soup.find("h1")
        if not name_element:
            raise ValueError(
                "The Allegro.pl product page did not load correctly. "
                "Please verify the URL and try again."
            )
        name = name_element.get_text(strip=True)
        
        # Initialize sale status
        is_on_sale = False
        original_price = None
        
        # Extract price - Allegro uses specific selectors
        price = None
        price_selectors = [
            {"attrs": {"data-role": "price"}},
            {"class_": lambda x: x and 'price' in x},
            {"name": "meta", "property": "product:price:amount"}
        ]
        
        for selector in price_selectors:
            if "name" in selector:
                price_element = soup.find(**selector)
                if price_element and price_element.get("content"):
                    price = self._extract_price_from_text(price_element.get("content"))
                    if price:
                        break
            else:
                price_element = soup.find(**selector)
                if price_element:
                    price_text = price_element.get_text(strip=True)
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
            soup.find(attrs={"data-role": "old-price"}),
            soup.find(class_="price-old"),
            soup.find(class_=lambda x: x and 'old-price' in x),
            soup.find("del"),
            soup.find("s")
        ]
        
        for old_price_element in strikethrough_selectors:
            if old_price_element:
                old_price_text = old_price_element.get_text(strip=True)
                original_price = self._extract_price_from_text(old_price_text)
                if original_price:
                    is_on_sale = True
                    break
        
        # Check for sale badges
        if not is_on_sale:
            sale_indicators = [
                soup.find(class_=lambda x: x and 'badge' in x),
                soup.find(class_=lambda x: x and 'promocja' in x),
                soup.find(class_=lambda x: x and 'sale' in x)
            ]
            
            for sale_element in sale_indicators:
                if sale_element:
                    sale_text = sale_element.get_text(strip=True).lower()
                    if any(word in sale_text for word in ['sale', 'promocja', 'obniżka', 'discount']):
                        is_on_sale = True
                        break
        
        logger.info(f"Successfully fetched product: {name}")
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
            site: E-commerce site name (e.g., 'alza', 'smarty', 'allegro')
            query: Search query
            limit: Maximum number of results to return (default: 10)
            
        Returns:
            list[SearchResultItem]: List of search results
            
        Raises:
            ValueError: If site is not supported
        """
        logger.info(f"Searching {site} for '{query}' (limit: {limit})")
        if not self.client:
            await self.initialize()
        
        site_lower = site.lower()
        
        if site_lower not in ["alza", "smarty", "allegro"]:
            raise ValueError(
                f"Unsupported site: {site}. "
                f"Supported sites: alza, smarty, allegro"
            )
        
        try:
            if site_lower == "alza":
                return await self._search_alza(query, limit)
            elif site_lower == "smarty":
                return await self._search_smarty(query, limit)
            elif site_lower == "allegro":
                return await self._search_allegro(query, limit)
        except Exception as e:
            # If mock mode is enabled, return mock data instead of failing
            if settings.scraper_mock_mode:
                logger.info(f"Using mock data for query '{query}': {e}")
                return self._get_mock_search_results(query, limit)
            raise
    
    async def _search_alza(self, query: str, limit: int = 10) -> list[SearchResultItem]:
        """
        Search Alza.cz for products.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            list[SearchResultItem]: Search results
        """
        try:
            # Build search URL
            search_url = f"https://www.alza.cz/search.htm?extext={query.replace(' ', '+')}"
            response = await self.client.get(search_url)
            response.raise_for_status()
        except httpx.ConnectError:
            raise ValueError(
                "Cannot connect to Alza.cz. "
                "Please check your internet connection and try again."
            )
        except httpx.TimeoutException:
            raise ValueError(
                "Alza.cz is not responding. The site may be experiencing high traffic. "
                "Please try again in a few moments."
            )
        except httpx.HTTPStatusError as e:
            raise ValueError(f"Failed to access Alza.cz: HTTP {e.response.status_code}")
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Get all product boxes
        product_boxes = soup.find_all(class_=['box browsingitem', 'browsingitem'])
        if not product_boxes:
            # Try alternative selector
            product_boxes = soup.find_all('div', class_=lambda x: x and 'browsingitem' in x)
        
        results = []
        for box in product_boxes[:limit]:
            try:
                # Extract product name
                name_element = box.find('a', class_='name') or box.find(class_='name').find('a') if box.find(class_='name') else None
                if not name_element:
                    continue
                name = name_element.get_text(strip=True)
                
                # Extract product URL
                product_url = name_element.get('href')
                if product_url and not product_url.startswith('http'):
                    product_url = f"https://www.alza.cz{product_url}"
                
                # Extract price
                price_element = box.find(class_='price-box__price') or box.find(class_='price')
                if not price_element:
                    continue
                price_text = price_element.get_text(strip=True)
                
                # Parse price using helper method
                price = self._extract_price_from_text(price_text)
                if not price:
                    continue
                
                # Extract image URL
                image_url = None
                img_element = box.find('img')
                if img_element:
                    image_url = img_element.get('src') or img_element.get('data-src')
                
                # Check for sale status
                is_on_sale = False
                original_price = None
                
                # Look for old/strikethrough price
                old_price_element = box.find(class_='price-box__old-price') or box.find(class_='old-price') or box.find('del') or box.find('s')
                if old_price_element:
                    old_price_text = old_price_element.get_text(strip=True)
                    original_price = self._extract_price_from_text(old_price_text)
                    if original_price:
                        is_on_sale = True
                
                # If no strikethrough price, check for sale badge
                if not is_on_sale:
                    sale_badge = box.find(class_=lambda x: x and ('sale' in x or 'akce' in x))
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
                logger.debug(f"Error processing product box: {e}")
                continue
        
        logger.info(f"Found {len(results)} results for '{query}'")
        return results
    
    async def _search_smarty(self, query: str, limit: int = 10) -> list[SearchResultItem]:
        """
        Search Smarty.cz for products.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            list[SearchResultItem]: Search results
        """
        try:
            search_url = f"https://www.smarty.cz/search.html?q={query.replace(' ', '+')}"
            response = await self.client.get(search_url)
            response.raise_for_status()
        except httpx.ConnectError:
            raise ValueError(
                "Cannot connect to Smarty.cz. "
                "Please check your internet connection and try again."
            )
        except httpx.TimeoutException:
            raise ValueError(
                "Smarty.cz is not responding. Please try again in a few moments."
            )
        except httpx.HTTPStatusError as e:
            raise ValueError(f"Failed to access Smarty.cz: HTTP {e.response.status_code}")
        
        soup = BeautifulSoup(response.text, 'lxml')
        product_boxes = soup.find_all(class_=lambda x: x and ('product-item' in x or 'product' in x))
        
        results = []
        for box in product_boxes[:limit]:
            try:
                name_element = box.find('a', class_=lambda x: x and 'name' in x) or box.find(class_='product-name') or box.find(['h3', 'h2']).find('a') if box.find(['h3', 'h2']) else None
                if not name_element:
                    continue
                name = name_element.get_text(strip=True)
                
                product_url = name_element.get('href')
                if product_url and not product_url.startswith('http'):
                    product_url = f"https://www.smarty.cz{product_url}"
                
                price_element = box.find(class_=lambda x: x and 'price' in x)
                if not price_element:
                    continue
                price = self._extract_price_from_text(price_element.get_text(strip=True))
                if not price:
                    continue
                
                image_url = None
                img_element = box.find('img')
                if img_element:
                    image_url = img_element.get('src') or img_element.get('data-src')
                
                is_on_sale = False
                original_price = None
                old_price_element = box.find(class_=lambda x: x and ('old' in x or 'original' in x)) or box.find('del') or box.find('s')
                if old_price_element:
                    original_price = self._extract_price_from_text(old_price_element.get_text(strip=True))
                    if original_price:
                        is_on_sale = True
                
                if not is_on_sale:
                    sale_badge = box.find(class_=lambda x: x and 'sale' in x)
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
                logger.debug(f"Error processing product box: {e}")
                continue
        
        logger.info(f"Found {len(results)} results for '{query}'")
        return results
    
    async def _search_allegro(self, query: str, limit: int = 10) -> list[SearchResultItem]:
        """
        Search Allegro.pl for products.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            list[SearchResultItem]: Search results
        """
        try:
            search_url = f"https://allegro.pl/listing?string={query.replace(' ', '+')}"
            response = await self.client.get(search_url)
            response.raise_for_status()
        except httpx.ConnectError:
            raise ValueError(
                "Cannot connect to Allegro.pl. "
                "Please check your internet connection and try again."
            )
        except httpx.TimeoutException:
            raise ValueError(
                "Allegro.pl is not responding. Please try again in a few moments."
            )
        except httpx.HTTPStatusError as e:
            raise ValueError(f"Failed to access Allegro.pl: HTTP {e.response.status_code}")
        
        soup = BeautifulSoup(response.text, 'lxml')
        product_boxes = soup.find_all(['article', 'div'], attrs={"data-role": "offer"})
        if not product_boxes:
            product_boxes = soup.find_all(class_=lambda x: x and 'offer' in x)
        
        results = []
        for box in product_boxes[:limit]:
            try:
                name_element = box.find('a', class_=lambda x: x and 'name' in x) or box.find(['h2', 'h3']).find('a') if box.find(['h2', 'h3']) else None
                if not name_element:
                    continue
                name = name_element.get_text(strip=True)
                
                product_url = name_element.get('href')
                if product_url and not product_url.startswith('http'):
                    product_url = f"https://allegro.pl{product_url}"
                
                price_element = box.find(attrs={"data-role": "price"}) or box.find(class_=lambda x: x and 'price' in x)
                if not price_element:
                    continue
                price = self._extract_price_from_text(price_element.get_text(strip=True))
                if not price:
                    continue
                
                image_url = None
                img_element = box.find('img')
                if img_element:
                    image_url = img_element.get('src') or img_element.get('data-src')
                
                is_on_sale = False
                original_price = None
                old_price_element = box.find(attrs={"data-role": "old-price"}) or box.find(class_='price-old') or box.find('del')
                if old_price_element:
                    original_price = self._extract_price_from_text(old_price_element.get_text(strip=True))
                    if original_price:
                        is_on_sale = True
                
                if not is_on_sale:
                    sale_badge = box.find(class_=lambda x: x and ('badge' in x or 'promocja' in x))
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
                logger.debug(f"Error processing product box: {e}")
                continue
        
        logger.info(f"Found {len(results)} results for '{query}'")
        return results
    
    
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
