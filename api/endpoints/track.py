"""Track endpoint for product price tracking."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.schemas import ProductCreate, ProductOut, PriceHistoryOut, AlertCreate, AlertResponse
from db import get_db
from db.models import Product, PriceHistory
from scraper.service import ScraperService, get_scraper_service

router = APIRouter(prefix="/track", tags=["tracking"])


@router.post(
    "",
    response_model=ProductOut,
    summary="Start tracking a product",
    description="Add a new product URL to track. Fetches initial product details and price.",
    status_code=201
)
async def track_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    scraper: ScraperService = Depends(get_scraper_service)
):
    """
    Start tracking a product by URL.
    
    Args:
        product_data: Product data with URL
        db: Database session
        scraper: Scraper service dependency
        
    Returns:
        ProductOut: Created product with details
        
    Raises:
        HTTPException: If product already exists or fetching fails
    """
    # Check if product already exists
    result = await db.execute(
        select(Product).where(Product.url == product_data.url)
    )
    existing_product = result.scalar_one_or_none()
    
    if existing_product:
        raise HTTPException(
            status_code=400,
            detail=f"This product is already being tracked. You can view it in your dashboard."
        )
    
    # Fetch product details
    try:
        details = await scraper.fetch_product_details(product_data.url)
    except ValueError as e:
        # User-friendly error from scraper
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to fetch product information. Please verify the URL is correct and try again. Error: {str(e)}"
        )
    
    # Determine e-shop from URL
    eshop = "unknown"
    if "alza.cz" in product_data.url:
        eshop = "alza"
    
    # Create new product
    new_product = Product(
        url=product_data.url,
        name=details["name"],
        eshop=eshop,
        last_known_price=details["price"],
        last_check_time=datetime.now(timezone.utc),
        is_tracked=True,
        is_on_sale=details.get("is_on_sale", False),
        original_price=details.get("original_price")
    )
    
    db.add(new_product)
    await db.flush()  # Get the product ID
    
    # Create initial price history entry
    price_entry = PriceHistory(
        product_id=new_product.id,
        price=details["price"],
        timestamp=datetime.now(timezone.utc),
        is_on_sale=details.get("is_on_sale", False),
        original_price=details.get("original_price")
    )
    db.add(price_entry)
    
    await db.commit()
    await db.refresh(new_product)
    
    return new_product


@router.get(
    "/product/{product_id}/history",
    response_model=list[PriceHistoryOut],
    summary="Get product price history",
    description="Retrieve the price history for a tracked product."
)
async def get_product_history(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get price history for a product.
    
    Args:
        product_id: Product ID
        db: Database session
        
    Returns:
        list[PriceHistoryOut]: List of price history entries
        
    Raises:
        HTTPException: If product not found
    """
    # Get product with price history
    result = await db.execute(
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.price_history))
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID {product_id} not found. Unable to retrieve price history."
        )
    
    # Sort price history by timestamp (newest first)
    history = sorted(
        product.price_history,
        key=lambda x: x.timestamp,
        reverse=True
    )
    
    return history


@router.get(
    "",
    response_model=list[ProductOut],
    summary="Get all tracked products",
    description="Retrieve all products that are being tracked."
)
async def get_tracked_products(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all tracked products.
    
    Args:
        db: Database session
        
    Returns:
        list[ProductOut]: List of all tracked products
    """
    result = await db.execute(
        select(Product).where(Product.is_tracked == True)
    )
    products = result.scalars().all()
    return products


@router.get(
    "/{product_id}",
    response_model=ProductOut,
    summary="Get product details",
    description="Get details of a specific tracked product including all fields."
)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get product details.
    
    Args:
        product_id: Product ID
        db: Database session
        
    Returns:
        ProductOut: Product details
        
    Raises:
        HTTPException: If product not found
    """
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID {product_id} not found in your tracked products."
        )
    
    return product


@router.put(
    "/{product_id}/alert",
    response_model=AlertResponse,
    summary="Set price alert",
    description="Set or update a price alert for a tracked product."
)
async def set_price_alert(
    product_id: int,
    alert_data: AlertCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Set or update price alert for a product.
    
    Args:
        product_id: Product ID
        alert_data: Alert configuration with target price
        db: Database session
        
    Returns:
        AlertResponse: Success status and updated product
        
    Raises:
        HTTPException: If product not found
    """
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID {product_id} not found. Unable to set price alert."
        )
    
    # Update alert settings
    product.alert_price = alert_data.target_price
    # Reset alert triggered flag when setting a new alert
    product.alert_triggered = False
    
    await db.commit()
    await db.refresh(product)
    
    return AlertResponse(
        status="success",
        item=product
    )


@router.delete(
    "/{product_id}/alert",
    summary="Clear price alert",
    description="Remove the price alert for a tracked product."
)
async def clear_price_alert(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Clear price alert for a product.
    
    Args:
        product_id: Product ID
        db: Database session
        
    Returns:
        dict: Success status
        
    Raises:
        HTTPException: If product not found
    """
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID {product_id} not found. Unable to clear price alert."
        )
    
    # Clear alert settings
    product.alert_price = None
    product.alert_triggered = False
    
    await db.commit()
    
    return {"status": "success"}
