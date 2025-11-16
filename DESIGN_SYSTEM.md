# PriceScout Design System & UX Blueprint

**Version:** 1.0.0  
**Project:** PriceScout - Visual Design & UX Blueprint  
**Last Updated:** 2025-11-16

## Table of Contents
1. [Overview](#overview)
2. [Design Philosophy](#design-philosophy)
3. [Design Tokens](#design-tokens)
4. [Typography](#typography)
5. [Layout System](#layout-system)
6. [Component Specifications](#component-specifications)
7. [UX Principles](#ux-principles)
8. [Responsive Design](#responsive-design)
9. [Implementation Guidelines](#implementation-guidelines)

---

## Overview

This document provides a comprehensive design brief and style guide for creating a modern, clean, and data-driven user interface for the PriceScout frontend. This guide focuses on visual hierarchy, user feedback, and clearly communicating price data, sales, and alerts.

### Project Information

**Theme:** Modern, Clean, Data-First

**Philosophy:** The UI must be intuitive, with a strong visual hierarchy. Price data, savings, and alerts are the most important information and must be presented with maximum clarity. The design should inspire trust and feel responsive.

---

## Design Philosophy

The PriceScout interface is built around three core principles:

1. **Clarity First**: Price information, sales, and alerts are the primary focus. All visual elements support clear communication of this data.

2. **Trust Through Design**: Clean, professional aesthetics with consistent spacing and typography inspire confidence in the price tracking data.

3. **Responsive Feedback**: Every user action receives immediate visual feedback through animations, toasts, and state changes.

---

## Design Tokens

### Color Palette

```css
/* Primary Colors */
--color-primary: #3B82F6;
--color-primary-dark: #2563EB;
--color-secondary: #6B7280;

/* Background Colors */
--color-bg-light: #F9FAFB;
--color-bg-white: #FFFFFF;

/* Text Colors */
--color-text-primary: #1F2937;
--color-text-secondary: #4B5563;

/* Border Colors */
--color-border-default: #E5E7EB;

/* Accent Colors - Sale */
--color-accent-sale: #EF4444;
--color-accent-sale-bg: #FEE2E2;

/* Accent Colors - Alert */
--color-accent-alert: #10B981;
--color-accent-alert-bg: #D1FAE5;

/* Accent Colors - Alert Triggered */
--color-accent-alert-triggered: #F59E0B;
--color-accent-alert-triggered-bg: #FEF3C7;
```

#### Color Usage Guidelines

| Color Token | Use Case | Example |
|-------------|----------|---------|
| `primary` | Primary buttons, links, main chart line | "Set Alert" button, price chart line |
| `primary-dark` | Hover states for primary elements | Button hover |
| `secondary` | Secondary text, subtle UI elements | Timestamps, metadata |
| `bg-light` | Page background, card backgrounds for KPIs | Dashboard background |
| `bg-white` | Card backgrounds, modal backgrounds | ProductCard background |
| `text-primary` | Primary headings, important text | Product names, prices |
| `text-secondary` | Supporting text, descriptions | "Last checked", labels |
| `accent-sale` | Sale indicators, price up indicators | "ON SALE" badge, price increase |
| `accent-alert` | Active alerts, price down indicators | "ALERT SET" badge, price decrease |
| `accent-alert-triggered` | Triggered alerts, notifications | "PRICE REACHED!" badge |

---

## Typography

### Font Families

```css
--font-family-headings: 'Manrope', 'Inter', sans-serif;
--font-family-body: 'Inter', 'Roboto', sans-serif;
```

### Font Sizes & Weights

```css
/* Base */
--font-size-base: 16px;

/* Headings */
--font-size-h1: 2.25rem;    /* 36px */
--font-weight-h1: 700;

--font-size-h2: 1.875rem;   /* 30px */
--font-weight-h2: 700;

--font-size-h3: 1.5rem;     /* 24px */
--font-weight-h3: 600;

/* Body */
--font-size-body: 1rem;     /* 16px */
--font-weight-body: 400;

/* Small */
--font-size-small: 0.875rem; /* 14px */
--font-weight-small: 400;

/* Price Display - Special */
--font-size-price: 1.5rem;   /* 24px */
--font-weight-price: 700;

--font-size-price-original: 1rem; /* 16px */
```

### Typography Scale

| Element | Font Family | Size | Weight | Use Case |
|---------|-------------|------|--------|----------|
| H1 | Manrope | 2.25rem | 700 | Page titles |
| H2 | Manrope | 1.875rem | 700 | Section headers |
| H3 | Manrope | 1.5rem | 600 | Subsection headers |
| Body | Inter | 1rem | 400 | General text |
| Small | Inter | 0.875rem | 400 | Captions, labels |
| Price (Current) | Manrope | 1.5rem | 700 | Current price display |
| Price (Original) | Inter | 1rem | 400 | Original price (strikethrough) |
| Product Title | Inter | 1.125rem | 600 | Product names on cards |

---

## Layout System

### Spacing

```css
--spacing-unit: 8px;

/* Common Spacing Values */
--spacing-xs: 4px;    /* 0.5 units */
--spacing-sm: 8px;    /* 1 unit */
--spacing-md: 16px;   /* 2 units */
--spacing-lg: 24px;   /* 3 units */
--spacing-xl: 32px;   /* 4 units */
--spacing-2xl: 48px;  /* 6 units */
```

### Border Radius

```css
--border-radius: 8px;
--border-radius-sm: 4px;
--border-radius-lg: 12px;
--border-radius-pill: 9999px;
```

### Shadows

```css
--shadow-default: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
```

### Container

```css
--container-max-width: 1440px;
--component-spacing: 16px;
```

---

## Component Specifications

### 1. ProductCard (Dashboard)

**Purpose:** The visual representation of a tracked item. Must be glanceable and communicate status at a glance.

#### Visual Specifications

```css
.product-card {
  background: var(--color-bg-white);
  border: 1px solid var(--color-border-default);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-default);
  border-left: 3px solid transparent; /* Status border */
  transition: all 0.2s ease-in-out;
}

.product-card:hover {
  box-shadow: var(--shadow-lg);
  transform: scale(1.02);
}

/* Status Border Variants */
.product-card--on-sale {
  border-left-color: var(--color-accent-sale);
}

.product-card--alert-triggered {
  border-left-color: var(--color-accent-alert-triggered);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}
```

#### Structure

```
┌─────────────────────────────────┐
│ [Status Border 3px]             │
│  ┌──────────────────────────┐   │
│  │      Product Image       │   │
│  │    (1:1 aspect ratio)    │   │
│  └──────────────────────────┘   │
│                                  │
│  Product Name (max 2 lines)     │
│  with truncation...              │
│                                  │
│  [Badge] [Badge]                 │
│                                  │
│  Kč 12,990  [Kč 15,990]         │
│  (current)  (original - strike)  │
│                                  │
│  Last checked: 2h ago            │
└─────────────────────────────────┘
```

#### Layout Details

- **Container padding:** 16px
- **Image:**
  - Aspect ratio: 1:1
  - `object-fit: contain`
  - Rounded top corners or padding within container
  - Background: `var(--color-bg-light)` for transparent images

- **Title:**
  - Font: `var(--font-family-body)`
  - Weight: 600
  - Size: 1.125rem (18px)
  - Max 2 lines with truncation (`text-overflow: ellipsis`)
  - Margin bottom: 12px

- **Price Display:**
  - **Current Price:**
    - Font: `var(--font-family-headings)`
    - Weight: 700
    - Size: 1.5rem (24px)
    - Color: `var(--color-text-primary)`
  
  - **Original Price (if on sale):**
    - Font: `var(--font-family-body)`
    - Size: 1rem (16px)
    - Color: `var(--color-text-secondary)`
    - Style: `text-decoration: line-through`
    - Display inline next to current price

- **Badge Area:**
  - Margin: 8px 0
  - Display: flex, gap 8px
  - Badges wrap to next line if needed

#### Interaction States

- **Default:** Base styles as above
- **Hover:** Increase shadow to `shadow-lg`, scale to 1.02
- **Focus:** Add focus ring with primary color
- **Active/Pressed:** Slight scale down (0.98)

---

### 2. StatusBadges (Pills)

**Purpose:** Small tags to quickly show item status.

#### Visual Specifications

```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border-radius: var(--border-radius-pill);
  font-size: var(--font-size-small);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}
```

#### Variants

**1. ON SALE Badge**
```css
.badge--on-sale {
  background: var(--color-accent-sale-bg);
  color: var(--color-accent-sale);
}
```
- Icon: `tag` (from icon set)
- Text: "ON SALE"

**2. ALERT SET Badge**
```css
.badge--alert-set {
  background: var(--color-accent-alert-bg);
  color: var(--color-accent-alert);
}
```
- Icon: `bell`
- Text: "ALERT SET"

**3. PRICE REACHED Badge**
```css
.badge--alert-triggered {
  background: var(--color-accent-alert-triggered-bg);
  color: var(--color-accent-alert-triggered);
  font-weight: 700;
}
```
- Icon: `bell-ringing`
- Text: "PRICE REACHED!"

#### Size Variants

```css
.badge--sm {
  padding: 2px 8px;
  font-size: 0.75rem;
}

.badge--md {
  padding: 4px 12px;
  font-size: 0.875rem;
}
```

---

### 3. PriceHistoryChart (ProductDetail)

**Purpose:** Visualizes price history, differentiating sales from fluctuations.

#### Chart Configuration

**Library Recommendation:** Recharts (React) or Chart.js

**Chart Type:** Line chart with scatter overlay

#### Visual Elements

**1. Main Price Line**
```javascript
{
  type: 'line',
  dataKey: 'price',
  stroke: 'var(--color-primary)',
  strokeWidth: 2,
  dot: false,
  activeDot: { r: 6 }
}
```

**2. Sale Points (Scatter Overlay)**
```javascript
{
  type: 'scatter',
  dataKey: 'price',
  data: priceHistory.filter(point => point.is_on_sale),
  fill: 'var(--color-accent-sale)',
  shape: 'circle',
  r: 6
}
```

**3. Alert Line (Horizontal Reference)**
```javascript
{
  type: 'referenceLine',
  y: alertPrice,
  stroke: 'var(--color-accent-alert-triggered)',
  strokeDasharray: '5 5',
  strokeWidth: 2,
  label: 'Alert Price'
}
```

**4. Custom Tooltip**
```css
.chart-tooltip {
  background: var(--color-text-primary);
  color: var(--color-bg-white);
  padding: 12px;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
}
```

Tooltip Content:
- **Date:** Format: "Jan 15, 2024, 10:30 AM"
- **Price:** Format: "Kč 12,990"
- **Status:** "Regular" or "On Sale" (styled with accent color)

#### Container Styles

```css
.price-chart {
  background: var(--color-bg-white);
  padding: var(--spacing-lg);
  border-radius: var(--border-radius);
  border: 1px solid var(--color-border-default);
  min-height: 400px;
}
```

#### Responsive Behavior

- **Desktop:** Chart height 400px
- **Tablet:** Chart height 350px
- **Mobile:** Chart height 300px, simplify tooltip

---

### 4. StatisticsKPIs (ProductDetail)

**Purpose:** A grid of key statistics for the product.

#### Layout Structure

```css
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-md);
}

@media (min-width: 768px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .kpi-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

#### KPI Card

```css
.kpi-card {
  background: var(--color-bg-light);
  padding: var(--spacing-md);
  border-radius: var(--border-radius);
  transition: transform 0.2s;
}

.kpi-card:hover {
  transform: translateY(-2px);
}

.kpi-card__label {
  font-size: var(--font-size-small);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  font-weight: 500;
  letter-spacing: 0.05em;
  margin-bottom: 8px;
}

.kpi-card__value {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--color-text-primary);
  font-family: var(--font-family-headings);
}
```

#### Standard KPIs

1. **Current Price**
   - Label: "CURRENT PRICE"
   - Value: Current price formatted with currency

2. **Lowest Price**
   - Label: "LOWEST RECORDED"
   - Value: Minimum price from history

3. **Highest Price**
   - Label: "HIGHEST RECORDED"
   - Value: Maximum price from history

4. **Initial Price**
   - Label: "INITIAL PRICE"
   - Value: First tracked price

5. **Times on Sale**
   - Label: "TIMES ON SALE"
   - Value: Count of sale occurrences

#### Special KPI: Price Change Delta

```css
.kpi-card--price-change {
  /* Base styles from .kpi-card */
}

.kpi-card__value--positive {
  color: var(--color-accent-sale);
  display: flex;
  align-items: center;
  gap: 8px;
}

.kpi-card__value--positive::before {
  content: '↑';
  font-size: 1.5rem;
}

.kpi-card__value--negative {
  color: var(--color-accent-alert);
  display: flex;
  align-items: center;
  gap: 8px;
}

.kpi-card__value--negative::before {
  content: '↓';
  font-size: 1.5rem;
}
```

**Price Change Logic:**
- Positive (price increase): Red color with ↑ arrow
- Negative (price decrease): Green color with ↓ arrow
- Display both absolute change and percentage

---

### 5. AlertManager (ProductDetail)

**Purpose:** The form/UI for setting a price alert.

#### Visual Specifications

```css
.alert-manager {
  background: var(--color-bg-white);
  border: 1px solid var(--color-border-default);
  border-radius: var(--border-radius);
  padding: var(--spacing-lg);
}

.alert-manager__title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: var(--spacing-md);
}

.alert-manager__current-alert {
  background: var(--color-accent-alert-bg);
  color: var(--color-accent-alert);
  padding: 12px;
  border-radius: var(--border-radius);
  margin-bottom: var(--spacing-md);
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.alert-manager__current-alert::before {
  content: '🔔';
  font-size: 1.25rem;
}
```

#### Form Elements

**Price Input**
```css
.alert-input {
  width: 100%;
  padding: 12px 16px;
  font-size: 1rem;
  border: 2px solid var(--color-border-default);
  border-radius: var(--border-radius);
  transition: border-color 0.2s;
}

.alert-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.alert-input-wrapper {
  position: relative;
}

.alert-input-prefix {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-secondary);
  font-weight: 500;
}

.alert-input--with-prefix {
  padding-left: 40px;
}
```

**Buttons**

```css
/* Primary Button - Set Alert */
.btn-primary {
  background: var(--color-primary);
  color: var(--color-bg-white);
  padding: 12px 24px;
  border: none;
  border-radius: var(--border-radius);
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background: var(--color-primary-dark);
}

.btn-primary:active {
  transform: scale(0.98);
}

/* Secondary/Destructive Button - Clear Alert */
.btn-secondary {
  background: transparent;
  color: var(--color-accent-sale);
  padding: 12px 24px;
  border: 2px solid var(--color-accent-sale);
  border-radius: var(--border-radius);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: var(--color-accent-sale-bg);
}

.btn-secondary:active {
  transform: scale(0.98);
}
```

#### Layout Structure

```
┌────────────────────────────────────┐
│  Price Alert                       │
│                                    │
│  ┌─────────────────────────────┐  │
│  │ 🔔 Alert active at: Kč 10,000│ │
│  └─────────────────────────────┘  │
│                                    │
│  Set new price alert:              │
│  ┌─────────────────────────────┐  │
│  │ Kč [input field]             │ │
│  └─────────────────────────────┘  │
│                                    │
│  [Set Alert] [Clear Alert]         │
└────────────────────────────────────┘
```

---

## Iconography

### Recommended Icon Libraries

- **Primary:** [Tabler Icons](https://tabler-icons.io/)
- **Alternative:** [Feather Icons](https://feathericons.com/)

### Icon Mapping

| Function | Icon Name | Tabler/Feather |
|----------|-----------|----------------|
| Alert | `bell` | `bell` |
| Alert Triggered | `bell-ringing` | `bell` (animated) |
| Sale | `tag` | `tag` |
| Delete | `trash` | `trash-2` |
| Track/Add | `plus` | `plus` |
| Search | `search` | `search` |
| Arrow Up | `arrow-up` | `arrow-up` |
| Arrow Down | `arrow-down` | `arrow-down` |
| External Link | `external-link` | `external-link` |
| Check | `check` | `check` |
| Close | `x` | `x` |

### Icon Sizes

```css
--icon-size-sm: 16px;
--icon-size-md: 20px;
--icon-size-lg: 24px;
--icon-size-xl: 32px;
```

---

## UX Principles

### User Feedback

#### Loading States

**Skeleton Components**
```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-bg-light) 0%,
    #E5E7EB 50%,
    var(--color-bg-light) 100%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--border-radius);
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
```

**Usage:**
- Use skeleton cards that mimic ProductCard layout while data loads
- Use spinners for button actions and chart loading
- Never show blank/empty spaces during loading

**Button Loading State**
```css
.btn-loading {
  position: relative;
  color: transparent;
  pointer-events: none;
}

.btn-loading::after {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  top: 50%;
  left: 50%;
  margin-left: -8px;
  margin-top: -8px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

#### Toast Notifications

**Success Toast**
```css
.toast--success {
  background: var(--color-accent-alert);
  color: white;
  padding: 16px 24px;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-xl);
  display: flex;
  align-items: center;
  gap: 12px;
}
```

**Error Toast**
```css
.toast--error {
  background: var(--color-accent-sale);
  color: white;
  padding: 16px 24px;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-xl);
  display: flex;
  align-items: center;
  gap: 12px;
}
```

**Toast Container**
- Position: Fixed, top-right
- Top: 24px, Right: 24px
- Stack vertically with 8px gap
- Auto-dismiss after 3-5 seconds
- Include close button

**Toast Messages:**
- "Alert Set" → Success
- "Item Tracked" → Success
- "Alert Cleared" → Success
- "Failed to load data" → Error
- "Failed to set alert" → Error

---

### Empty States

#### No Tracked Items (Dashboard)

```
┌──────────────────────────────────────┐
│                                      │
│            📦                        │
│                                      │
│    No Products Tracked Yet           │
│                                      │
│    Start tracking products to        │
│    monitor prices and get alerts     │
│                                      │
│       [Search Products]              │
│                                      │
└──────────────────────────────────────┘
```

**Implementation:**
```css
.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--color-text-secondary);
}

.empty-state__icon {
  font-size: 4rem;
  margin-bottom: var(--spacing-md);
  opacity: 0.5;
}

.empty-state__title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
}

.empty-state__description {
  font-size: 1rem;
  margin-bottom: var(--spacing-lg);
}
```

#### No Search Results

```
┌──────────────────────────────────────┐
│                                      │
│            🔍                        │
│                                      │
│    No Results Found                  │
│                                      │
│    Try adjusting your search terms   │
│                                      │
└──────────────────────────────────────┘
```

---

## Responsive Design

### Mobile-First Approach

Design and develop mobile layouts first, then progressively enhance for larger screens.

### Breakpoints

```css
/* Mobile First - Base styles are for mobile */
/* Styles apply to all screen sizes unless overridden */

/* Small tablets and large phones (landscape) */
@media (min-width: 640px) {
  /* sm */
}

/* Tablets */
@media (min-width: 768px) {
  /* md */
}

/* Small laptops */
@media (min-width: 1024px) {
  /* lg */
}

/* Desktops */
@media (min-width: 1280px) {
  /* xl */
}

/* Large desktops */
@media (min-width: 1536px) {
  /* 2xl */
}
```

### Component Responsive Behavior

#### ProductCard Grid

**Mobile (< 640px):**
```css
.product-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-md);
}
```

**Tablet (≥ 640px):**
```css
@media (min-width: 640px) {
  .product-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

**Desktop (≥ 1024px):**
```css
@media (min-width: 1024px) {
  .product-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

**Large Desktop (≥ 1280px):**
```css
@media (min-width: 1280px) {
  .product-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
```

#### StatisticsKPIs Grid

**Mobile (< 768px):**
```css
.kpi-grid {
  grid-template-columns: 1fr;
}
```

**Tablet (≥ 768px):**
```css
@media (min-width: 768px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

**Desktop (≥ 1024px):**
```css
@media (min-width: 1024px) {
  .kpi-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

#### Mobile Navigation

- Use hamburger menu for mobile
- Full navigation visible on desktop
- Sticky header on scroll

---

## Implementation Guidelines

### File Structure Recommendation

```
src/
├── styles/
│   ├── tokens.css          # Design tokens (colors, spacing, etc.)
│   ├── typography.css      # Font imports and typography styles
│   ├── layout.css          # Layout utilities
│   └── components/
│       ├── ProductCard.css
│       ├── StatusBadges.css
│       ├── PriceChart.css
│       ├── StatisticsKPIs.css
│       └── AlertManager.css
├── components/
│   ├── ProductCard/
│   │   ├── ProductCard.tsx
│   │   └── ProductCard.module.css
│   ├── StatusBadges/
│   │   ├── StatusBadge.tsx
│   │   └── StatusBadge.module.css
│   └── ...
└── pages/
    ├── Dashboard.tsx
    ├── ProductDetail.tsx
    └── Search.tsx
```

### CSS Methodology

**Option 1: CSS Modules**
- Scoped styles per component
- Use design tokens via CSS variables
- Example: `ProductCard.module.css`

**Option 2: Tailwind CSS**
- Extend Tailwind config with design tokens
- Use custom classes for complex components
- Maintain design system consistency

**Option 3: Styled Components / Emotion**
- Theme provider with design tokens
- Component-scoped styles
- Dynamic theming support

### Performance Considerations

1. **Lazy Load Images:**
   ```jsx
   <img loading="lazy" src={imageUrl} alt={productName} />
   ```

2. **Optimize Bundle Size:**
   - Tree-shake icon libraries
   - Code split by route
   - Minimize CSS

3. **Animations:**
   - Use `transform` and `opacity` for best performance
   - Avoid animating `width`, `height`, or `top/left`
   - Use `will-change` sparingly

---

## Accessibility

### WCAG 2.1 Level AA Compliance

#### Color Contrast

All color combinations meet WCAG AA standards:
- Text on backgrounds: minimum 4.5:1 ratio
- Large text: minimum 3:1 ratio
- Interactive elements: minimum 3:1 ratio

#### Keyboard Navigation

- All interactive elements must be keyboard accessible
- Visible focus indicators on all focusable elements
- Logical tab order
- Skip links for navigation

#### Screen Readers

- Semantic HTML elements
- ARIA labels where needed
- Alt text for all images
- Status announcements for dynamic content

```html
<!-- Example: Alert status announcement -->
<div role="status" aria-live="polite" aria-atomic="true">
  Price alert triggered for {productName}
</div>
```

#### Focus Indicators

```css
*:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
```

---

## Animation Guidelines

### Duration

```css
--duration-fast: 150ms;
--duration-normal: 200ms;
--duration-slow: 300ms;
```

### Easing Functions

```css
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in: cubic-bezier(0.4, 0, 1, 1);
```

### Common Animations

**Fade In**
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.fade-in {
  animation: fadeIn var(--duration-normal) var(--ease-out);
}
```

**Slide Up**
```css
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.slide-up {
  animation: slideUp var(--duration-normal) var(--ease-out);
}
```

**Pulse (for alerts)**
```css
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

.pulse {
  animation: pulse 2s var(--ease-in-out) infinite;
}
```

---

## Integration with Backend

### API Data Mapping

Refer to `FRONTEND_INTEGRATION_GUIDE.md` for detailed API documentation.

**Key Data Points:**

```typescript
interface Product {
  id: number;
  name: string;
  last_known_price: number;
  is_on_sale: boolean;
  original_price?: number;
  alert_price?: number;
  alert_triggered: boolean;
  // ... other fields
}

interface PriceHistoryPoint {
  price: number;
  timestamp: string;
  is_on_sale: boolean;
  original_price?: number;
}
```

### Display Logic

**ProductCard Component:**
```typescript
// Status border
const statusBorderClass = 
  product.alert_triggered ? 'product-card--alert-triggered' :
  product.is_on_sale ? 'product-card--on-sale' :
  '';

// Badges
const badges = [];
if (product.is_on_sale) {
  badges.push({ type: 'on-sale', text: 'ON SALE', icon: 'tag' });
}
if (product.alert_price && !product.alert_triggered) {
  badges.push({ type: 'alert-set', text: 'ALERT SET', icon: 'bell' });
}
if (product.alert_triggered) {
  badges.push({ type: 'alert-triggered', text: 'PRICE REACHED!', icon: 'bell-ringing' });
}

// Price display
const currentPrice = formatCurrency(product.last_known_price);
const originalPrice = product.is_on_sale && product.original_price
  ? formatCurrency(product.original_price)
  : null;
```

---

## Testing Checklist

### Visual Testing

- [ ] All components render correctly on mobile, tablet, desktop
- [ ] Color contrast meets WCAG AA standards
- [ ] Typography scales properly across breakpoints
- [ ] Spacing is consistent using design tokens
- [ ] Shadows and borders render correctly

### Interaction Testing

- [ ] Hover states work on all interactive elements
- [ ] Focus indicators visible and accessible
- [ ] Loading states display correctly
- [ ] Toast notifications appear and dismiss properly
- [ ] Animations perform smoothly (60fps)

### Functionality Testing

- [ ] ProductCard displays correct status (sale, alert)
- [ ] StatusBadges show appropriate icons and colors
- [ ] PriceHistoryChart differentiates sales from fluctuations
- [ ] StatisticsKPIs calculate correctly
- [ ] AlertManager sets and clears alerts properly

### Accessibility Testing

- [ ] Keyboard navigation works throughout
- [ ] Screen reader announces status changes
- [ ] All images have alt text
- [ ] Form inputs have labels
- [ ] ARIA attributes used correctly

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-16 | Initial design system specification |

---

## References

- [FRONTEND_INTEGRATION_GUIDE.md](./FRONTEND_INTEGRATION_GUIDE.md) - API integration details
- [README.md](./README.md) - Backend API documentation
- [Tabler Icons](https://tabler-icons.io/) - Recommended icon library
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/) - Accessibility standards

---

## Support

For questions or clarifications about this design system, please refer to the project documentation or contact the design team.
