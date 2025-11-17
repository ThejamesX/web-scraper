"""Search endpoint for product discovery."""

from fastapi import APIRouter, Depends, HTTPException
from api.schemas import SearchQuery, SearchResponse
from scraper.service import ScraperService, get_scraper_service

router = APIRouter(prefix="/search", tags=["search"])


@router.post(
    "",
    response_model=SearchResponse,
    summary="Search for products",
    description="Search an e-commerce site for products matching a query. Returns up to 10 results."
)
async def search_products(
    search_query: SearchQuery,
    scraper: ScraperService = Depends(get_scraper_service)
):
    """
    Search for products on an e-commerce site.
    
    Args:
        search_query: Search parameters (site and query text)
        scraper: Scraper service dependency
        
    Returns:
        SearchResponse: Search results with up to 10 products
        
    Raises:
        HTTPException: If search fails or site is not supported
    """
    try:
        results = await scraper.search_site(
            site=search_query.site,
            query=search_query.query,
            limit=10
        )
        
        return SearchResponse(
            query=search_query.query,
            site=search_query.site,
            results=results
        )
    except ValueError as e:
        # User-friendly error messages from the scraper service
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Unexpected errors - provide a helpful message
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while searching. Please try again later. Error: {str(e)}"
        )
