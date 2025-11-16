# PriceScout Frontend

A modern, responsive web UI for tracking product prices across e-commerce platforms.

## Screenshot

![Soundbar Search](https://github.com/user-attachments/assets/c3e03453-26c0-4bf9-bd56-99e03929c802)

*The search interface showing results for "soundbar" with multiple products, sale indicators, and tracking capabilities.*

## Features

- **Dashboard**: View all tracked products with filters (All, On Sale, Triggered Alerts)
- **Search**: Search for products on supported e-commerce sites (Alza.cz)
- **Product Details**: View price history, statistics, and set price alerts
- **Categories**: Organize products into custom categories
- **Price Alerts**: Get notified when products reach your target price
- **Price History Chart**: Visualize price changes over time with sale indicators

## Technology Stack

- **Vanilla JavaScript** - No framework dependencies for easy migration
- **Chart.js** - Interactive price history charts
- **CSS Custom Properties** - Design tokens for consistent styling
- **LocalStorage** - Client-side category management

## Quick Start

### 1. Start the Backend

Make sure the backend API is running:

```bash
cd /home/runner/work/web-scraper/web-scraper
uvicorn main:app --reload
```

### 2. Access the Frontend

Open your browser and navigate to:
- Frontend UI: http://localhost:8000/
- API Documentation: http://localhost:8000/docs

The frontend is automatically served by the FastAPI backend.

## Project Structure

```
frontend/
├── index.html              # Main HTML page
├── css/
│   ├── main.css           # Main styles and layout
│   └── components.css     # Component-specific styles
├── js/
│   ├── api.js            # API client for backend communication
│   ├── app.js            # Main application logic
│   ├── categories.js     # Category management
│   └── utils.js          # Utility functions
└── assets/               # Images and other static assets
```

## Key Features Explained

### Dashboard

The dashboard provides an overview of all tracked products with:
- Statistics cards showing total products, items on sale, and triggered alerts
- Filter tabs to view all products, only sales, or triggered alerts
- Product cards with visual indicators for sales and alerts

### Search

Search for products across supported e-commerce platforms:
1. Select the e-commerce site (currently Alza.cz)
2. Enter your search query (e.g., "laptop", "soundbar")
3. Browse results and click "Track" to start monitoring

### Product Details

Each product has a dedicated detail page showing:
- Current price and sale status
- Price history chart with visual sale indicators
- Key statistics (lowest, highest, initial price, times on sale)
- Alert management interface

### Categories

Organize products into custom categories:
1. Create categories (e.g., "Soundbars", "Laptops")
2. Assign products to one or more categories
3. View all products in a category
4. Categories are stored locally in the browser

### Price Alerts

Set up custom price alerts for any tracked product:
1. Go to the product detail page
2. Enter your target price
3. Click "Set Alert"
4. The system will automatically check prices and trigger alerts when reached

## Design System

The UI follows a comprehensive design system with:
- **Primary Color**: Blue (#3B82F6) for actions and emphasis
- **Sale Indicator**: Red (#EF4444) for discounts and price increases
- **Alert Colors**: Green (#10B981) for active alerts, Amber (#F59E0B) for triggered alerts
- **Typography**: Inter for body text, Manrope for headings
- **Responsive**: Mobile-first design with breakpoints for tablets and desktops

## Browser Compatibility

The frontend works on all modern browsers:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Development

### Customizing Styles

All design tokens are defined in `/design-tokens.css`. Modify these values to customize the appearance:

```css
:root {
  --color-primary: #3B82F6;
  --spacing-md: 16px;
  /* ... more tokens */
}
```

### Adding New Features

1. **API Integration**: Update `js/api.js` with new API endpoints
2. **UI Components**: Add component styles to `css/components.css`
3. **Logic**: Implement functionality in `js/app.js` or create new modules

### Converting to a Framework

The frontend is built with vanilla JavaScript to make it easy to convert to any framework:

**React**: Replace the HTML templates with JSX components
**Vue**: Convert to Vue components with the template syntax
**Svelte**: Transform into Svelte components

The design tokens and component structure remain the same across frameworks.

## API Integration

The frontend communicates with the backend via REST API:

```javascript
// Example API calls
await api.searchProducts('alza', 'laptop');
await api.getTrackedProducts();
await api.trackProduct(productUrl);
await api.setAlert(productId, targetPrice);
```

See `js/api.js` for all available API methods.

## Troubleshooting

### Products Not Loading

1. Check that the backend is running on port 8000
2. Open browser console for error messages
3. Verify API endpoints are accessible at http://localhost:8000/docs

### CORS Errors

The backend is configured to allow CORS for development. If you still see CORS errors:
1. Make sure you're accessing the frontend through http://localhost:8000
2. Check that the API_BASE_URL in `js/api.js` matches your backend URL

### Charts Not Displaying

1. Ensure Chart.js is loaded (check browser console)
2. Verify there is price history data for the product
3. Check browser console for JavaScript errors

## Future Enhancements

Potential features to add:
- Dark mode support
- User authentication and multi-user support
- Email/push notifications for price alerts
- Export data to CSV/Excel
- Price comparison across multiple sites
- Historical price predictions
- Wishlist sharing
- Advanced filtering options

See [FUTURE_WORK.md](../FUTURE_WORK.md) for a complete roadmap of planned enhancements.

## Recent Improvements

- ✅ Enhanced error messages with actionable guidance
- ✅ Improved input validation
- ✅ Optimized code structure with reduced duplication
- ✅ Comprehensive test coverage including soundbar search
- ✅ Better error handling throughout the application

## License

See the main repository LICENSE file.

## Support

For issues or questions:
- Check the backend API docs at http://localhost:8000/docs
- Review the design system documentation in `DESIGN_SYSTEM.md`
- See the integration guide in `FRONTEND_INTEGRATION_GUIDE.md`
