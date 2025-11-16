# PriceScout Component Examples

This document provides code examples and implementation guidelines for all PriceScout UI components based on the Design System.

## Table of Contents
- [ProductCard Component](#productcard-component)
- [StatusBadges Component](#statusbadges-component)
- [PriceHistoryChart Component](#pricehistorychart-component)
- [StatisticsKPIs Component](#statisticskpis-component)
- [AlertManager Component](#alertmanager-component)
- [Toast Notifications](#toast-notifications)
- [Empty States](#empty-states)
- [Skeleton Loaders](#skeleton-loaders)

---

## ProductCard Component

### React/TypeScript Example

```tsx
import React from 'react';
import './ProductCard.css';

interface ProductCardProps {
  id: number;
  name: string;
  imageUrl?: string;
  currentPrice: number;
  originalPrice?: number;
  isOnSale: boolean;
  alertPrice?: number;
  alertTriggered: boolean;
  lastCheckTime: string;
  onClick?: () => void;
}

const ProductCard: React.FC<ProductCardProps> = ({
  id,
  name,
  imageUrl,
  currentPrice,
  originalPrice,
  isOnSale,
  alertPrice,
  alertTriggered,
  lastCheckTime,
  onClick
}) => {
  const statusClass = alertTriggered 
    ? 'product-card--alert-triggered'
    : isOnSale 
    ? 'product-card--on-sale'
    : '';

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('cs-CZ', {
      style: 'currency',
      currency: 'CZK',
      minimumFractionDigits: 0
    }).format(price);
  };

  const getTimeAgo = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    
    if (diffHours < 1) return 'Just now';
    if (diffHours === 1) return '1 hour ago';
    if (diffHours < 24) return `${diffHours} hours ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays === 1) return '1 day ago';
    return `${diffDays} days ago`;
  };

  return (
    <div 
      className={`product-card ${statusClass}`}
      onClick={onClick}
      role="button"
      tabIndex={0}
    >
      <div className="product-card__image">
        {imageUrl ? (
          <img src={imageUrl} alt={name} loading="lazy" />
        ) : (
          <div className="product-card__image-placeholder">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
              <circle cx="8.5" cy="8.5" r="1.5" />
              <polyline points="21 15 16 10 5 21" />
            </svg>
          </div>
        )}
      </div>

      <div className="product-card__content">
        <h3 className="product-card__title">{name}</h3>

        <div className="product-card__badges">
          {isOnSale && (
            <span className="badge badge--on-sale">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" />
                <line x1="7" y1="7" x2="7.01" y2="7" />
              </svg>
              ON SALE
            </span>
          )}
          {alertPrice && !alertTriggered && (
            <span className="badge badge--alert-set">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                <path d="M13.73 21a2 2 0 0 1-3.46 0" />
              </svg>
              ALERT SET
            </span>
          )}
          {alertTriggered && (
            <span className="badge badge--alert-triggered">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                <path d="M13.73 21a2 2 0 0 1-3.46 0" />
              </svg>
              PRICE REACHED!
            </span>
          )}
        </div>

        <div className="product-card__price">
          <span className="product-card__current-price">
            {formatPrice(currentPrice)}
          </span>
          {isOnSale && originalPrice && (
            <span className="product-card__original-price">
              {formatPrice(originalPrice)}
            </span>
          )}
        </div>

        <div className="product-card__meta">
          <span className="product-card__last-check">
            Last checked: {getTimeAgo(lastCheckTime)}
          </span>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
```

### CSS for ProductCard

```css
.product-card {
  background: var(--color-bg-white);
  border: 1px solid var(--color-border-default);
  border-left: 3px solid transparent;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-default);
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-in-out);
  overflow: hidden;
}

.product-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px) scale(1.01);
}

.product-card:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.product-card--on-sale {
  border-left-color: var(--color-accent-sale);
}

.product-card--alert-triggered {
  border-left-color: var(--color-accent-alert-triggered);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.9; }
}

.product-card__image {
  width: 100%;
  aspect-ratio: 1 / 1;
  background: var(--color-bg-light);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.product-card__image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.product-card__image-placeholder {
  color: var(--color-text-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-card__content {
  padding: var(--spacing-md);
}

.product-card__title {
  font-family: var(--font-family-body);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm) 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: var(--line-height-tight);
}

.product-card__badges {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.product-card__price {
  display: flex;
  align-items: baseline;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.product-card__current-price {
  font-family: var(--font-family-headings);
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
}

.product-card__original-price {
  font-family: var(--font-family-body);
  font-size: var(--font-size-md);
  color: var(--color-text-secondary);
  text-decoration: line-through;
}

.product-card__meta {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}
```

---

## StatusBadges Component

### React/TypeScript Example

```tsx
import React from 'react';
import './StatusBadge.css';

type BadgeVariant = 'on-sale' | 'alert-set' | 'alert-triggered';

interface StatusBadgeProps {
  variant: BadgeVariant;
  size?: 'sm' | 'md' | 'lg';
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ variant, size = 'md' }) => {
  const config = {
    'on-sale': {
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" />
          <line x1="7" y1="7" x2="7.01" y2="7" />
        </svg>
      ),
      text: 'ON SALE'
    },
    'alert-set': {
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
          <path d="M13.73 21a2 2 0 0 1-3.46 0" />
        </svg>
      ),
      text: 'ALERT SET'
    },
    'alert-triggered': {
      icon: (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
          <path d="M13.73 21a2 2 0 0 1-3.46 0" />
        </svg>
      ),
      text: 'PRICE REACHED!'
    }
  };

  const { icon, text } = config[variant];

  return (
    <span className={`badge badge--${variant} badge--${size}`}>
      {icon}
      {text}
    </span>
  );
};

export default StatusBadge;
```

### CSS for StatusBadge

```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: var(--badge-padding-md);
  border-radius: var(--border-radius-pill);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  text-transform: uppercase;
  letter-spacing: var(--letter-spacing-wide);
  line-height: 1;
}

.badge--sm {
  padding: var(--badge-padding-sm);
  font-size: var(--font-size-xs);
}

.badge--md {
  padding: var(--badge-padding-md);
  font-size: var(--font-size-sm);
}

.badge--lg {
  padding: var(--badge-padding-lg);
  font-size: var(--font-size-md);
}

.badge--on-sale {
  background: var(--color-accent-sale-bg);
  color: var(--color-accent-sale);
}

.badge--alert-set {
  background: var(--color-accent-alert-bg);
  color: var(--color-accent-alert);
}

.badge--alert-triggered {
  background: var(--color-accent-alert-triggered-bg);
  color: var(--color-accent-alert-triggered);
  font-weight: var(--font-weight-bold);
}

.badge svg {
  stroke-width: 2;
}
```

---

## PriceHistoryChart Component

### React/TypeScript Example with Recharts

```tsx
import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Scatter,
  ComposedChart
} from 'recharts';
import './PriceHistoryChart.css';

interface PricePoint {
  price: number;
  timestamp: string;
  is_on_sale: boolean;
  original_price?: number;
}

interface PriceHistoryChartProps {
  data: PricePoint[];
  alertPrice?: number;
  currency?: string;
}

const PriceHistoryChart: React.FC<PriceHistoryChartProps> = ({
  data,
  alertPrice,
  currency = 'CZK'
}) => {
  const formatPrice = (value: number) => {
    return new Intl.NumberFormat('cs-CZ', {
      style: 'currency',
      currency,
      minimumFractionDigits: 0
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('cs-CZ', {
      month: 'short',
      day: 'numeric'
    }).format(date);
  };

  const salePoints = data.filter(point => point.is_on_sale);

  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;

    const point = payload[0].payload;

    return (
      <div className="chart-tooltip">
        <p className="chart-tooltip__date">
          {new Intl.DateTimeFormat('cs-CZ', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          }).format(new Date(point.timestamp))}
        </p>
        <p className="chart-tooltip__price">
          {formatPrice(point.price)}
        </p>
        <p className={`chart-tooltip__status ${point.is_on_sale ? 'chart-tooltip__status--sale' : ''}`}>
          {point.is_on_sale ? '🏷️ On Sale' : '📊 Regular Price'}
        </p>
      </div>
    );
  };

  return (
    <div className="price-chart">
      <h3 className="price-chart__title">Price History</h3>
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-default)" />
          
          <XAxis
            dataKey="timestamp"
            tickFormatter={formatDate}
            stroke="var(--color-text-secondary)"
            style={{ fontSize: '14px' }}
          />
          
          <YAxis
            tickFormatter={formatPrice}
            stroke="var(--color-text-secondary)"
            style={{ fontSize: '14px' }}
          />
          
          <Tooltip content={<CustomTooltip />} />
          
          {alertPrice && (
            <ReferenceLine
              y={alertPrice}
              stroke="var(--color-accent-alert-triggered)"
              strokeDasharray="5 5"
              strokeWidth={2}
              label={{
                value: `Alert: ${formatPrice(alertPrice)}`,
                position: 'right',
                fill: 'var(--color-accent-alert-triggered)',
                fontSize: 14
              }}
            />
          )}
          
          <Line
            type="monotone"
            dataKey="price"
            stroke="var(--color-primary)"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 6, fill: 'var(--color-primary)' }}
          />
          
          <Scatter
            data={salePoints}
            dataKey="price"
            fill="var(--color-accent-sale)"
            shape="circle"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PriceHistoryChart;
```

### CSS for PriceHistoryChart

```css
.price-chart {
  background: var(--color-bg-white);
  padding: var(--spacing-lg);
  border-radius: var(--border-radius);
  border: 1px solid var(--color-border-default);
}

.price-chart__title {
  font-family: var(--font-family-headings);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-md) 0;
}

.chart-tooltip {
  background: var(--color-text-primary);
  color: var(--color-bg-white);
  padding: 12px 16px;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
}

.chart-tooltip__date {
  font-size: var(--font-size-sm);
  margin: 0 0 4px 0;
  opacity: 0.9;
}

.chart-tooltip__price {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  margin: 0 0 4px 0;
}

.chart-tooltip__status {
  font-size: var(--font-size-sm);
  margin: 0;
}

.chart-tooltip__status--sale {
  color: var(--color-accent-sale);
  font-weight: var(--font-weight-semibold);
}

@media (max-width: 768px) {
  .price-chart {
    padding: var(--spacing-md);
  }
  
  .recharts-surface {
    overflow: visible;
  }
}
```

---

## StatisticsKPIs Component

### React/TypeScript Example

```tsx
import React from 'react';
import './StatisticsKPIs.css';

interface KPIData {
  label: string;
  value: string | number;
  change?: {
    value: number;
    percentage: number;
    direction: 'up' | 'down';
  };
}

interface StatisticsKPIsProps {
  currentPrice: number;
  lowestPrice: number;
  highestPrice: number;
  initialPrice: number;
  timesOnSale: number;
  currency?: string;
}

const StatisticsKPIs: React.FC<StatisticsKPIsProps> = ({
  currentPrice,
  lowestPrice,
  highestPrice,
  initialPrice,
  timesOnSale,
  currency = 'CZK'
}) => {
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('cs-CZ', {
      style: 'currency',
      currency,
      minimumFractionDigits: 0
    }).format(price);
  };

  const priceChange = currentPrice - initialPrice;
  const priceChangePercentage = ((priceChange / initialPrice) * 100).toFixed(1);
  const priceDirection = priceChange > 0 ? 'up' : 'down';

  const kpis: KPIData[] = [
    {
      label: 'Current Price',
      value: formatPrice(currentPrice)
    },
    {
      label: 'Lowest Recorded',
      value: formatPrice(lowestPrice)
    },
    {
      label: 'Highest Recorded',
      value: formatPrice(highestPrice)
    },
    {
      label: 'Initial Price',
      value: formatPrice(initialPrice)
    },
    {
      label: 'Price Change',
      value: formatPrice(Math.abs(priceChange)),
      change: {
        value: priceChange,
        percentage: parseFloat(priceChangePercentage),
        direction: priceDirection
      }
    },
    {
      label: 'Times on Sale',
      value: timesOnSale
    }
  ];

  return (
    <div className="kpi-grid">
      {kpis.map((kpi, index) => (
        <div key={index} className="kpi-card">
          <div className="kpi-card__label">{kpi.label}</div>
          <div className={`kpi-card__value ${kpi.change ? `kpi-card__value--${kpi.change.direction}` : ''}`}>
            {kpi.change && (
              <span className="kpi-card__arrow">
                {kpi.change.direction === 'up' ? '↑' : '↓'}
              </span>
            )}
            {kpi.value}
            {kpi.change && (
              <span className="kpi-card__percentage">
                ({kpi.change.percentage}%)
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default StatisticsKPIs;
```

### CSS for StatisticsKPIs

```css
.kpi-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-md);
}

@media (min-width: 640px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .kpi-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.kpi-card {
  background: var(--color-bg-light);
  padding: var(--spacing-md);
  border-radius: var(--border-radius);
  transition: transform var(--duration-fast) var(--ease-out);
}

.kpi-card:hover {
  transform: translateY(-2px);
}

.kpi-card__label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  font-weight: var(--font-weight-medium);
  letter-spacing: var(--letter-spacing-wider);
  margin-bottom: var(--spacing-sm);
}

.kpi-card__value {
  font-family: var(--font-family-headings);
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.kpi-card__value--up {
  color: var(--color-accent-sale);
}

.kpi-card__value--down {
  color: var(--color-accent-alert);
}

.kpi-card__arrow {
  font-size: var(--font-size-2xl);
}

.kpi-card__percentage {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-medium);
  opacity: 0.8;
}
```

---

## AlertManager Component

### React/TypeScript Example

```tsx
import React, { useState } from 'react';
import './AlertManager.css';

interface AlertManagerProps {
  productId: number;
  currentAlertPrice?: number;
  alertTriggered: boolean;
  onSetAlert: (price: number) => Promise<void>;
  onClearAlert: () => Promise<void>;
}

const AlertManager: React.FC<AlertManagerProps> = ({
  productId,
  currentAlertPrice,
  alertTriggered,
  onSetAlert,
  onClearAlert
}) => {
  const [alertPrice, setAlertPrice] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSetAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    const price = parseFloat(alertPrice);
    
    if (isNaN(price) || price <= 0) {
      alert('Please enter a valid price');
      return;
    }

    setIsLoading(true);
    try {
      await onSetAlert(price);
      setAlertPrice('');
    } catch (error) {
      console.error('Failed to set alert:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearAlert = async () => {
    setIsLoading(true);
    try {
      await onClearAlert();
    } catch (error) {
      console.error('Failed to clear alert:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="alert-manager">
      <h3 className="alert-manager__title">Price Alert</h3>

      {currentAlertPrice && (
        <div className="alert-manager__current-alert">
          <span className="alert-manager__bell">🔔</span>
          {alertTriggered ? (
            <span className="alert-manager__triggered">
              Alert triggered! Price reached Kč {currentAlertPrice.toLocaleString()}
            </span>
          ) : (
            <span>
              Alert active at: Kč {currentAlertPrice.toLocaleString()}
            </span>
          )}
        </div>
      )}

      <form onSubmit={handleSetAlert} className="alert-manager__form">
        <label htmlFor={`alert-input-${productId}`} className="alert-manager__label">
          Set new price alert:
        </label>
        
        <div className="alert-input-wrapper">
          <span className="alert-input-prefix">Kč</span>
          <input
            id={`alert-input-${productId}`}
            type="number"
            step="0.01"
            min="0"
            className="alert-input alert-input--with-prefix"
            value={alertPrice}
            onChange={(e) => setAlertPrice(e.target.value)}
            placeholder="Enter target price"
            disabled={isLoading}
          />
        </div>

        <div className="alert-manager__actions">
          <button
            type="submit"
            className={`btn-primary ${isLoading ? 'btn-loading' : ''}`}
            disabled={isLoading || !alertPrice}
          >
            Set Alert
          </button>

          {currentAlertPrice && (
            <button
              type="button"
              className={`btn-secondary ${isLoading ? 'btn-loading' : ''}`}
              onClick={handleClearAlert}
              disabled={isLoading}
            >
              Clear Alert
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default AlertManager;
```

### CSS for AlertManager

```css
.alert-manager {
  background: var(--color-bg-white);
  border: 1px solid var(--color-border-default);
  border-radius: var(--border-radius);
  padding: var(--spacing-lg);
}

.alert-manager__title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-md) 0;
}

.alert-manager__current-alert {
  background: var(--color-accent-alert-bg);
  color: var(--color-accent-alert);
  padding: 12px 16px;
  border-radius: var(--border-radius);
  margin-bottom: var(--spacing-md);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-weight: var(--font-weight-medium);
}

.alert-manager__bell {
  font-size: var(--font-size-xl);
}

.alert-manager__triggered {
  color: var(--color-accent-alert-triggered);
  font-weight: var(--font-weight-bold);
}

.alert-manager__form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.alert-manager__label {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
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
  font-weight: var(--font-weight-medium);
  pointer-events: none;
}

.alert-input {
  width: 100%;
  padding: 12px 16px;
  font-size: var(--font-size-md);
  font-family: var(--font-family-body);
  border: 2px solid var(--color-border-default);
  border-radius: var(--border-radius);
  transition: border-color var(--duration-fast) var(--ease-out);
}

.alert-input--with-prefix {
  padding-left: 44px;
}

.alert-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.alert-input:disabled {
  background: var(--color-bg-light);
  cursor: not-allowed;
}

.alert-manager__actions {
  display: flex;
  gap: var(--spacing-md);
}

.btn-primary,
.btn-secondary {
  padding: 12px 24px;
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  border: none;
}

.btn-primary {
  background: var(--color-primary);
  color: var(--color-bg-white);
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.btn-primary:active:not(:disabled) {
  transform: scale(0.98);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: transparent;
  color: var(--color-accent-sale);
  border: 2px solid var(--color-accent-sale);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--color-accent-sale-bg);
}

.btn-secondary:active:not(:disabled) {
  transform: scale(0.98);
}

.btn-loading {
  position: relative;
  color: transparent !important;
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

---

## Toast Notifications

### React/TypeScript Example

```tsx
import React, { useEffect } from 'react';
import './Toast.css';

type ToastType = 'success' | 'error' | 'info' | 'warning';

interface ToastProps {
  type: ToastType;
  message: string;
  onClose: () => void;
  duration?: number;
}

const Toast: React.FC<ToastProps> = ({ type, message, onClose, duration = 3000 }) => {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const icons = {
    success: '✓',
    error: '✕',
    info: 'ℹ',
    warning: '⚠'
  };

  return (
    <div className={`toast toast--${type}`}>
      <span className="toast__icon">{icons[type]}</span>
      <span className="toast__message">{message}</span>
      <button className="toast__close" onClick={onClose} aria-label="Close notification">
        ×
      </button>
    </div>
  );
};

export default Toast;
```

### CSS for Toast

```css
.toast {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--toast-padding);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-xl);
  min-width: 300px;
  max-width: 500px;
  color: white;
  animation: slideIn var(--duration-normal) var(--ease-out);
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.toast--success {
  background: var(--color-accent-alert);
}

.toast--error {
  background: var(--color-accent-sale);
}

.toast--warning {
  background: var(--color-accent-alert-triggered);
}

.toast--info {
  background: var(--color-primary);
}

.toast__icon {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  flex-shrink: 0;
}

.toast__message {
  flex: 1;
  font-size: var(--font-size-md);
}

.toast__close {
  background: none;
  border: none;
  color: white;
  font-size: var(--font-size-2xl);
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.8;
  transition: opacity var(--duration-fast);
  flex-shrink: 0;
}

.toast__close:hover {
  opacity: 1;
}

/* Toast Container */
.toast-container {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: var(--z-index-toast);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  pointer-events: none;
}

.toast-container > * {
  pointer-events: all;
}

@media (max-width: 640px) {
  .toast-container {
    left: 16px;
    right: 16px;
    top: 16px;
  }
  
  .toast {
    min-width: auto;
  }
}
```

---

## Empty States

### React/TypeScript Example

```tsx
import React from 'react';
import './EmptyState.css';

interface EmptyStateProps {
  type: 'no-products' | 'no-results';
  onAction?: () => void;
}

const EmptyState: React.FC<EmptyStateProps> = ({ type, onAction }) => {
  const config = {
    'no-products': {
      icon: '📦',
      title: 'No Products Tracked Yet',
      description: 'Start tracking products to monitor prices and get alerts',
      actionLabel: 'Search Products'
    },
    'no-results': {
      icon: '🔍',
      title: 'No Results Found',
      description: 'Try adjusting your search terms',
      actionLabel: null
    }
  };

  const { icon, title, description, actionLabel } = config[type];

  return (
    <div className="empty-state">
      <div className="empty-state__icon">{icon}</div>
      <h2 className="empty-state__title">{title}</h2>
      <p className="empty-state__description">{description}</p>
      {actionLabel && onAction && (
        <button className="btn-primary" onClick={onAction}>
          {actionLabel}
        </button>
      )}
    </div>
  );
};

export default EmptyState;
```

### CSS for EmptyState

```css
.empty-state {
  text-align: center;
  padding: var(--spacing-3xl) var(--spacing-md);
  color: var(--color-text-secondary);
}

.empty-state__icon {
  font-size: 4rem;
  margin-bottom: var(--spacing-lg);
  opacity: 0.5;
}

.empty-state__title {
  font-family: var(--font-family-headings);
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm) 0;
}

.empty-state__description {
  font-size: var(--font-size-md);
  margin: 0 0 var(--spacing-xl) 0;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}
```

---

## Skeleton Loaders

### React/TypeScript Example

```tsx
import React from 'react';
import './Skeleton.css';

const SkeletonProductCard: React.FC = () => {
  return (
    <div className="skeleton-card">
      <div className="skeleton skeleton-image" />
      <div className="skeleton-content">
        <div className="skeleton skeleton-title" />
        <div className="skeleton skeleton-title skeleton-title--short" />
        <div className="skeleton-badges">
          <div className="skeleton skeleton-badge" />
          <div className="skeleton skeleton-badge" />
        </div>
        <div className="skeleton skeleton-price" />
        <div className="skeleton skeleton-meta" />
      </div>
    </div>
  );
};

export default SkeletonProductCard;
```

### CSS for Skeleton

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
  border-radius: var(--border-radius-sm);
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.skeleton-card {
  background: var(--color-bg-white);
  border: 1px solid var(--color-border-default);
  border-radius: var(--border-radius);
  overflow: hidden;
}

.skeleton-image {
  width: 100%;
  aspect-ratio: 1 / 1;
}

.skeleton-content {
  padding: var(--spacing-md);
}

.skeleton-title {
  height: 20px;
  margin-bottom: var(--spacing-sm);
}

.skeleton-title--short {
  width: 60%;
}

.skeleton-badges {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.skeleton-badge {
  width: 80px;
  height: 24px;
  border-radius: var(--border-radius-pill);
}

.skeleton-price {
  height: 32px;
  width: 40%;
  margin-bottom: var(--spacing-sm);
}

.skeleton-meta {
  height: 16px;
  width: 50%;
}
```

---

This document provides complete implementation examples for all major components in the PriceScout design system. Use these as starting points and customize according to your specific framework and requirements.
