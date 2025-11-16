// Main Application Logic

let allProducts = [];
let currentFilter = 'all';
let currentProductDetail = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeNavigation();
    initializeSearchForm();
    initializeTabs();
    loadDashboard();
});

// Initialize navigation
function initializeNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            navigateTo(page);
        });
    });
}

// Initialize search form
function initializeSearchForm() {
    const form = document.getElementById('search-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const site = document.getElementById('search-site').value;
        const query = document.getElementById('search-query').value;
        
        if (!query.trim()) {
            showToast('Please enter a search query', 'error');
            return;
        }
        
        await performSearch(site, query);
    });
}

// Initialize filter tabs
function initializeTabs() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            // Update active tab
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Filter products
            currentFilter = tab.dataset.filter;
            filterProducts();
        });
    });
}

// Load dashboard
async function loadDashboard() {
    const loadingSpinner = document.getElementById('loading-spinner');
    const productGrid = document.getElementById('product-grid');
    const emptyState = document.getElementById('empty-state');
    
    try {
        loadingSpinner.style.display = 'block';
        productGrid.style.display = 'none';
        emptyState.style.display = 'none';
        
        allProducts = await api.getTrackedProducts();
        
        loadingSpinner.style.display = 'none';
        
        if (allProducts.length === 0) {
            emptyState.style.display = 'block';
        } else {
            productGrid.style.display = 'grid';
            updateStats();
            filterProducts();
        }
    } catch (error) {
        console.error('Error loading products:', error);
        loadingSpinner.style.display = 'none';
        showToast('Failed to load products', 'error');
    }
}

// Update statistics
function updateStats() {
    const total = allProducts.length;
    const onSale = allProducts.filter(p => p.is_on_sale).length;
    const alerts = allProducts.filter(p => p.alert_triggered).length;
    
    document.getElementById('stat-total').textContent = total;
    document.getElementById('stat-sale').textContent = onSale;
    document.getElementById('stat-alerts').textContent = alerts;
}

// Filter products based on current filter
function filterProducts() {
    let filtered = allProducts;
    
    if (currentFilter === 'sale') {
        filtered = allProducts.filter(p => p.is_on_sale);
    } else if (currentFilter === 'alert') {
        filtered = allProducts.filter(p => p.alert_triggered);
    }
    
    renderProducts(filtered);
}

// Render products
function renderProducts(products) {
    const productGrid = document.getElementById('product-grid');
    
    if (products.length === 0) {
        productGrid.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">🔍</div>
                <h3>No Products Found</h3>
                <p>No products match the selected filter</p>
            </div>
        `;
        return;
    }
    
    productGrid.innerHTML = products.map(product => createProductCard(product)).join('');
}

// Create product card HTML
function createProductCard(product) {
    const badges = [];
    
    if (product.is_on_sale) {
        badges.push('<span class="badge badge--sale">🏷️ ON SALE</span>');
    }
    
    if (product.alert_triggered) {
        badges.push('<span class="badge badge--alert-triggered">🔔 PRICE REACHED!</span>');
    } else if (product.alert_price) {
        badges.push('<span class="badge badge--alert">🔔 ALERT SET</span>');
    }
    
    const cardClass = product.alert_triggered 
        ? 'product-card--alert-triggered' 
        : product.is_on_sale 
        ? 'product-card--on-sale' 
        : '';
    
    const categories = categoryManager.getCategoriesForProduct(product.id);
    
    return `
        <div class="product-card ${cardClass}" onclick="showProductDetail(${product.id})">
            <img src="${getPlaceholderImage()}" 
                 alt="${product.name}" 
                 class="product-card__image"
                 onerror="this.src='${getPlaceholderImage()}'">
            <div class="product-card__content">
                <h3 class="product-card__title">${product.name}</h3>
                <div class="product-card__badges">
                    ${badges.join('')}
                </div>
                <div class="product-card__price-container">
                    <span class="product-card__price">${formatPrice(product.last_known_price)}</span>
                    ${product.is_on_sale && product.original_price ? `
                        <span class="product-card__original-price">${formatPrice(product.original_price)}</span>
                    ` : ''}
                </div>
                ${categories.length > 0 ? `
                    <div style="margin-bottom: var(--spacing-sm); font-size: var(--font-size-sm); color: var(--color-text-secondary);">
                        📂 ${categories.map(c => c.name).join(', ')}
                    </div>
                ` : ''}
                <div class="product-card__meta">
                    Last checked: ${timeAgo(product.last_check_time)}
                </div>
            </div>
        </div>
    `;
}

// Perform search
async function performSearch(site, query) {
    const resultsContainer = document.getElementById('search-results-container');
    const resultsGrid = document.getElementById('search-results');
    
    try {
        resultsContainer.style.display = 'block';
        resultsGrid.innerHTML = '<div class="loading-spinner"><div class="spinner"></div><p>Searching...</p></div>';
        
        const response = await api.searchProducts(site, query);
        const results = response.results;
        
        if (results.length === 0) {
            resultsGrid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🔍</div>
                    <h3>No Results Found</h3>
                    <p>Try adjusting your search terms</p>
                </div>
            `;
            return;
        }
        
        resultsGrid.innerHTML = results.map(result => createSearchResultCard(result)).join('');
    } catch (error) {
        console.error('Search error:', error);
        showToast('Search failed. Please try again.', 'error');
        resultsGrid.innerHTML = '';
    }
}

// Create search result card
function createSearchResultCard(result) {
    return `
        <div class="search-result-card">
            <img src="${result.image_url || getPlaceholderImage()}" 
                 alt="${result.name}" 
                 class="search-result-card__image"
                 onerror="this.src='${getPlaceholderImage()}'">
            <div class="search-result-card__content">
                <h3 class="search-result-card__title">${result.name}</h3>
                ${result.is_on_sale ? '<span class="badge badge--sale">🏷️ ON SALE</span>' : ''}
                <div class="search-result-card__price-row">
                    <span class="search-result-card__price">${formatPrice(result.price)}</span>
                    ${result.is_on_sale && result.original_price ? `
                        <span class="search-result-card__original-price">${formatPrice(result.original_price)}</span>
                    ` : ''}
                </div>
                <div class="search-result-card__actions">
                    <button class="btn-primary btn-small" onclick="trackProductFromSearch('${result.product_url}', event)">
                        ➕ Track
                    </button>
                    <a href="${result.product_url}" target="_blank" class="btn-secondary btn-small">
                        View →
                    </a>
                </div>
            </div>
        </div>
    `;
}

// Track product from search
async function trackProductFromSearch(url, event) {
    event.stopPropagation();
    
    const button = event.target;
    const originalText = button.innerHTML;
    
    try {
        button.disabled = true;
        button.innerHTML = 'Tracking...';
        
        await api.trackProduct(url);
        showToast('Product tracked successfully!', 'success');
        button.innerHTML = '✓ Tracked';
        
        // Reload dashboard data
        setTimeout(() => {
            loadDashboard();
        }, 1000);
    } catch (error) {
        console.error('Track error:', error);
        showToast(error.message || 'Failed to track product', 'error');
        button.disabled = false;
        button.innerHTML = originalText;
    }
}

// Show product detail
async function showProductDetail(productId) {
    navigateTo('product-detail');
    
    const content = document.getElementById('product-detail-content');
    content.innerHTML = '<div class="loading-spinner"><div class="spinner"></div><p>Loading product details...</p></div>';
    
    try {
        const [product, history] = await Promise.all([
            api.getProduct(productId),
            api.getPriceHistory(productId),
        ]);
        
        currentProductDetail = { product, history };
        renderProductDetail(product, history);
    } catch (error) {
        console.error('Error loading product detail:', error);
        showToast('Failed to load product details', 'error');
        content.innerHTML = '<p>Failed to load product details</p>';
    }
}

// Render product detail
function renderProductDetail(product, history) {
    const content = document.getElementById('product-detail-content');
    const stats = calculateStats(history);
    const categories = categoryManager.getCategoriesForProduct(product.id);
    
    content.innerHTML = `
        <div class="product-detail">
            <div class="product-detail__header">
                <img src="${getPlaceholderImage()}" 
                     alt="${product.name}" 
                     class="product-detail__image">
                <div class="product-detail__info">
                    <h1>${product.name}</h1>
                    ${product.is_on_sale ? '<span class="badge badge--sale">🏷️ ON SALE</span>' : ''}
                    <div class="product-detail__price-section">
                        <div class="product-detail__current-price">${formatPrice(product.last_known_price)}</div>
                        ${product.is_on_sale && product.original_price ? `
                            <div style="font-size: var(--font-size-lg); color: var(--color-text-secondary); text-decoration: line-through;">
                                ${formatPrice(product.original_price)}
                            </div>
                        ` : ''}
                    </div>
                    <span class="product-detail__eshop">🏪 ${product.eshop}</span>
                    <a href="${product.url}" target="_blank" class="product-detail__link">
                        Visit Product Page →
                    </a>
                    <div style="margin-top: var(--spacing-md);">
                        <button class="btn-secondary btn-small" onclick="showCategorySelector(${product.id})">
                            📂 Manage Categories
                        </button>
                        ${categories.length > 0 ? `
                            <div style="margin-top: var(--spacing-sm); font-size: var(--font-size-sm); color: var(--color-text-secondary);">
                                In: ${categories.map(c => c.name).join(', ')}
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
            
            ${renderKPIGrid(product, stats)}
            ${renderPriceChart(history, product.alert_price)}
            ${renderAlertManager(product)}
        </div>
    `;
    
    // Initialize chart after rendering
    if (history.length > 0) {
        setTimeout(() => initializeChart(history, product.alert_price), 100);
    }
}

// Render KPI Grid
function renderKPIGrid(product, stats) {
    const change = stats.initial ? calculatePriceChange(product.last_known_price, stats.initial) : null;
    
    return `
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-card__label">Current Price</div>
                <div class="kpi-card__value">${formatPrice(product.last_known_price)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-card__label">Lowest Recorded</div>
                <div class="kpi-card__value">${formatPrice(stats.lowest)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-card__label">Highest Recorded</div>
                <div class="kpi-card__value">${formatPrice(stats.highest)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-card__label">Initial Price</div>
                <div class="kpi-card__value">${formatPrice(stats.initial)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-card__label">Times on Sale</div>
                <div class="kpi-card__value">${stats.timesOnSale}</div>
            </div>
            ${change ? `
                <div class="kpi-card">
                    <div class="kpi-card__label">Price Change</div>
                    <div class="kpi-card__value ${change.isIncrease ? 'kpi-card__value--positive' : change.isDecrease ? 'kpi-card__value--negative' : ''}">
                        ${formatPrice(Math.abs(change.absolute))} (${change.percent.toFixed(1)}%)
                    </div>
                </div>
            ` : ''}
        </div>
    `;
}

// Render price chart
function renderPriceChart(history, alertPrice) {
    if (history.length === 0) {
        return '<p>No price history available yet.</p>';
    }
    
    return `
        <div class="chart-container">
            <h3>Price History</h3>
            <canvas id="price-chart"></canvas>
        </div>
    `;
}

// Initialize Chart.js chart
function initializeChart(history, alertPrice) {
    const ctx = document.getElementById('price-chart');
    if (!ctx) return;
    
    // Sort history by timestamp (oldest first for chart)
    const sortedHistory = [...history].sort((a, b) => 
        new Date(a.timestamp) - new Date(b.timestamp)
    );
    
    const labels = sortedHistory.map(h => formatDateTime(h.timestamp));
    const prices = sortedHistory.map(h => h.price);
    const salePoints = sortedHistory.map(h => h.is_on_sale ? h.price : null);
    
    const datasets = [
        {
            label: 'Price',
            data: prices,
            borderColor: '#3B82F6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 2,
            tension: 0.1,
            fill: true,
        },
        {
            label: 'On Sale',
            data: salePoints,
            borderColor: '#EF4444',
            backgroundColor: '#EF4444',
            pointRadius: 6,
            pointHoverRadius: 8,
            showLine: false,
            type: 'scatter',
        },
    ];
    
    // Add alert line if alert price is set
    if (alertPrice) {
        datasets.push({
            label: 'Alert Price',
            data: Array(prices.length).fill(alertPrice),
            borderColor: '#F59E0B',
            borderWidth: 2,
            borderDash: [5, 5],
            pointRadius: 0,
            fill: false,
        });
    }
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets,
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 2,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                },
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return formatPrice(value);
                        },
                    },
                },
            },
        },
    });
}

// Render alert manager
function renderAlertManager(product) {
    return `
        <div class="alert-manager">
            <h3>Price Alert</h3>
            ${product.alert_price ? `
                <div class="alert-current">
                    🔔 Alert active at: ${formatPrice(product.alert_price)}
                    ${product.alert_triggered ? ' - TRIGGERED!' : ''}
                </div>
            ` : ''}
            <form class="alert-form" onsubmit="setProductAlert(event, ${product.id})">
                <div class="form-group">
                    <label for="alert-price">Target Price (Kč)</label>
                    <input type="number" 
                           id="alert-price" 
                           class="form-input" 
                           placeholder="Enter target price"
                           value="${product.alert_price || ''}"
                           min="0"
                           step="1"
                           required>
                </div>
                <button type="submit" class="btn-primary">Set Alert</button>
                ${product.alert_price ? `
                    <button type="button" class="btn-secondary" onclick="clearProductAlert(${product.id})">
                        Clear Alert
                    </button>
                ` : ''}
            </form>
        </div>
    `;
}

// Set product alert
async function setProductAlert(event, productId) {
    event.preventDefault();
    
    const input = document.getElementById('alert-price');
    const targetPrice = parseFloat(input.value);
    
    if (!targetPrice || targetPrice <= 0) {
        showToast('Please enter a valid price', 'error');
        return;
    }
    
    try {
        await api.setAlert(productId, targetPrice);
        showToast('Alert set successfully!', 'success');
        
        // Reload product detail
        showProductDetail(productId);
    } catch (error) {
        console.error('Set alert error:', error);
        showToast('Failed to set alert', 'error');
    }
}

// Clear product alert
async function clearProductAlert(productId) {
    if (!confirm('Are you sure you want to clear this alert?')) {
        return;
    }
    
    try {
        await api.clearAlert(productId);
        showToast('Alert cleared', 'success');
        
        // Reload product detail
        showProductDetail(productId);
    } catch (error) {
        console.error('Clear alert error:', error);
        showToast('Failed to clear alert', 'error');
    }
}
