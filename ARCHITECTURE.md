# PriceScout Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Client Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   Web UI     │  │  Mobile App  │  │  Browser     │              │
│  │  (Vanilla JS)│  │   (Future)   │  │  Extension   │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                  │                  │                       │
│         └──────────────────┴──────────────────┘                       │
│                            │                                          │
│                            │ HTTPS/REST API                           │
└────────────────────────────┼──────────────────────────────────────────┘
                             │
┌────────────────────────────┼──────────────────────────────────────────┐
│                  Application Layer (FastAPI)                          │
│                            │                                          │
│  ┌─────────────────────────▼──────────────────────────┐              │
│  │              API Gateway (main.py)                  │              │
│  │  • CORS Middleware                                  │              │
│  │  • Request Validation                               │              │
│  │  • Response Serialization                           │              │
│  └─────┬────────────────────────────────────────┬──────┘              │
│        │                                        │                     │
│  ┌─────▼────────┐                      ┌────────▼──────┐             │
│  │   Search     │                      │   Tracking    │             │
│  │   Endpoint   │                      │   Endpoints   │             │
│  │              │                      │  • Track      │             │
│  │ /search      │                      │  • Get All    │             │
│  └─────┬────────┘                      │  • Get One    │             │
│        │                               │  • Set Alert  │             │
│        │                               │  • History    │             │
│        │                               └────────┬──────┘             │
│        │                                        │                     │
│  ┌─────▼────────────────────────────────────────▼──────┐             │
│  │            Business Logic Layer                     │             │
│  │  • Product Management                               │             │
│  │  • Price Tracking Logic                             │             │
│  │  • Alert System                                     │             │
│  └─────┬────────────────────────────────────────┬──────┘             │
│        │                                        │                     │
└────────┼────────────────────────────────────────┼──────────────────────┘
         │                                        │
         │                                        │
┌────────▼────────┐                      ┌────────▼──────────────────────┐
│  Scraper Layer  │                      │   Data Layer (SQLAlchemy)     │
│                 │                      │                               │
│  ┌───────────┐  │                      │  ┌──────────┐  ┌──────────┐  │
│  │ Playwright│  │                      │  │ Product  │  │  Price   │  │
│  │  Browser  │  │                      │  │  Model   │  │ History  │  │
│  └─────┬─────┘  │                      │  └────┬─────┘  └────┬─────┘  │
│        │        │                      │       │             │        │
│  ┌─────▼─────┐  │                      │  ┌────▼─────────────▼─────┐  │
│  │  Alza.cz  │  │                      │  │    Database Session     │  │
│  │  Scraper  │  │                      │  │   (Async SQLAlchemy)    │  │
│  └───────────┘  │                      │  └─────────┬───────────────┘  │
│                 │                      │            │                  │
└─────────────────┘                      └────────────┼───────────────────┘
                                                      │
                                         ┌────────────▼───────────────┐
                                         │   PostgreSQL / SQLite      │
                                         │                            │
                                         │  Tables:                   │
                                         │   • products               │
                                         │   • price_history          │
                                         └────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                    Background Jobs (APScheduler)                      │
│                                                                       │
│  ┌──────────────────────────────────────────────────────┐            │
│  │  check_all_product_prices()                          │            │
│  │  • Runs every N hours (configurable)                 │            │
│  │  • Fetches current prices for tracked products       │            │
│  │  • Updates price history                             │            │
│  │  • Triggers price alerts                             │            │
│  └──────────────────────────────────────────────────────┘            │
└──────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Client Layer

**Web UI (Frontend)**
- Pure vanilla JavaScript (no framework dependencies)
- Chart.js for price history visualization
- LocalStorage for category management
- Responsive design for all devices

**Future Extensions**
- Mobile app (React Native / Flutter)
- Browser extension for quick tracking

### 2. Application Layer

**FastAPI Framework**
- Async request handling
- Automatic API documentation (OpenAPI/Swagger)
- Pydantic for request/response validation
- CORS middleware for cross-origin requests

**API Endpoints**

Search Endpoint (`/search`):
```
POST /search
Input: { site: "alza", query: "laptop" }
Output: List of search results with prices
```

Tracking Endpoints (`/track`):
```
POST /track          # Start tracking a product
GET /track           # Get all tracked products
GET /track/{id}      # Get specific product
PUT /track/{id}/alert # Set price alert
GET /track/product/{id}/history # Get price history
```

### 3. Scraper Layer

**Playwright Integration**
- Headless browser automation
- JavaScript rendering support
- Screenshot capability for debugging
- Supports Chromium browser

**Site-Specific Scrapers**
- Alza.cz scraper (currently implemented)
- Extensible architecture for adding new sites
- Sale detection (strikethrough prices, badges)
- Image extraction

**Scraping Process**
1. Navigate to product/search page
2. Wait for content to load
3. Extract data using CSS selectors
4. Parse prices and detect sales
5. Return structured data

### 4. Data Layer

**Models**

Product Model:
- Stores product information
- Tracks current sale status
- Manages price alerts
- References price history

Price History Model:
- Historical price snapshots
- Sale indicators
- Timestamp for each entry

**Database Features**
- Async database operations
- Connection pooling
- Indexed columns for performance
- Composite indexes for common queries

### 5. Background Jobs

**Price Check Job**
- Scheduled execution (default: every 4 hours)
- Fetches prices for all tracked products
- Creates price history entries on changes
- Triggers alerts when conditions met
- Error handling for individual failures

## Data Flow Diagrams

### Product Tracking Flow

```
User Action: Track Product
         │
         ▼
┌─────────────────────┐
│  POST /track        │
│  { url: "..." }     │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Validate Request   │
│  Check if exists    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Scrape Product     │
│  (Playwright)       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Extract:           │
│  • Name             │
│  • Price            │
│  • Sale Status      │
│  • Image            │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Save to Database   │
│  • Product record   │
│  • Initial price    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Return Product     │
│  to User            │
└─────────────────────┘
```

### Price Check Flow (Background Job)

```
Scheduled Time
         │
         ▼
┌─────────────────────┐
│  Get All Tracked    │
│  Products           │
└─────────┬───────────┘
          │
          ▼
     ┌────────┐
     │  Loop  │
     └────┬───┘
          │
          ▼
┌─────────────────────┐
│  Fetch Current      │
│  Price (Scraper)    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Compare with       │
│  Last Known Price   │
└─────────┬───────────┘
          │
     ┌────┴────┐
     │ Changed?│
     └────┬────┘
    Yes   │    No
     │    │     │
     ▼    │     ▼
┌─────────┐   ┌──────────┐
│Create   │   │Update    │
│History  │   │Check Time│
│Entry    │   └──────────┘
└─────┬───┘
      │
      ▼
┌─────────────────────┐
│  Update Product     │
│  last_known_price   │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Check Alert        │
│  Conditions         │
└─────────┬───────────┘
          │
     ┌────┴────┐
     │Trigger? │
     └────┬────┘
    Yes   │    No
     │    │     │
     ▼    │     ▼
┌─────────┐   │
│Set      │   │
│Alert    │   │
│Triggered│   │
└─────┬───┘   │
      │       │
      └───┬───┘
          │
          ▼
     Continue Loop
```

### Search Flow

```
User Action: Search
         │
         ▼
┌─────────────────────┐
│  POST /search       │
│  { site, query }    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Validate Input     │
│  • Site supported?  │
│  • Query not empty? │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Navigate to        │
│  Search Page        │
│  (Playwright)       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Enter Search Query │
│  Wait for Results   │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Extract Results    │
│  (up to 10)         │
│  • Name             │
│  • Price            │
│  • URL              │
│  • Image            │
│  • Sale status      │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Return Results     │
│  to User            │
└─────────────────────┘
```

## Technology Stack

### Backend
- **Python 3.12+** - Primary language
- **FastAPI** - Web framework
- **Playwright** - Browser automation
- **SQLAlchemy** - ORM with async support
- **Pydantic** - Data validation
- **APScheduler** - Background jobs
- **PostgreSQL/SQLite** - Database

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **Chart.js** - Price history charts
- **CSS Custom Properties** - Design tokens
- **LocalStorage** - Client-side data

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Reverse proxy (production)
- **PostgreSQL** - Production database

## Database Schema

### Products Table
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    url VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    eshop VARCHAR NOT NULL,
    last_known_price FLOAT,
    last_check_time TIMESTAMP,
    is_tracked BOOLEAN DEFAULT true,
    is_on_sale BOOLEAN DEFAULT false,
    original_price FLOAT,
    alert_price FLOAT,
    alert_triggered BOOLEAN DEFAULT false
);

-- Indexes for performance
CREATE INDEX ix_products_is_tracked ON products(is_tracked);
CREATE INDEX ix_products_is_on_sale ON products(is_on_sale);
CREATE INDEX ix_products_alert_triggered ON products(alert_triggered);
CREATE INDEX ix_products_eshop ON products(eshop);
CREATE INDEX ix_products_last_check_time ON products(last_check_time);
CREATE INDEX ix_products_tracked_sale ON products(is_tracked, is_on_sale);
CREATE INDEX ix_products_tracked_alert ON products(is_tracked, alert_triggered);
```

### Price History Table
```sql
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    price FLOAT NOT NULL,
    timestamp TIMESTAMP,
    is_on_sale BOOLEAN DEFAULT false,
    original_price FLOAT
);

CREATE INDEX ix_price_history_product_id ON price_history(product_id);
CREATE INDEX ix_price_history_timestamp ON price_history(timestamp);
```

## Security Considerations

1. **Input Validation** - Pydantic schemas validate all inputs
2. **SQL Injection** - SQLAlchemy ORM prevents SQL injection
3. **CORS** - Configurable allowed origins
4. **Rate Limiting** - Future enhancement
5. **HTTPS** - Required in production
6. **Non-root Container** - Docker runs as non-root user

## Performance Optimizations

1. **Database Indexes** - On frequently queried columns
2. **Async Operations** - All I/O is async
3. **Connection Pooling** - Configured for PostgreSQL
4. **Browser Reuse** - Playwright browser instance reused
5. **Caching** - Future enhancement with Redis

## Scalability

### Horizontal Scaling
- Stateless application design
- Multiple worker processes
- Load balancer compatible

### Database Scaling
- Read replicas for read-heavy loads
- Connection pooling with pgBouncer
- Indexed queries for performance

### Scraping Optimization
- Distributed task queue (future: Celery)
- Rate limiting per site
- Proxy rotation capability

## Monitoring and Observability

### Logging
- Structured logging with proper levels
- Request/response logging
- Error tracking with stack traces

### Health Checks
- `/health` endpoint for monitoring
- Scheduler status included
- Database connectivity check (implicit)

### Metrics (Future)
- Prometheus integration
- Grafana dashboards
- Request latency tracking
- Scraping success rates

## Development Workflow

1. **Local Development**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **Testing**
   ```bash
   pytest -v
   pytest --cov=. --cov-report=html
   ```

3. **Docker Development**
   ```bash
   docker-compose up -d
   docker-compose logs -f web
   ```

4. **Production Deployment**
   - See DEPLOYMENT.md for detailed guide

## Future Enhancements

See FUTURE_WORK.md for comprehensive roadmap including:
- Multi-site support
- User authentication
- Email notifications
- Browser extension
- Advanced analytics
- Caching layer
- Mobile app

## Contributing

See main README.md for contribution guidelines.
