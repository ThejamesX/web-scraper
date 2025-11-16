// Category Management with LocalStorage

const CATEGORIES_STORAGE_KEY = 'pricescout_categories';
const PRODUCT_CATEGORIES_KEY = 'pricescout_product_categories';

// Category Manager
const categoryManager = {
    // Get all categories
    getCategories() {
        const stored = localStorage.getItem(CATEGORIES_STORAGE_KEY);
        return stored ? JSON.parse(stored) : [];
    },

    // Save categories
    saveCategories(categories) {
        localStorage.setItem(CATEGORIES_STORAGE_KEY, JSON.stringify(categories));
    },

    // Create a new category
    createCategory(name) {
        const categories = this.getCategories();
        const newCategory = {
            id: Date.now(),
            name,
            createdAt: new Date().toISOString(),
            productIds: [],
        };
        categories.push(newCategory);
        this.saveCategories(categories);
        return newCategory;
    },

    // Delete category
    deleteCategory(categoryId) {
        const categories = this.getCategories();
        const filtered = categories.filter(c => c.id !== categoryId);
        this.saveCategories(filtered);
        
        // Also remove product associations
        const productCategories = this.getProductCategories();
        Object.keys(productCategories).forEach(productId => {
            productCategories[productId] = productCategories[productId].filter(
                cId => cId !== categoryId
            );
        });
        this.saveProductCategories(productCategories);
    },

    // Get product-category mapping
    getProductCategories() {
        const stored = localStorage.getItem(PRODUCT_CATEGORIES_KEY);
        return stored ? JSON.parse(stored) : {};
    },

    // Save product-category mapping
    saveProductCategories(mapping) {
        localStorage.setItem(PRODUCT_CATEGORIES_KEY, JSON.stringify(mapping));
    },

    // Add product to category
    addProductToCategory(productId, categoryId) {
        const categories = this.getCategories();
        const category = categories.find(c => c.id === categoryId);
        
        if (category && !category.productIds.includes(productId)) {
            category.productIds.push(productId);
            this.saveCategories(categories);
        }

        const productCategories = this.getProductCategories();
        if (!productCategories[productId]) {
            productCategories[productId] = [];
        }
        if (!productCategories[productId].includes(categoryId)) {
            productCategories[productId].push(categoryId);
            this.saveProductCategories(productCategories);
        }
    },

    // Remove product from category
    removeProductFromCategory(productId, categoryId) {
        const categories = this.getCategories();
        const category = categories.find(c => c.id === categoryId);
        
        if (category) {
            category.productIds = category.productIds.filter(id => id !== productId);
            this.saveCategories(categories);
        }

        const productCategories = this.getProductCategories();
        if (productCategories[productId]) {
            productCategories[productId] = productCategories[productId].filter(
                id => id !== categoryId
            );
            this.saveProductCategories(productCategories);
        }
    },

    // Get categories for a product
    getCategoriesForProduct(productId) {
        const productCategories = this.getProductCategories();
        const categoryIds = productCategories[productId] || [];
        const allCategories = this.getCategories();
        return allCategories.filter(c => categoryIds.includes(c.id));
    },

    // Get products in a category
    getProductsInCategory(categoryId) {
        const categories = this.getCategories();
        const category = categories.find(c => c.id === categoryId);
        return category ? category.productIds : [];
    },
};

// Show category modal
function showCategoryModal() {
    const modal = document.getElementById('category-modal');
    modal.style.display = 'flex';
}

// Close category modal
function closeCategoryModal() {
    const modal = document.getElementById('category-modal');
    modal.style.display = 'none';
    document.getElementById('category-form').reset();
}

// Handle category form submission
document.getElementById('category-form').addEventListener('submit', (e) => {
    e.preventDefault();
    
    const nameInput = document.getElementById('category-name');
    const name = nameInput.value.trim();
    
    if (name) {
        try {
            categoryManager.createCategory(name);
            showToast('Category created successfully', 'success');
            closeCategoryModal();
            loadCategories();
        } catch (error) {
            showToast('Failed to create category', 'error');
        }
    }
});

// Load categories page
async function loadCategories() {
    const container = document.getElementById('categories-grid');
    const categories = categoryManager.getCategories();
    
    if (categories.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📂</div>
                <h3>No Categories Yet</h3>
                <p>Create categories to organize your tracked products</p>
                <button class="btn-primary" onclick="showCategoryModal()">Create Category</button>
            </div>
        `;
        return;
    }

    // Get tracked products to count items in each category
    let trackedProducts = [];
    try {
        trackedProducts = await api.getTrackedProducts();
    } catch (error) {
        console.error('Error loading products:', error);
    }

    container.innerHTML = categories.map(category => {
        const productCount = category.productIds.length;
        const productsInCategory = trackedProducts.filter(p => 
            category.productIds.includes(p.id)
        );
        
        return `
            <div class="category-card" data-category-id="${category.id}">
                <div class="category-card__header">
                    <h3 class="category-card__title">${category.name}</h3>
                    <button class="btn-small btn-secondary" onclick="event.stopPropagation(); deleteCategory(${category.id})">
                        Delete
                    </button>
                </div>
                <div class="category-card__count">${productCount} product${productCount !== 1 ? 's' : ''}</div>
                ${productsInCategory.length > 0 ? `
                    <div style="margin-top: var(--spacing-md);">
                        ${productsInCategory.slice(0, 3).map(p => `
                            <div style="font-size: var(--font-size-sm); color: var(--color-text-secondary); margin-bottom: var(--spacing-xs);">
                                • ${p.name.substring(0, 40)}${p.name.length > 40 ? '...' : ''}
                            </div>
                        `).join('')}
                        ${productsInCategory.length > 3 ? `<div style="font-size: var(--font-size-sm); color: var(--color-text-tertiary);">and ${productsInCategory.length - 3} more...</div>` : ''}
                    </div>
                ` : '<div style="color: var(--color-text-tertiary); font-size: var(--font-size-sm);">No products in this category</div>'}
            </div>
        `;
    }).join('');
}

// Delete category
function deleteCategory(categoryId) {
    if (confirm('Are you sure you want to delete this category?')) {
        categoryManager.deleteCategory(categoryId);
        showToast('Category deleted', 'success');
        loadCategories();
    }
}

// Show category selector for a product
function showCategorySelector(productId) {
    const categories = categoryManager.getCategories();
    const productCategories = categoryManager.getCategoriesForProduct(productId);
    
    if (categories.length === 0) {
        showToast('Create a category first', 'error');
        navigateTo('categories');
        return;
    }

    const selectedIds = productCategories.map(c => c.id);
    
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Add to Categories</h3>
                <button class="modal-close" onclick="this.closest('.modal').remove()">✕</button>
            </div>
            <div style="margin-bottom: var(--spacing-lg);">
                ${categories.map(cat => `
                    <label style="display: flex; align-items: center; gap: var(--spacing-sm); padding: var(--spacing-sm); cursor: pointer;">
                        <input type="checkbox" value="${cat.id}" 
                            ${selectedIds.includes(cat.id) ? 'checked' : ''}
                            onchange="toggleProductCategory(${productId}, ${cat.id}, this.checked)">
                        <span>${cat.name}</span>
                    </label>
                `).join('')}
            </div>
            <div class="modal-actions">
                <button class="btn-primary" onclick="this.closest('.modal').remove()">Done</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    modal.style.display = 'flex';
}

// Toggle product in category
function toggleProductCategory(productId, categoryId, add) {
    if (add) {
        categoryManager.addProductToCategory(productId, categoryId);
        showToast('Added to category', 'success');
    } else {
        categoryManager.removeProductFromCategory(productId, categoryId);
        showToast('Removed from category', 'success');
    }
}
