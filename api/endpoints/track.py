"""Track endpoint for product price tracking."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.schemas import ProductCreate, ProductOut, PriceHistoryOut
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
            detail="Product URL is already being tracked"
        )
    
    # Fetch product details
    try:
        details = await scraper.fetch_product_details(product_data.url)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch product details: {str(e)}"
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
        is_tracked=True
    )
    
    db.add(new_product)
    await db.flush()  # Get the product ID
    
    # Create initial price history entry
    price_entry = PriceHistory(
        product_id=new_product.id,
        price=details["price"],
        timestamp=datetime.now(timezone.utc)
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
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Sort price history by timestamp (newest first)
    history = sorted(
        product.price_history,
        key=lambda x: x.timestamp,
        reverse=True
    )
    
    return history
