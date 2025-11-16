"""Core configuration module for PriceScout API."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str = "sqlite+aiosqlite:///./pricescout.db"
    
    # API Configuration
    api_title: str = "PriceScout API"
    api_version: str = "1.0.0"
    api_description: str = "E-commerce product search and price tracking API"
    
    # Scheduler Configuration
    price_check_interval_hours: int = 4
    
    # Scraper Configuration
    scraper_timeout: int = 30000
    scraper_headless: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
