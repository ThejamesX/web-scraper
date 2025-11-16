# PriceScout Frontend Integration Guide

This guide provides all the information needed to implement the PriceScout frontend as described in the blueprint.

## API Base URL

Development: `http://localhost:8000`

## Enhanced API Endpoints

### 1. Search Products
**Endpoint:** `POST /search`

**Request:**
```json
{
  "site": "alza",
  "query": "laptop"
}
```

**Response:**
```json
{
  "query": "laptop",
  "site": "alza",
  "results": [
    {
      "name": "Product Name",
      "price": 12999.00,
      "product_url": "https://www.alza.cz/product-url",
      "image_url": "https://cdn.alza.cz/image.jpg",
      "is_on_sale": true,
      "original_price": 15999.00
    }
  ]
}
```

**New Fields:**
- `is_on_sale`: Boolean indicating if product is currently on sale
- `original_price`: Original price before discount (null if not on sale)

---

### 2. Get All Tracked Products
**Endpoint:** `GET /track`

**Response:**
```json
[
  {
    "id": 1,
    "url": "https://www.alza.cz/product",
    "name": "Product Name",
    "eshop": "alza",
    "last_known_price": 12999.00,
    "last_check_time": "2024-01-15T10:30:00Z",
    "is_tracked": true,
    "is_on_sale": true,
    "original_price": 15999.00,
    "alert_price": 10000.00,
    "alert_triggered": false
  }
]
```

**New Fields:**
- `is_on_sale`: Boolean - product is currently on sale
- `original_price`: Float or null - original price before discount
- `alert_price`: Float or null - user-defined target price for alert
- `alert_triggered`: Boolean - true when current price <= alert_price

**Use Cases:**
- Dashboard "All" tab: Display all items
- Dashboard "On Sale" tab: Filter where `is_on_sale === true`
- Dashboard "Triggered Alerts" tab: Filter where `alert_triggered === true`

---

### 3. Get Single Product Details
**Endpoint:** `GET /track/{product_id}`

**Response:**
```json
{
  "id": 1,
  "url": "https://www.alza.cz/product",
  "name": "Product Name",
  "eshop": "alza",
  "last_known_price": 12999.00,
  "last_check_time": "2024-01-15T10:30:00Z",
  "is_tracked": true,
  "is_on_sale": true,
  "original_price": 15999.00,
  "alert_price": 10000.00,
  "alert_triggered": false
}
```

**Use Case:** ProductDetail page header and current status

---

### 4. Get Product Price History
**Endpoint:** `GET /track/product/{product_id}/history`

**Response:**
```json
[
  {
    "price": 12999.00,
    "timestamp": "2024-01-15T10:30:00Z",
    "is_on_sale": true,
    "original_price": 15999.00
  },
  {
    "price": 15999.00,
    "timestamp": "2024-01-14T06:00:00Z",
    "is_on_sale": false,
    "original_price": null
  }
]
```

**New Fields:**
- `is_on_sale`: Boolean - whether item was on sale at this point in time
- `original_price`: Float or null - original price if on sale

**Use Case:** 
- PriceHistoryChart component
- Differentiate between price fluctuations and actual sales
- Calculate "Times on Sale" statistic

---

### 5. Track New Product
**Endpoint:** `POST /track`

**Request:**
```json
{
  "url": "https://www.alza.cz/product-url"
}
```

**Response:** Same as "Get Single Product Details" (status code 201)

---

### 6. Set Price Alert (NEW)
**Endpoint:** `PUT /track/{product_id}/alert`

**Request:**
```json
{
  "target_price": 10000.00
}
```

**Response:**
```json
{
  "status": "success",
  "item": {
    "id": 1,
    "alert_price": 10000.00,
    "alert_triggered": false,
    // ... all other product fields
  }
}
```

**Use Case:** AlertManager component - set or update price alert

---

### 7. Clear Price Alert (NEW)
**Endpoint:** `DELETE /track/{product_id}/alert`

**Response:**
```json
{
  "status": "success"
}
```

**Use Case:** AlertManager component - remove price alert

---

## Frontend Component Implementation Guide

### SearchResultsList Component
```typescript
interface SearchResult {
  name: string;
  price: number;
  product_url: string;
  image_url?: string;
  is_on_sale: boolean;
  original_price?: number;
}

// Display logic:
// - If is_on_sale is true, show "SALE" badge
// - Display original_price with strikethrough next to current price
// - Example: <del>15,999 Kč</del> 12,999 Kč
```

### TrackedItemsGrid Component
```typescript
interface TrackedItem {
  id: number;
  name: string;
  last_known_price: number;
  is_on_sale: boolean;
  original_price?: number;
  alert_price?: number;
  alert_triggered: boolean;
}

// Display logic for each card:
// 1. Sale Status:
//    - If is_on_sale: show "SALE" badge
//    - Display: <del>{original_price}</del> {last_known_price}
//
// 2. Alert Status:
//    - If alert_triggered: show bell icon and special border (green/gold)
//    - Display "Price Alert!" indicator
```

### AlertManager Component
```typescript
interface AlertManagerProps {
  productId: number;
  currentAlertPrice?: number;
  alertTriggered: boolean;
}

// Features to implement:
// 1. Display current alert_price if set
// 2. Input field + "Set Alert" button -> PUT /track/{id}/alert
// 3. "Clear Alert" button (show if alert_price exists) -> DELETE /track/{id}/alert
// 4. Show toast notification on success
// 5. If alert_triggered is true, show prominent "Alert Triggered!" message
```

### PriceHistoryChart Component
```typescript
interface PriceHistoryPoint {
  price: number;
  timestamp: string;
  is_on_sale: boolean;
  original_price?: number;
}

// Chart implementation with Recharts:
// 1. Primary Line: price over time
// 2. Horizontal Reference Line: alert_price (dashed)
// 3. Scatter Plot: Red dots where is_on_sale === true
// 4. Custom Tooltip showing:
//    - Date
//    - Price
//    - Status: "Regular Price" or "ON SALE"
```

### StatisticsKPIs Component
```typescript
// Calculate from product and price_history:
{
  "Current Price": product.last_known_price,
  "Lowest Recorded Price": product.lowest_price, // May need to calculate from history
  "Highest Recorded Price": Math.max(...price_history.map(h => h.price)),
  "Initial Tracked Price": price_history[price_history.length - 1].price,
  "Times on Sale": price_history.filter(h => h.is_on_sale).length
}
```

### Dashboard Tabs Implementation
```typescript
// Tab filters based on GET /track response:

// "All" Tab
const allItems = trackedItems;

// "On Sale" Tab
const onSaleItems = trackedItems.filter(item => item.is_on_sale);

// "Triggered Alerts" Tab
const triggeredAlerts = trackedItems.filter(item => item.alert_triggered);
```

## Sale vs. Fluctuation Differentiation

The key feature request is to distinguish between:
1. **Price Fluctuation**: Normal price changes (shown as line on chart)
2. **Explicit Sales**: Product marked as "on sale" by retailer (shown as red dots on chart)

This is tracked in two ways:
- **Real-time**: `product.is_on_sale` shows current status
- **Historical**: `price_history[].is_on_sale` shows when item was on sale in the past

## Background Price Checking

The backend automatically checks prices every 4 hours (configurable). When a price check occurs:
1. Current price is fetched
2. Sale status is detected
3. If price changed, new price_history entry is created
4. If `alert_price` is set and current price <= alert_price:
   - `alert_triggered` is set to true
   - Frontend should highlight this prominently

## Error Handling

Standard HTTP status codes:
- `200`: Success
- `201`: Created (POST /track)
- `400`: Bad request / validation error
- `404`: Product not found
- `422`: Validation error (missing required fields)
- `500`: Server error

## Development Notes

1. **API Documentation**: Full interactive docs at `http://localhost:8000/docs`
2. **Database**: SQLite in development, PostgreSQL recommended for production
3. **CORS**: May need to be configured for frontend development
4. **Polling**: Consider implementing periodic refresh (e.g., every 30s) on Dashboard to catch new price updates

## Example API Usage Flow

```typescript
// 1. Search for products
const searchResults = await fetch('/search', {
  method: 'POST',
  body: JSON.stringify({ site: 'alza', query: 'laptop' })
});

// 2. Track a product from search results
const tracked = await fetch('/track', {
  method: 'POST',
  body: JSON.stringify({ url: searchResults.results[0].product_url })
});

// 3. Set price alert
await fetch(`/track/${tracked.id}/alert`, {
  method: 'PUT',
  body: JSON.stringify({ target_price: 10000 })
});

// 4. Get all tracked products for dashboard
const allProducts = await fetch('/track');

// 5. Get product details with history
const product = await fetch(`/track/${productId}`);
const history = await fetch(`/track/product/${productId}/history`);
```

## Testing

The backend includes comprehensive tests for all new features. Frontend should test:
- Displaying sale badges correctly
- Price alert setting/clearing
- Alert triggered state highlighting
- Historical sale tracking on charts
- Filtering by sale status and alert status
