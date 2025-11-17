"""Database models for PriceScout API."""

from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class Product(Base):
    """Product model for tracking e-commerce products."""
    
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    eshop: Mapped[str] = mapped_column(String, nullable=False, index=True)
    last_known_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_check_time: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    is_tracked: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    
    # Sale tracking fields
    is_on_sale: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    original_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Price alert fields
    alert_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    alert_triggered: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    # Relationship to price history
    price_history: Mapped[List["PriceHistory"]] = relationship(
        "PriceHistory",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    
    # Composite indexes for common query patterns
    __table_args__ = (
        Index('ix_products_tracked_sale', 'is_tracked', 'is_on_sale'),
        Index('ix_products_tracked_alert', 'is_tracked', 'alert_triggered'),
    )


class PriceHistory(Base):
    """Price history model for tracking price changes over time."""
    
    __tablename__ = "price_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Sale tracking fields
    is_on_sale: Mapped[bool] = mapped_column(Boolean, default=False)
    original_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Relationship to product
    product: Mapped["Product"] = relationship("Product", back_populates="price_history")
