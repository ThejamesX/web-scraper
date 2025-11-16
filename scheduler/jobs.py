"""Background jobs for scheduled tasks."""

from datetime import datetime, timezone
from sqlalchemy import select
from db import AsyncSessionLocal
from db.models import Product, PriceHistory
from scraper.service import get_scraper_service


async def check_all_product_prices():
    """
    Background job to check prices for all tracked products.
    
    This function:
    1. Gets all products where is_tracked=True
    2. Fetches current price for each product
    3. Compares with last_known_price
    4. If different, creates new PriceHistory entry and updates product
    """
    async with AsyncSessionLocal() as db:
        try:
            # Get all tracked products
            result = await db.execute(
                select(Product).where(Product.is_tracked == True)
            )
            products = result.scalars().all()
            
            if not products:
                print("No products to check")
                return
            
            # Get scraper service
            scraper = await get_scraper_service()
            
            for product in products:
                try:
                    print(f"Checking price for: {product.name} ({product.url})")
                    
                    # Fetch current product details
                    details = await scraper.fetch_product_details(product.url)
                    current_price = details["price"]
                    is_on_sale = details.get("is_on_sale", False)
                    original_price = details.get("original_price")
                    
                    # Update last check time
                    product.last_check_time = datetime.now(timezone.utc)
                    
                    # Update sale status
                    product.is_on_sale = is_on_sale
                    product.original_price = original_price
                    
                    # Check if price has changed
                    if product.last_known_price != current_price:
                        print(f"Price changed: {product.last_known_price} -> {current_price}")
                        
                        # Create new price history entry
                        price_entry = PriceHistory(
                            product_id=product.id,
                            price=current_price,
                            timestamp=datetime.now(timezone.utc),
                            is_on_sale=is_on_sale,
                            original_price=original_price
                        )
                        db.add(price_entry)
                        
                        # Update product's last known price
                        product.last_known_price = current_price
                    else:
                        print(f"Price unchanged: {current_price}")
                    
                    # Check if price alert should be triggered
                    if product.alert_price is not None and not product.alert_triggered:
                        if current_price <= product.alert_price:
                            print(f"Alert triggered! Price {current_price} <= target {product.alert_price}")
                            product.alert_triggered = True
                    
                except Exception as e:
                    print(f"Error checking product {product.id}: {str(e)}")
                    # Continue with next product even if one fails
                    continue
            
            # Commit all changes
            await db.commit()
            print("Price check completed")
            
        except Exception as e:
            print(f"Error in price check job: {str(e)}")
            await db.rollback()
