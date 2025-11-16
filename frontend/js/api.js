// API Client for PriceScout Backend

const API_BASE_URL = 'http://localhost:8000';

const api = {
    // Search products
    async searchProducts(site, query) {
        const response = await fetch(`${API_BASE_URL}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ site, query }),
        });
        
        if (!response.ok) {
            throw new Error(`Search failed: ${response.statusText}`);
        }
        
        return await response.json();
    },

    // Get all tracked products
    async getTrackedProducts() {
        const response = await fetch(`${API_BASE_URL}/track`);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch tracked products: ${response.statusText}`);
        }
        
        return await response.json();
    },

    // Get product details
    async getProduct(productId) {
        const response = await fetch(`${API_BASE_URL}/track/${productId}`);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch product: ${response.statusText}`);
        }
        
        return await response.json();
    },

    // Get product price history
    async getPriceHistory(productId) {
        const response = await fetch(`${API_BASE_URL}/track/product/${productId}/history`);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch price history: ${response.statusText}`);
        }
        
        return await response.json();
    },

    // Track a new product
    async trackProduct(url) {
        const response = await fetch(`${API_BASE_URL}/track`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url }),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to track product');
        }
        
        return await response.json();
    },

    // Set price alert
    async setAlert(productId, targetPrice) {
        const response = await fetch(`${API_BASE_URL}/track/${productId}/alert`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ target_price: targetPrice }),
        });
        
        if (!response.ok) {
            throw new Error('Failed to set alert');
        }
        
        return await response.json();
    },

    // Clear price alert
    async clearAlert(productId) {
        const response = await fetch(`${API_BASE_URL}/track/${productId}/alert`, {
            method: 'DELETE',
        });
        
        if (!response.ok) {
            throw new Error('Failed to clear alert');
        }
        
        return await response.json();
    },
};
