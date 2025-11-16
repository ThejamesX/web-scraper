# PriceScout API

A robust, scalable FastAPI backend service for e-commerce product search and price tracking. Built with modern async Python tools including FastAPI, Playwright, and SQLAlchemy.

## Features

- **Product Search**: Search e-commerce sites (currently supports Alza.cz) for products and get top 10 results
- **Price Tracking**: Track product URLs and monitor price changes over time
- **Sale Detection**: Automatically detect when products are on sale and track original prices
- **Price Alerts**: Set custom price alerts and get notified when prices drop below your target
- **Historical Sale Tracking**: Track when products were on sale, not just current status
- **Background Jobs**: Automated price checks using APScheduler
- **Async Architecture**: Built with async/await for high performance
- **Comprehensive Testing**: Unit tests, integration tests, and API tests
- **Auto-Generated API Documentation**: Interactive OpenAPI/Swagger docs at `/docs`

## Technology Stack

- **FastAPI**: High-performance async web framework
- **Playwright**: Browser automation for web scraping
- **SQLAlchemy**: Async ORM for database operations
- **PostgreSQL/SQLite**: Production/development databases
- **Pydantic**: Data validation and settings management
- **Pytest**: Testing framework with async support
- **APScheduler**: Background task scheduling

## Project Structure

```
web-scraper/
├── core/               # Configuration and settings
│   ├── __init__.py
│   └── config.py
├── db/                 # Database models and session management
│   ├── __init__.py
│   ├── models.py       # Product and PriceHistory models
│   └── session.py      # Async database sessions
├── scraper/            # Web scraping service
│   ├── __init__.py
│   └── service.py      # Playwright-based scraper
├── api/                # API endpoints and schemas
│   ├── __init__.py
│   ├── schemas.py      # Pydantic models
│   └── endpoints/      # API route handlers
│       ├── __init__.py
│       ├── search.py   # Search endpoint
│       └── track.py    # Tracking endpoints
├── scheduler/          # Background jobs
│   ├── __init__.py
│   └── jobs.py         # Price check job
├── tests/              # Test suite
│   ├── __init__.py
│   ├── conftest.py     # Pytest fixtures
│   ├── test_api.py     # API endpoint tests
│   ├── test_logic.py   # Business logic tests
│   └── test_scraper.py # Integration tests
├── main.py             # FastAPI application entry point
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment variables
└── README.md           # This file
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd web-scraper
```

### 2. Create Virtual Environment

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
```

### 4. Install Playwright Browsers

```bash
playwright install chromium
```

### 5. Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` file with your settings:

```env
# For development (SQLite)
DATABASE_URL=sqlite+aiosqlite:///./pricescout.db

# For production (PostgreSQL)
# DATABASE_URL=postgresql+asyncpg://user:password@localhost/pricescout

# API Configuration
API_TITLE=PriceScout API
API_VERSION=1.0.0
API_DESCRIPTION=E-commerce product search and price tracking API

# Scheduler - check prices every 4 hours
PRICE_CHECK_INTERVAL_HOURS=4

# Scraper Configuration
SCRAPER_TIMEOUT=30000
SCRAPER_HEADLESS=true
```

## Running the Application

### Development Server

Start the development server with auto-reload:

```bash
uvicorn main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Interactive API Docs: http://localhost:8000/docs
- ReDoc Documentation: http://localhost:8000/redoc

### Production Server

For production, use multiple workers:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Usage

### 1. Search for Products

Search Alza.cz for products:

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "site": "alza",
    "query": "Samsung Galaxy S23"
  }'
```

Response:
```json
{
  "query": "Samsung Galaxy S23",
  "site": "alza",
  "results": [
    {
      "name": "Samsung Galaxy S23 256GB",
      "price": 22990.00,
      "product_url": "https://www.alza.cz/samsung-galaxy-s23-...",
      "image_url": "https://cdn.alza.cz/...",
      "is_on_sale": true,
      "original_price": 25990.00
    }
  ]
}
```

### 2. Track a Product

Start tracking a product URL:

```bash
curl -X POST "http://localhost:8000/track" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.alza.cz/samsung-galaxy-s23-d7654321.htm"
  }'
```

Response:
```json
{
  "id": 1,
  "url": "https://www.alza.cz/samsung-galaxy-s23-d7654321.htm",
  "name": "Samsung Galaxy S23 256GB",
  "eshop": "alza",
  "last_known_price": 22990.00,
  "last_check_time": "2024-01-15T10:30:00",
  "is_tracked": true,
  "is_on_sale": true,
  "original_price": 25990.00,
  "alert_price": null,
  "alert_triggered": false
}
```

### 3. Set Price Alert

Set a price alert to be notified when the price drops:

```bash
curl -X PUT "http://localhost:8000/track/1/alert" \
  -H "Content-Type: application/json" \
  -d '{
    "target_price": 20000.00
  }'
```

Response:
```json
{
  "status": "success",
  "item": {
    "id": 1,
    "alert_price": 20000.00,
    "alert_triggered": false,
    ...
  }
}
```

### 4. Get All Tracked Products

List all products you're tracking:

```bash
curl -X GET "http://localhost:8000/track"
```

Response: Array of product objects with all fields including sale status and alert information.

### 5. Get Price History

Retrieve price history for a tracked product:

```bash
curl -X GET "http://localhost:8000/track/product/1/history"
```

Response:
```json
[
  {
    "price": 22990.00,
    "timestamp": "2024-01-15T10:30:00",
    "is_on_sale": true,
    "original_price": 25990.00
  },
  {
    "price": 24990.00,
    "timestamp": "2024-01-14T06:00:00",
    "is_on_sale": false,
    "original_price": null
  }
]
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Types

```bash
# Unit tests only (fast)
pytest tests/test_api.py tests/test_logic.py

# Integration tests only (slow, requires internet)
pytest tests/test_scraper.py -m slow

# Exclude slow tests
pytest -m "not slow"
```

### Run with Coverage

```bash
pytest --cov=. --cov-report=html
```

### Test Structure

- **`test_api.py`**: Tests API endpoints with mocked dependencies (database and scraper)
- **`test_logic.py`**: Tests business logic in isolation (scheduler jobs)
- **`test_scraper.py`**: Integration tests against live websites (marked with `@pytest.mark.slow`)

## Background Jobs

The application automatically runs a background job to check prices for all tracked products every 4 hours (configurable via `PRICE_CHECK_INTERVAL_HOURS`).

The job:
1. Fetches all products where `is_tracked=True`
2. Scrapes current price and sale status for each product
3. Updates sale information (`is_on_sale`, `original_price`)
4. Compares with `last_known_price`
5. If changed, creates a new `PriceHistory` entry with sale information
6. Updates `last_known_price` and `last_check_time`
7. Checks if price alert should be triggered:
   - If `alert_price` is set and current price <= `alert_price`
   - Sets `alert_triggered` to `true` (only triggers once per alert)

**Alert Behavior:**
- Alerts trigger automatically when the price drops to or below the target
- Once triggered, the alert won't re-trigger until it's cleared and set again
- Frontend should monitor `alert_triggered` to notify users

## Development

### Code Quality

The codebase follows these principles:
- **Type hints**: All functions use proper type annotations
- **Async/await**: Consistent async patterns throughout
- **Dependency injection**: FastAPI's dependency system for testability
- **Separation of concerns**: Clear separation between API, business logic, and data layers

### Adding Support for New E-commerce Sites

To add support for a new site:

1. Add scraping logic in `scraper/service.py`:
   - Implement `_fetch_<sitename>_product_details()`
   - Implement `_search_<sitename>()`
   
2. Update `fetch_product_details()` and `search_site()` to handle the new site

3. Add tests in `tests/test_scraper.py`

### Database Migrations

For production use with schema changes, consider adding Alembic:

```bash
pip install alembic
alembic init alembic
# Configure and create migrations
```

## API Documentation

The API automatically generates comprehensive documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

All Pydantic schemas include:
- Field descriptions
- Type information
- Example values
- Validation rules

This makes the API self-documenting and ready for frontend integration.

## Troubleshooting

### Playwright Installation Issues

If Playwright fails to install browsers:

```bash
# Install system dependencies (Linux)
playwright install-deps chromium

# Then install browser
playwright install chromium
```

### Database Connection Issues

- **SQLite**: Ensure the application has write permissions in the directory
- **PostgreSQL**: Verify connection string and database exists

### Scraping Errors

If scraping fails:
1. Check if the website structure has changed
2. Verify internet connectivity
3. Check `SCRAPER_TIMEOUT` setting
4. Try running with `SCRAPER_HEADLESS=false` to see browser

## License

[Your License Here]

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request