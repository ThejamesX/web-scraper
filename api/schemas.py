"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional


# Product Schemas
class ProductBase(BaseModel):
    """Base product schema."""
    url: str = Field(
        ...,
        description="The URL of the product page",
        examples=["https://www.alza.cz/samsung-galaxy-s23-d7654321.htm"],
        min_length=10,
        max_length=2048
    )


class ProductCreate(ProductBase):
    """Schema for creating a new product to track."""
    pass


class ProductOut(BaseModel):
    """Schema for product output with full details."""
    
    id: int = Field(..., description="Unique product identifier")
    url: str = Field(..., description="Product page URL")
    name: str = Field(..., description="Product name")
    eshop: str = Field(..., description="E-shop name (e.g., 'alza')")
    last_known_price: Optional[float] = Field(
        None,
        description="Last known price in CZK",
        examples=[12999.00]
    )
    last_check_time: datetime = Field(..., description="Timestamp of last price check")
    is_tracked: bool = Field(..., description="Whether the product is actively tracked")
    
    # Sale tracking fields
    is_on_sale: bool = Field(default=False, description="Whether the product is currently on sale")
    original_price: Optional[float] = Field(
        None,
        description="Original price before discount (if on sale)",
        examples=[15999.00]
    )
    
    # Price alert fields
    alert_price: Optional[float] = Field(
        None,
        description="User-defined target price for alert",
        examples=[10999.00]
    )
    alert_triggered: bool = Field(default=False, description="Whether price alert has been triggered")
    
    model_config = {"from_attributes": True}


# Price History Schemas
class PriceHistoryOut(BaseModel):
    """Schema for price history output."""
    
    price: float = Field(..., description="Price in CZK", examples=[12999.00])
    timestamp: datetime = Field(..., description="When the price was recorded")
    
    # Sale tracking fields
    is_on_sale: bool = Field(default=False, description="Whether the product was on sale at this time")
    original_price: Optional[float] = Field(
        None,
        description="Original price before discount (if on sale)",
        examples=[15999.00]
    )
    
    model_config = {"from_attributes": True}


# Search Schemas
class SearchQuery(BaseModel):
    """Schema for product search query."""
    
    site: str = Field(
        ...,
        description="E-commerce site to search (currently supports: 'alza')",
        examples=["alza"],
        min_length=1
    )
    query: str = Field(
        ...,
        description="Search query text",
        examples=["Samsung Galaxy S23", "iPhone 15", "laptop"],
        min_length=2,
        max_length=200
    )


class SearchResultItem(BaseModel):
    """Schema for a single search result item."""
    
    name: str = Field(..., description="Product name", examples=["Samsung Galaxy S23 256GB"])
    price: float = Field(..., description="Product price in CZK", examples=[22990.00])
    product_url: str = Field(
        ...,
        description="Direct URL to the product page",
        examples=["https://www.alza.cz/samsung-galaxy-s23-d7654321.htm"]
    )
    image_url: Optional[str] = Field(
        None,
        description="URL to the product image",
        examples=["https://cdn.alza.cz/Foto/f10/RI/RI123.jpg"]
    )
    
    # Sale tracking fields
    is_on_sale: bool = Field(default=False, description="Whether the product is on sale")
    original_price: Optional[float] = Field(
        None,
        description="Original price before discount (if on sale)",
        examples=[25990.00]
    )


class SearchResponse(BaseModel):
    """Schema for search results response."""
    
    query: str = Field(..., description="The search query that was executed")
    site: str = Field(..., description="The e-commerce site that was searched")
    results: list[SearchResultItem] = Field(
        ...,
        description="List of search results (up to 10 items)"
    )


# Alert Schemas
class AlertCreate(BaseModel):
    """Schema for creating/updating a price alert."""
    
    target_price: float = Field(
        ...,
        description="Target price to trigger alert",
        examples=[9999.00],
        gt=0
    )


class AlertResponse(BaseModel):
    """Schema for alert operation response."""
    
    status: str = Field(..., description="Status of the operation", examples=["success"])
    item: ProductOut = Field(..., description="Updated product with alert information")
