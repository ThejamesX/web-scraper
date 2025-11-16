# PriceScout Frontend Quick Start Guide

Welcome to the PriceScout frontend development guide! This document helps you get started quickly with implementing the PriceScout user interface.

## 📚 Documentation Overview

This repository contains comprehensive design and implementation documentation for the PriceScout frontend:

### 1. **DESIGN_SYSTEM.md** - The Complete Design Specification
- **Purpose:** Comprehensive visual design and UX blueprint
- **Contains:**
  - Complete color palette and design tokens
  - Typography system and font specifications
  - Layout system (spacing, borders, shadows)
  - Detailed component specifications for all UI elements
  - UX principles (feedback, responsiveness, empty states)
  - Accessibility guidelines (WCAG 2.1 AA compliance)
  - Animation guidelines
  - Responsive design patterns

**Start here** to understand the overall design philosophy and visual language.

### 2. **design-tokens.css** - Ready-to-Use CSS Variables
- **Purpose:** Production-ready CSS design tokens
- **Contains:**
  - All color variables
  - Typography variables
  - Spacing scale
  - Border radius values
  - Shadow definitions
  - Transition timing functions
  - Utility classes

**Import this file** at the root of your application to access all design tokens via CSS custom properties.

```css
/* In your root CSS file */
@import './design-tokens.css';

/* Use design tokens in your components */
.my-component {
  background: var(--color-bg-white);
  padding: var(--spacing-md);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-default);
}
```

### 3. **COMPONENT_EXAMPLES.md** - Implementation Code Examples
- **Purpose:** Complete implementation examples with code
- **Contains:**
  - React/TypeScript component examples
  - Complete CSS implementations
  - All major components:
    - ProductCard
    - StatusBadges
    - PriceHistoryChart (with Recharts)
    - StatisticsKPIs
    - AlertManager
    - Toast Notifications
    - Empty States
    - Skeleton Loaders

**Use these examples** as starting points for your component implementations.

### 4. **FRONTEND_INTEGRATION_GUIDE.md** - API Integration Guide
- **Purpose:** Backend API integration documentation
- **Contains:**
  - Complete API endpoint documentation
  - Request/response examples
  - Data models and interfaces
  - Display logic for components
  - API usage flow examples

**Reference this** when integrating with the backend API.

### 5. **README.md** - Backend Documentation
- **Purpose:** Backend API server documentation
- **Contains:**
  - Backend setup instructions
  - API features and endpoints
  - Database schema
  - Testing instructions

---

## 🚀 Quick Start Steps

### Step 1: Set Up Your Project

Choose your preferred frontend framework:

**React + TypeScript (Recommended)**
```bash
npx create-react-app pricescout-frontend --template typescript
cd pricescout-frontend
```

**Next.js + TypeScript**
```bash
npx create-next-app pricescout-frontend --typescript
cd pricescout-frontend
```

**Vite + React + TypeScript**
```bash
npm create vite@latest pricescout-frontend -- --template react-ts
cd pricescout-frontend
```

### Step 2: Install Required Dependencies

```bash
# Core dependencies
npm install axios recharts

# Icons (choose one)
npm install @tabler/icons-react
# OR
npm install react-feather

# Optional: Utility libraries
npm install date-fns classnames
```

### Step 3: Copy Design Tokens

1. Copy `design-tokens.css` to your project's `src/styles/` directory
2. Import it in your root CSS/index file:

```css
/* src/index.css or src/App.css */
@import './styles/design-tokens.css';

/* Apply base styles */
body {
  font-family: var(--font-family-body);
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  background: var(--color-bg-light);
  margin: 0;
  padding: 0;
}
```

### Step 4: Set Up API Client

Create an API client to communicate with the backend:

```typescript
// src/api/client.ts
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API functions
export const searchProducts = (site: string, query: string) => 
  apiClient.post('/search', { site, query });

export const getTrackedProducts = () => 
  apiClient.get('/track');

export const getProductDetails = (productId: number) => 
  apiClient.get(`/track/${productId}`);

export const getPriceHistory = (productId: number) => 
  apiClient.get(`/track/product/${productId}/history`);

export const trackProduct = (url: string) => 
  apiClient.post('/track', { url });

export const setAlert = (productId: number, targetPrice: number) => 
  apiClient.put(`/track/${productId}/alert`, { target_price: targetPrice });

export const clearAlert = (productId: number) => 
  apiClient.delete(`/track/${productId}/alert`);
```

### Step 5: Implement Components

Use the examples from `COMPONENT_EXAMPLES.md` as templates:

1. Create component directories in `src/components/`
2. Copy the React/TypeScript code for each component
3. Copy the corresponding CSS
4. Customize as needed for your implementation

Example structure:
```
src/
├── components/
│   ├── ProductCard/
│   │   ├── ProductCard.tsx
│   │   └── ProductCard.css
│   ├── StatusBadge/
│   │   ├── StatusBadge.tsx
│   │   └── StatusBadge.css
│   ├── PriceHistoryChart/
│   │   ├── PriceHistoryChart.tsx
│   │   └── PriceHistoryChart.css
│   └── ...
├── pages/
│   ├── Dashboard.tsx
│   ├── ProductDetail.tsx
│   └── Search.tsx
├── api/
│   └── client.ts
└── styles/
    └── design-tokens.css
```

### Step 6: Build Your Pages

**Dashboard Page**
- Displays grid of tracked products using ProductCard components
- Tabs for filtering: All, On Sale, Triggered Alerts
- Empty state when no products tracked

**Search Page**
- Search form
- Display search results
- "Track Product" buttons

**Product Detail Page**
- Product information header
- PriceHistoryChart component
- StatisticsKPIs grid
- AlertManager component

---

## 🎨 Design Token Reference

Quick reference for the most commonly used design tokens:

### Colors
```css
--color-primary: #3B82F6        /* Primary actions, links */
--color-accent-sale: #EF4444    /* Sale indicators */
--color-accent-alert: #10B981   /* Active alerts */
--color-text-primary: #1F2937   /* Main text */
--color-bg-white: #FFFFFF       /* Card backgrounds */
--color-bg-light: #F9FAFB       /* Page backgrounds */
```

### Spacing
```css
--spacing-sm: 8px               /* Small gaps */
--spacing-md: 16px              /* Medium gaps, card padding */
--spacing-lg: 24px              /* Large gaps, section spacing */
```

### Typography
```css
--font-family-headings: 'Manrope', 'Inter', sans-serif
--font-family-body: 'Inter', 'Roboto', sans-serif
--font-size-base: 16px
--font-size-lg: 1.125rem        /* Product titles */
--font-size-2xl: 1.5rem         /* Current prices */
```

---

## 📱 Responsive Breakpoints

```css
/* Mobile first - base styles for mobile */

@media (min-width: 640px) { /* sm - Large phones */ }
@media (min-width: 768px) { /* md - Tablets */ }
@media (min-width: 1024px) { /* lg - Small laptops */ }
@media (min-width: 1280px) { /* xl - Desktops */ }
```

---

## 🧪 Testing Your Implementation

### Visual Testing Checklist
- [ ] Colors match the design system
- [ ] Typography uses correct fonts and sizes
- [ ] Spacing is consistent using design tokens
- [ ] Components are responsive (mobile, tablet, desktop)
- [ ] Hover and focus states work correctly
- [ ] Loading states display properly
- [ ] Empty states show when appropriate

### Functionality Testing
- [ ] ProductCard displays sale status correctly
- [ ] StatusBadges show appropriate icons and colors
- [ ] PriceHistoryChart differentiates sales from regular prices
- [ ] AlertManager can set and clear alerts
- [ ] Toast notifications appear and dismiss
- [ ] Data loads from API correctly

### Accessibility Testing
- [ ] Keyboard navigation works
- [ ] Focus indicators are visible
- [ ] Screen reader can navigate the app
- [ ] Color contrast meets WCAG AA standards
- [ ] All images have alt text

---

## 🔗 External Resources

### Icon Libraries
- **Tabler Icons:** https://tabler-icons.io/
- **Feather Icons:** https://feathericons.com/

### Chart Libraries
- **Recharts:** https://recharts.org/
- **Chart.js:** https://www.chartjs.org/

### Fonts
- **Manrope:** https://fonts.google.com/specimen/Manrope
- **Inter:** https://fonts.google.com/specimen/Inter

### Accessibility
- **WCAG 2.1 Guidelines:** https://www.w3.org/WAI/WCAG21/quickref/

---

## 💡 Tips for Success

1. **Start with design tokens**: Import `design-tokens.css` first and use CSS variables throughout your app
2. **Component-first approach**: Build individual components before assembling pages
3. **Test responsiveness early**: Check mobile layouts as you build each component
4. **Follow the examples**: Use `COMPONENT_EXAMPLES.md` as a starting point, don't reinvent the wheel
5. **Stay consistent**: Always refer back to `DESIGN_SYSTEM.md` for design decisions
6. **Accessibility matters**: Include ARIA labels and keyboard support from the start

---

## 📞 Need Help?

- **Design Specification:** See `DESIGN_SYSTEM.md`
- **API Integration:** See `FRONTEND_INTEGRATION_GUIDE.md`
- **Code Examples:** See `COMPONENT_EXAMPLES.md`
- **Backend Setup:** See `README.md`

---

## 📝 License

See the main repository LICENSE file.

---

**Happy Coding! 🚀**

Build something amazing with PriceScout!
