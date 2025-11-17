"""Search endpoint for product discovery."""

import logging
from fastapi import APIRouter, Depends, HTTPException
from api.schemas import SearchQuery, SearchResponse
from scraper.service import ScraperService, get_scraper_service

router = APIRouter(prefix="/search", tags=["search"])
logger = logging.getLogger(__name__)


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
    # Validate and sanitize search query
    sanitized_query = search_query.query.strip()
    
    if not sanitized_query:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty or contain only whitespace."
        )
    
    # Validate supported sites
    supported_sites = ["alza"]
    if search_query.site.lower() not in supported_sites:
        raise HTTPException(
            status_code=400,
            detail=f"Site '{search_query.site}' is not supported. Supported sites: {', '.join(supported_sites)}"
        )
    
    try:
        logger.info(f"Searching {search_query.site} for: {sanitized_query}")
        
        results = await scraper.search_site(
            site=search_query.site.lower(),
            query=sanitized_query,
            limit=10
        )
        
        logger.info(f"Found {len(results)} results for query: {sanitized_query}")
        
        return SearchResponse(
            query=sanitized_query,
            site=search_query.site.lower(),
            results=results
        )
    except ValueError as e:
        # User-friendly error messages from the scraper service
        logger.warning(f"Search validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Unexpected errors - log and provide a helpful message
        logger.error(f"Unexpected error during search: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while searching. Please try again later."
        )
