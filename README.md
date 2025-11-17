# PriceScout - Smart Price Tracking Platform

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-60%20passed-brightgreen.svg)](tests/)

A complete e-commerce price tracking solution with a modern web UI and robust FastAPI backend. Track prices across multiple e-commerce sites (supports Alza.cz, Smarty.cz, and Allegro.pl), get notified when prices drop, and organize products into categories.

## 📚 Documentation

### Backend Documentation
- **[Architecture](ARCHITECTURE.md)** - System design and technical architecture
- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment instructions
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the project
- **[Future Roadmap](FUTURE_WORK.md)** - Planned features and enhancements

### Frontend Documentation
- **[Frontend README](frontend/README.md)** - Web UI documentation and development guide
- **[Design System](DESIGN_SYSTEM.md)** - Complete visual design and UX blueprint
- **[Integration Guide](FRONTEND_INTEGRATION_GUIDE.md)** - API integration documentation
- **[Component Examples](COMPONENT_EXAMPLES.md)** - Ready-to-use component code
- **[Quick Start Guide](FRONTEND_QUICK_START.md)** - Get started quickly with frontend

## ⚡ Quick Start

### Prerequisites
- Python 3.8+
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Option 1: Using Helper Script (Recommended)

```bash
git clone <repository-url>
cd web-scraper
./scripts/dev.sh setup    # Set up environment
./scripts/dev.sh start    # Start development server
```

### Option 2: Using Docker

```bash
git clone <repository-url>
cd web-scraper
docker-compose up -d
# Access at http://localhost:8000
```

### Option 3: Manual Setup

```bash
git clone <repository-url>
cd web-scraper
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
uvicorn main:app --reload
```

### Access the Application

- **Web UI**: http://localhost:8000/
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Demo & Testing

The application includes comprehensive test coverage including a soundbar search test that verifies end-to-end functionality:

![Soundbar Search Results](https://github.com/user-attachments/assets/c3e03453-26c0-4bf9-bd56-99e03929c802)

*Screenshot showing the soundbar search feature working correctly with mock data, displaying multiple products with pricing, sale indicators, and tracking capabilities.*

## 🌟 Features

### Frontend (Web UI)
- **Modern Dashboard**: View all tracked products with real-time filtering (All, On Sale, Triggered Alerts)
- **Product Search**: Search e-commerce sites and track products with one click
- **Price History Charts**: Interactive visualizations showing price trends and sale periods
- **Category Management**: Organize products into custom categories (e.g., "Soundbars", "Laptops")
- **Price Alerts**: Set target prices and get visual notifications when reached
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Statistics Dashboard**: View lowest/highest prices, price changes, and sale frequency

### Backend (API)
- **Product Search**: Search e-commerce sites (Alza.cz, Smarty.cz, Allegro.pl) for products
- **Price Tracking**: Track product URLs and monitor price changes over time
- **Sale Detection**: Automatically detect when products are on sale and track original prices
- **Price Alerts**: Set custom price alerts and get notified when prices drop
- **Historical Tracking**: Complete price history with sale indicators
- **Background Jobs**: Automated price checks using APScheduler
- **RESTful API**: Well-documented API endpoints with OpenAPI/Swagger docs

## 🎨 Design System

The frontend follows a comprehensive design system:
- **Clean, Modern UI**: Professional design with focus on clarity
- **Consistent Styling**: Design tokens for colors, spacing, and typography
- **Accessibility**: WCAG 2.1 Level AA compliant
- **Visual Hierarchy**: Clear indication of sales, alerts, and price changes

## 📱 Using the Web UI

### Dashboard
1. View all tracked products with statistics
2. Filter by "All", "On Sale", or "Triggered Alerts"
3. Click on any product to see detailed information

### Search for Products
1. Navigate to the "Search" tab
2. Select the e-commerce site (Alza.cz, Smarty.cz, or Allegro.pl)
3. Enter your search query (e.g., "soundbar", "laptop")
4. Click "Track" on products you want to monitor

### Product Details
1. Click on any product card
2. View interactive price history chart
3. See statistics (lowest/highest prices, sale frequency)
4. Set price alerts for notifications

### Categories
1. Navigate to "Categories" tab
2. Create custom categories (e.g., "Electronics", "Soundbars")
3. Assign products to categories for organization
4. Filter products by category

### Price Alerts
1. Go to any product detail page
2. Enter your target price
3. Click "Set Alert"
4. Get visual notification when price reaches your target

## 🏗️ Project Structure

```
web-scraper/
├── frontend/           # Web UI (HTML/CSS/JavaScript)
│   ├── index.html     # Main application page
│   ├── css/
│   │   ├── main.css   # Layout and general styles
│   │   └── components.css  # Component-specific styles
│   ├── js/
│   │   ├── api.js     # Backend API client
│   │   ├── app.js     # Main application logic
│   │   ├── categories.js  # Category management
│   │   └── utils.js   # Utility functions
│   └── README.md      # Frontend documentation
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
├── design-tokens.css   # Design system tokens
├── DESIGN_SYSTEM.md    # Complete design specification
├── FRONTEND_INTEGRATION_GUIDE.md  # API integration guide
├── COMPONENT_EXAMPLES.md  # Component code examples
├── main.py             # FastAPI application entry point
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment variables
└── README.md           # This file
```

## 🛠️ Technology Stack

### Frontend
- **Vanilla JavaScript** - No framework dependencies for easy migration
- **Chart.js** - Interactive price history charts
- **CSS Custom Properties** - Design tokens for consistent styling
- **LocalStorage** - Client-side category management

### Backend
- **FastAPI** - High-performance async web framework
- **Playwright** - Browser automation for web scraping
- **SQLAlchemy** - Async ORM for database operations
- **PostgreSQL/SQLite** - Production/development databases
- **Pydantic** - Data validation and settings management
- **APScheduler** - Background task scheduling

## 🎯 Recent Improvements

### Code Quality & Optimization (Latest)
- **Enhanced Error Messages**: All error messages now provide clear, actionable guidance
- **Code Refactoring**: Reduced code duplication with reusable helper methods for price extraction
- **Input Validation**: Added comprehensive validation with min/max length constraints
- **Better Error Handling**: Graceful error handling with user-friendly messages throughout
- **Test Coverage**: Comprehensive test suite including soundbar search verification

### Completed Features
- ✅ Complete product search and tracking functionality
- ✅ Price history visualization with sale indicators
- ✅ Price alert system with automatic monitoring
- ✅ Category management for product organization
- ✅ Responsive design for all devices
- ✅ Mock mode for testing without internet access
- ✅ Comprehensive API documentation
- ✅ End-to-end test coverage

## API Usage Examples

The backend provides a RESTful API. Here are some common operations:

### Search for Products

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "site": "alza",
    "query": "Samsung Galaxy S23"
  }'
```

### Track a Product

```bash
curl -X POST "http://localhost:8000/track" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.alza.cz/samsung-galaxy-s23-d7654321.htm"
  }'
```

### Set Price Alert

```bash
curl -X PUT "http://localhost:8000/track/1/alert" \
  -H "Content-Type: application/json" \
  -d '{
    "target_price": 20000.00
  }'
```

### Get All Tracked Products

```bash
curl -X GET "http://localhost:8000/track"
```

### Get Price History

```bash
curl -X GET "http://localhost:8000/track/product/1/history"
```

For complete API documentation with request/response schemas, visit http://localhost:8000/docs when the server is running.

## Key Features Explained

### Price Tracking
The system automatically checks prices for all tracked products every 4 hours (configurable). When a price changes:
1. A new price history entry is created
2. Sale status is detected and recorded
3. Price alerts are checked and triggered if conditions are met

### Sale Detection
The scraper automatically detects when products are on sale by:
- Looking for strikethrough/crossed-out original prices
- Detecting sale badges and discount indicators
- Recording both current and original prices

### Category Organization
Categories are stored locally in your browser using LocalStorage:
- Create unlimited custom categories
- Assign products to multiple categories
- Filter and view products by category
- Categories persist across browser sessions

### Price Alerts
Set target prices for any tracked product:
- Enter your desired price threshold
- System checks prices automatically
- Visual notification when price reaches or drops below target
- Alert triggers once until cleared and reset

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test types
pytest tests/test_api.py  # API tests only
pytest tests/test_soundbar_search.py  # Soundbar search tests
pytest tests/test_scraper.py -m slow  # Integration tests

# Run with coverage
pytest --cov=. --cov-report=html
```

### Code Quality

The codebase follows these principles:
- **Type hints**: All functions use proper type annotations
- **Async/await**: Consistent async patterns throughout
- **Separation of concerns**: Clear separation between API, business logic, and data layers
- **Design system**: Comprehensive design tokens for UI consistency
- **Error handling**: User-friendly error messages with actionable guidance
- **Code optimization**: Reusable helper methods reduce code duplication

### Adding Support for New E-commerce Sites

To add support for a new site:

1. Add scraping logic in `scraper/service.py`:
   ```python
   async def _fetch_<sitename>_product_details(self, page: Page) -> dict:
       # Implement scraping logic
       pass
   
   async def _search_<sitename>(self, query: str, limit: int = 10):
       # Implement search logic
       pass
   ```

2. Update `fetch_product_details()` and `search_site()` to handle the new site

3. Add tests in `tests/test_scraper.py`

## Production Deployment

### Database Migration

For production, use PostgreSQL:

1. Update `.env`:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost/pricescout
   ```

2. Install Alembic for migrations:
   ```bash
   pip install alembic
   alembic init alembic
   ```

### Server Configuration

For production, use multiple workers:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Environment Variables

Production environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SCRAPER_HEADLESS`: Set to `true` for production
- `SCRAPER_MOCK_MODE`: Set to `false` for production (use `true` for testing/demo without internet)
- `PRICE_CHECK_INTERVAL_HOURS`: Adjust based on your needs (default: 4)

## Troubleshooting

### Frontend Not Loading
- Ensure you're accessing http://localhost:8000/ (not http://127.0.0.1:8000/)
- Check that the `frontend/` directory exists and contains `index.html`
- Clear browser cache and reload

### Products Not Loading in Dashboard
- Open browser console (F12) to check for errors
- Verify backend is running and accessible
- Check CORS settings in `main.py`

### Search Not Working
- Ensure Playwright browsers are installed: `playwright install chromium`
- Check internet connectivity
- Verify the e-commerce site is accessible
- Try with `SCRAPER_HEADLESS=false` to debug
- **For testing without internet access**: Set `SCRAPER_MOCK_MODE=true` in your `.env` file to use mock data

### Price Updates Not Happening
- Check that the scheduler is running (you should see "Scheduler started" in logs)
- Adjust `PRICE_CHECK_INTERVAL_HOURS` if needed
- Check database for price history entries

## Browser Compatibility

The frontend works on all modern browsers:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Opera (latest)

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Future Enhancements

Potential features to add:
- [ ] Support for more e-commerce sites (Amazon, eBay, etc.)
- [ ] Email/push notifications for price alerts
- [ ] User authentication and multi-user support
- [ ] Export data to CSV/Excel
- [ ] Price comparison across multiple sites
- [ ] Historical price trend analysis
- [ ] Wishlist sharing functionality
- [ ] Browser extension for quick tracking

## Currently Supported E-commerce Sites

✅ **Alza.cz** - Czech electronics and gadgets retailer  
✅ **Smarty.cz** - Czech electronics and appliances store  
✅ **Allegro.pl** - Polish marketplace (largest in Poland)

The scraper features:
- Multi-site support with site-specific handlers
- Robust price extraction with multiple fallback patterns
- Automatic sale detection and original price tracking
- Error handling with user-friendly messages
- Mock mode for testing without internet access

## License

[Your License Here]

## Support

For issues, questions, or contributions:
- Check the [Documentation](#documentation)
- Review the [Troubleshooting](#troubleshooting) section
- Open an issue on GitHub
- Refer to the API docs at http://localhost:8000/docs

---

**Built with ❤️ using FastAPI, Playwright, and modern web technologies.**