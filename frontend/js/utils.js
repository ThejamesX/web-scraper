// Utility Functions

// Format price in Czech Koruna
function formatPrice(price) {
    if (price === null || price === undefined) return 'N/A';
    return new Intl.NumberFormat('cs-CZ', {
        style: 'currency',
        currency: 'CZK',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(price);
}

// Format date/time
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('cs-CZ', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    }).format(date);
}

// Calculate time ago
function timeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    return formatDateTime(dateString);
}

// Show toast notification
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icon = type === 'success' ? '✓' : '✕';
    
    toast.innerHTML = `
        <span style="font-size: 1.25rem;">${icon}</span>
        <span>${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">✕</button>
    `;
    
    container.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Navigate between pages
function navigateTo(pageName) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Show selected page
    const targetPage = document.getElementById(`${pageName}-page`);
    if (targetPage) {
        targetPage.classList.add('active');
    }
    
    // Update navigation active state
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === pageName) {
            link.classList.add('active');
        }
    });
    
    // Load page data if needed
    if (pageName === 'dashboard') {
        loadDashboard();
    } else if (pageName === 'categories') {
        loadCategories();
    }
}

// Calculate statistics from price history
function calculateStats(history) {
    if (!history || history.length === 0) {
        return {
            lowest: null,
            highest: null,
            initial: null,
            timesOnSale: 0,
        };
    }
    
    const prices = history.map(h => h.price);
    const lowest = Math.min(...prices);
    const highest = Math.max(...prices);
    const initial = history[history.length - 1].price;
    const timesOnSale = history.filter(h => h.is_on_sale).length;
    
    return { lowest, highest, initial, timesOnSale };
}

// Calculate price change
function calculatePriceChange(currentPrice, previousPrice) {
    if (!previousPrice || previousPrice === 0) return { percent: 0, absolute: 0 };
    
    const absolute = currentPrice - previousPrice;
    const percent = ((absolute / previousPrice) * 100);
    
    return {
        absolute,
        percent,
        isIncrease: absolute > 0,
        isDecrease: absolute < 0,
    };
}

// Get placeholder image
function getPlaceholderImage() {
    return 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23f0f0f0" width="200" height="200"/%3E%3Ctext fill="%23999" font-family="sans-serif" font-size="18" x="50%25" y="50%25" text-anchor="middle" dominant-baseline="middle"%3ENo Image%3C/text%3E%3C/svg%3E';
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
