# Contributing to PriceScout

Thank you for your interest in contributing to PriceScout! This document provides guidelines and instructions for contributing.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Adding New E-commerce Sites](#adding-new-e-commerce-sites)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Getting Started

### Prerequisites
- Python 3.12 or higher
- Git
- Basic understanding of FastAPI, SQLAlchemy, and Playwright

### Finding Issues to Work On

1. Check the [Issues](https://github.com/YourRepo/web-scraper/issues) page
2. Look for issues labeled:
   - `good first issue` - Great for newcomers
   - `help wanted` - Issues where we need help
   - `enhancement` - New feature requests
   - `bug` - Bug reports

3. Comment on the issue you'd like to work on to avoid duplicate work

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/web-scraper.git
cd web-scraper
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Set Up Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 5. Run Tests

```bash
pytest
```

### 6. Start Development Server

```bash
uvicorn main:app --reload
```

## How to Contribute

### Reporting Bugs

When reporting bugs, include:
1. **Description** - Clear description of the bug
2. **Steps to Reproduce** - Numbered steps to reproduce
3. **Expected Behavior** - What should happen
4. **Actual Behavior** - What actually happens
5. **Environment** - OS, Python version, browser
6. **Screenshots** - If applicable
7. **Logs** - Relevant error messages

Example:
```markdown
**Description**
Product search returns no results for valid queries.

**Steps to Reproduce**
1. Navigate to /search
2. Enter "laptop" as query
3. Click Search

**Expected Behavior**
Should return list of laptops from Alza.cz

**Actual Behavior**
Returns empty results array

**Environment**
- OS: Ubuntu 22.04
- Python: 3.12.1
- Browser: Chrome 120

**Error Logs**
```
Error: Timeout waiting for selector 'div.product'
```
```

### Suggesting Features

Feature requests should include:
1. **Problem Statement** - What problem does this solve?
2. **Proposed Solution** - How should it work?
3. **Alternatives Considered** - Other solutions you've thought about
4. **Additional Context** - Mockups, examples, use cases

## Code Style Guidelines

### Python Code Style

We follow PEP 8 with these specific guidelines:

**1. Imports**
```python
# Standard library
import logging
from datetime import datetime

# Third-party
from fastapi import APIRouter, Depends
from sqlalchemy import select

# Local
from api.schemas import ProductOut
from db.models import Product
```

**2. Function Documentation**
```python
async def fetch_product_details(url: str) -> dict:
    """
    Fetch product details from a product page URL.
    
    Args:
        url: Product page URL
        
    Returns:
        dict: Dictionary with 'name', 'price', 'is_on_sale', and 'original_price' keys
        
    Raises:
        ValueError: If URL is invalid or unsupported
        PlaywrightError: If page loading fails
    """
    # Implementation
```

**3. Type Hints**
Always use type hints:
```python
def calculate_discount(original: float, current: float) -> float:
    return ((original - current) / original) * 100
```

**4. Constants**
```python
# Use uppercase for constants
MAX_SEARCH_RESULTS = 10
DEFAULT_TIMEOUT = 30000
SUPPORTED_SITES = ["alza", "mall", "smarty"]
```

**5. Error Handling**
```python
try:
    result = await scraper.fetch_product_details(url)
except ValueError as e:
    # User-facing errors
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    # Unexpected errors - log and provide generic message
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="An error occurred")
```

### JavaScript Code Style

**1. Use Modern JavaScript**
```javascript
// Use const/let, not var
const apiUrl = '/api/products';
let products = [];

// Use arrow functions
const fetchProducts = async () => {
    const response = await fetch(apiUrl);
    return await response.json();
};
```

**2. Async/Await**
```javascript
// Prefer async/await over .then()
async function loadProduct(id) {
    try {
        const response = await fetch(`/track/${id}`);
        const product = await response.json();
        displayProduct(product);
    } catch (error) {
        console.error('Failed to load product:', error);
        showError('Failed to load product');
    }
}
```

### File Organization

```
web-scraper/
├── api/
│   ├── __init__.py
│   ├── schemas.py         # Pydantic schemas
│   └── endpoints/
│       ├── __init__.py
│       ├── search.py      # Search endpoint
│       └── track.py       # Tracking endpoints
├── core/
│   ├── __init__.py
│   └── config.py          # Configuration
├── db/
│   ├── __init__.py
│   ├── models.py          # Database models
│   └── session.py         # Database session
├── scraper/
│   ├── __init__.py
│   └── service.py         # Scraper implementation
├── scheduler/
│   ├── __init__.py
│   └── jobs.py            # Background jobs
└── tests/
    ├── conftest.py        # Pytest fixtures
    ├── test_api.py        # API tests
    └── test_scraper.py    # Scraper tests
```

## Testing Guidelines

### Writing Tests

**1. Unit Tests**
Test individual functions in isolation:
```python
@pytest.mark.asyncio
async def test_extract_price():
    """Test price extraction from text."""
    scraper = ScraperService()
    price = scraper._extract_price_from_text("Cena: 12 999,00 Kč")
    assert price == 12999.00
```

**2. Integration Tests**
Test multiple components together:
```python
@pytest.mark.asyncio
async def test_track_product_endpoint(client, mock_db, mock_scraper):
    """Test product tracking endpoint."""
    response = await client.post("/track", json={"url": "https://alza.cz/test"})
    assert response.status_code == 201
    assert "id" in response.json()
```

**3. Test Naming**
- Use descriptive names: `test_search_returns_empty_for_invalid_query`
- Start with `test_`
- Describe what is being tested and expected outcome

**4. Test Organization**
```python
# Arrange - Set up test data
product = Product(name="Test", price=999.99)

# Act - Perform the action
result = await calculate_discount(product)

# Assert - Check the result
assert result == 10.0
```

**5. Markers**
Use pytest markers for test categorization:
```python
@pytest.mark.slow  # For tests that take time
@pytest.mark.integration  # For integration tests
@pytest.mark.asyncio  # For async tests
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::test_search_endpoint

# Run with coverage
pytest --cov=. --cov-report=html

# Run excluding slow tests
pytest -m "not slow"
```

## Commit Message Guidelines

Follow the Conventional Commits specification:

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(scraper): add support for Mall.cz

Implemented scraper for Mall.cz e-commerce site with:
- Product search functionality
- Price extraction
- Sale detection

Closes #123
```

```
fix(api): handle empty search results gracefully

Previously crashed when no results found.
Now returns empty array with proper status code.

Fixes #456
```

```
docs(readme): update installation instructions

Added steps for Windows users and troubleshooting section.
```

## Pull Request Process

### Before Submitting

1. **Update your fork**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run tests**
   ```bash
   pytest
   ```

3. **Check code style**
   ```bash
   # Future: Add linting tools
   # black .
   # flake8
   # mypy .
   ```

4. **Update documentation**
   - Update README.md if needed
   - Add docstrings to new functions
   - Update CHANGELOG.md

### Submitting Pull Request

1. **Create Pull Request**
   - Use a clear title
   - Fill out the PR template
   - Reference related issues

2. **PR Description Template**
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Changes Made
   - Added X feature
   - Fixed Y bug
   - Updated Z documentation

   ## Testing
   - [ ] All tests pass
   - [ ] Added new tests
   - [ ] Updated existing tests

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No new warnings
   
   ## Related Issues
   Closes #123
   ```

3. **Respond to Feedback**
   - Address review comments promptly
   - Make requested changes
   - Re-request review when ready

### After PR is Merged

1. **Delete your branch**
   ```bash
   git branch -d your-feature-branch
   git push origin --delete your-feature-branch
   ```

2. **Update your fork**
   ```bash
   git checkout main
   git pull upstream main
   git push origin main
   ```

## Adding New E-commerce Sites

To add support for a new e-commerce site:

### 1. Implement Scraper Methods

In `scraper/service.py`:

```python
async def _fetch_SITENAME_product_details(self, page: Page) -> dict:
    """
    Extract product details from SITENAME product page.
    
    Args:
        page: Playwright page object
        
    Returns:
        dict: Dictionary with 'name', 'price', 'is_on_sale', 'original_price' keys
    """
    # Wait for page to load
    await page.wait_for_selector("h1.product-title")
    
    # Extract name
    name_element = await page.query_selector("h1.product-title")
    name = await name_element.inner_text()
    
    # Extract price
    price_element = await page.query_selector("span.price")
    price_text = await price_element.inner_text()
    price = self._extract_price_from_text(price_text)
    
    # Check for sale
    is_on_sale = False
    original_price = None
    old_price_element = await page.query_selector("span.old-price")
    if old_price_element:
        old_price_text = await old_price_element.inner_text()
        original_price = self._extract_price_from_text(old_price_text)
        is_on_sale = True
    
    return {
        "name": name,
        "price": price,
        "is_on_sale": is_on_sale,
        "original_price": original_price
    }

async def _search_SITENAME(self, query: str, limit: int = 10):
    """
    Search for products on SITENAME.
    
    Args:
        query: Search query
        limit: Maximum number of results
        
    Returns:
        list: List of SearchResultItem dictionaries
    """
    # Implementation
    pass
```

### 2. Update Main Methods

Update `fetch_product_details()` and `search_site()` to handle the new site:

```python
async def fetch_product_details(self, url: str) -> dict:
    # ... existing code ...
    
    if "sitename.com" in url:
        result = await self._fetch_SITENAME_product_details(page)
        return result
    # ... existing sites ...
```

### 3. Add Tests

In `tests/test_scraper.py`:

```python
@pytest.mark.slow
@pytest.mark.asyncio
async def test_sitename_search():
    """Test SITENAME product search."""
    scraper = ScraperService()
    await scraper.initialize()
    
    try:
        results = await scraper.search_site("sitename", "test query")
        assert len(results) > 0
        assert all("name" in r and "price" in r for r in results)
    finally:
        await scraper.close()
```

### 4. Update Documentation

- Add to supported sites list in README.md
- Update API documentation
- Add examples

### 5. Submit PR

Create pull request with:
- Implementation
- Tests
- Documentation
- Example searches

## Questions?

If you have questions:
1. Check existing documentation
2. Search issues for similar questions
3. Open a new issue with the `question` label

## Recognition

Contributors will be added to the README.md contributors section.

Thank you for contributing to PriceScout! 🎉
