# Multi-Site Scraping Architecture

This document describes the enhanced multi-site scraping architecture that supports multiple e-commerce platforms.

## Overview

The scraper has been redesigned with a modular architecture inspired by best practices from successful open-source web scraping projects. Each e-commerce site has its own handler class that implements site-specific logic for product extraction.

## Supported Sites

### Currently Supported

| Site | Country | URL Pattern | Features |
|------|---------|-------------|----------|
| **Alza.cz** | Czech Republic | `alza.cz` | Product search, price tracking, sale detection |
| **Smarty.cz** | Czech Republic | `smarty.cz` | Product search, price tracking, sale detection |
| **Allegro.pl** | Poland | `allegro.pl` | Product search, price tracking, sale detection |

### How It Works

The scraper automatically detects the e-commerce site from the URL and uses the appropriate handler:

```python
# Automatic site detection
from scraper.site_handlers import get_site_handler

handler = get_site_handler(product_url, page)
if handler:
    product_details = await handler.extract_product_details()
```

## Architecture

### Base Handler Class

All site handlers inherit from `BaseSiteHandler` which provides:

- Standard interface for product extraction
- Shared utility methods (price extraction, etc.)
- Consistent error handling

```python
class BaseSiteHandler(ABC):
    def __init__(self, page: Page):
        self.page = page
    
    @abstractmethod
    async def extract_product_details(self) -> Dict[str, Any]:
        """Extract product name, price, sale status"""
        pass
    
    @abstractmethod
    async def search_products(self, query: str, limit: int = 10) -> list:
        """Search for products on the site"""
        pass
```

### Site-Specific Handlers

Each site has a dedicated handler that implements:

1. **Product Detail Extraction**
   - Product name
   - Current price
   - Original price (if on sale)
   - Sale status

2. **Product Search**
   - Search by query
   - Extract search results with images
   - Detect sale items in results

3. **Robust Selectors**
   - Multiple fallback CSS selectors
   - Handles different page layouts
   - Graceful degradation

## Price Extraction

### Enhanced Price Parser

The price extraction logic handles multiple formats:

```python
# Supported formats:
"1 234,56 Kč"  -> 1234.56  # Czech format with space thousands separator
"1234.56 CZK"  -> 1234.56  # Standard format
"99,99 zł"     -> 99.99    # Polish złoty with comma decimal
"123.45 PLN"   -> 123.45   # Polish standard
```

### Features

- Handles both comma and dot as decimal separators
- Removes currency symbols automatically
- Supports multiple currencies (Kč, CZK, zł, PLN)
- Extracts first valid price found in text

## Sale Detection

### Multi-Strategy Approach

The scraper uses multiple strategies to detect sales:

1. **Original Price Detection**
   ```python
   # Looks for strikethrough/crossed-out prices
   selectors = [
       ".price-old",
       ".price-original", 
       "[class*='old-price']",
       "del", "s"  # HTML strikethrough tags
   ]
   ```

2. **Sale Badge Detection**
   ```python
   # Looks for sale indicator badges
   selectors = [
       ".badge-sale",
       ".label-sale",
       "[class*='sale']",
       "[class*='discount']"
   ]
   ```

3. **Multilingual Support**
   - Czech: "sleva", "akce", "akční"
   - Polish: "promocja", "obniżka"
   - English: "sale", "discount"

## Adding New Sites

To add support for a new e-commerce site:

### 1. Create a New Handler Class

```python
class NewSiteHandler(BaseSiteHandler):
    """Handler for newsite.com"""
    
    async def extract_product_details(self) -> Dict[str, Any]:
        # Wait for page load
        await self.page.wait_for_selector("h1", timeout=10000)
        
        # Extract name
        name_element = await self.page.query_selector("h1")
        name = await name_element.inner_text() if name_element else "Unknown"
        
        # Extract price (try multiple selectors)
        price = None
        for selector in [".price", "[class*='price']"]:
            price_elem = await self.page.query_selector(selector)
            if price_elem:
                price_text = await price_elem.inner_text()
                price = self._extract_price_from_text(price_text)
                if price:
                    break
        
        # Check for sale
        is_on_sale = False
        original_price = None
        old_price_elem = await self.page.query_selector(".old-price")
        if old_price_elem:
            old_price_text = await old_price_elem.inner_text()
            original_price = self._extract_price_from_text(old_price_text)
            if original_price:
                is_on_sale = True
        
        return {
            "name": name,
            "price": price,
            "is_on_sale": is_on_sale,
            "original_price": original_price
        }
    
    async def search_products(self, query: str, limit: int = 10) -> list:
        # Navigate to search page
        await self.page.goto("https://www.newsite.com/")
        
        # Perform search
        search_input = await self.page.wait_for_selector('input[type="search"]')
        await search_input.fill(query)
        await search_input.press("Enter")
        
        # Wait for results
        await self.page.wait_for_selector('.product-item')
        
        # Extract results
        results = []
        products = await self.page.query_selector_all('.product-item')
        
        for product in products[:limit]:
            # Extract product details...
            results.append(SearchResultItem(...))
        
        return results
```

### 2. Register in get_site_handler()

```python
def get_site_handler(url: str, page: Page) -> Optional[BaseSiteHandler]:
    url_lower = url.lower()
    
    if "alza.cz" in url_lower:
        return AlzaHandler(page)
    elif "smarty.cz" in url_lower:
        return SmartyHandler(page)
    elif "allegro.pl" in url_lower:
        return AllegroHandler(page)
    elif "newsite.com" in url_lower:  # Add new handler
        return NewSiteHandler(page)
    
    return None
```

### 3. Update Frontend

Add the new site to the dropdown in `frontend/index.html`:

```html
<select id="search-site" class="form-input" required>
    <option value="alza">Alza.cz (Czech)</option>
    <option value="smarty">Smarty.cz (Czech)</option>
    <option value="allegro">Allegro.pl (Poland)</option>
    <option value="newsite">NewSite.com</option>
</select>
```

### 4. Add Tests

Create tests in `tests/test_site_handlers.py`:

```python
@pytest.mark.asyncio
class TestNewSiteHandler:
    async def test_extract_product_details_success(self):
        mock_page = AsyncMock()
        # ... setup mocks ...
        
        handler = NewSiteHandler(mock_page)
        result = await handler.extract_product_details()
        
        assert result["name"] == "Expected Name"
        assert result["price"] == 99.99
```

## Best Practices

### Selector Strategy

1. **Primary Selectors**: Use specific class names when possible
   ```python
   ".price-box__price"
   ```

2. **Fallback Selectors**: Use broader patterns
   ```python
   "[class*='price']"
   ```

3. **Generic Selectors**: Last resort
   ```python
   ".price"
   ```

### Error Handling

Always provide user-friendly error messages:

```python
if price is None:
    raise ValueError(
        "Unable to find the product price on this page. "
        "The page layout may have changed or the product might not be available. "
        "Please check the product URL and try again."
    )
```

### Testing

Test multiple scenarios:
- ✅ Successful extraction
- ✅ Products on sale
- ✅ Missing prices
- ✅ Timeout errors
- ✅ Sale badge detection

## Troubleshooting

### Common Issues

1. **Price Not Found**
   - Check if the site updated their HTML structure
   - Add new selector to the fallback list
   - Verify currency symbol handling

2. **Sale Not Detected**
   - Check for new sale badge classes
   - Add new keywords to sale detection
   - Verify original price selector

3. **Timeout Errors**
   - Increase timeout in `core/config.py`
   - Check if site requires login
   - Verify internet connectivity

### Debugging

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Run with mock mode disabled to see real errors:

```bash
SCRAPER_MOCK_MODE=false pytest tests/test_scraper.py -v
```

## Performance

### Optimization Tips

1. **Reuse Browser Instances**
   - The scraper service maintains a single browser instance
   - Pages are created/closed for each request

2. **Timeout Configuration**
   - Default: 30 seconds (`SCRAPER_TIMEOUT`)
   - Adjust based on site response time

3. **Parallel Processing**
   - Multiple products can be scraped concurrently
   - Background scheduler handles periodic updates

## Security

### Anti-Bot Detection

- Use reasonable delays between requests
- Rotate user agents if needed
- Respect robots.txt
- Implement rate limiting

### Data Privacy

- Never store user credentials
- Only collect publicly available product data
- Comply with site terms of service

## Future Enhancements

Potential improvements:
- [ ] Add support for Amazon, eBay
- [ ] Implement request caching
- [ ] Add proxy rotation
- [ ] Browser fingerprint randomization
- [ ] GraphQL API support
- [ ] Dynamic selector learning
- [ ] Automated selector updates

## References

- [Playwright Documentation](https://playwright.dev/python/)
- [Crinibus/scraper](https://github.com/Crinibus/scraper) - Architecture inspiration
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/)
