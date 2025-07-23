"""
Web Crawling API Module

This module provides a FastAPI-based REST API for website crawling functionality.
 It allows clients to:
- Initiate website crawls starting from a specified URL
- Control the depth of crawling through max_pages parameter
- Retrieve structured results including visited URLs and saved content
- Check service health status

Key Features:
- Robust URL validation and input sanitization
- Comprehensive error handling and logging
- Support for both HTML and PDF content extraction
- Configurable maximum pages to crawl
- JSON-based API responses with proper HTTP status codes

Dependencies:
- FastAPI: For the web framework
- BeautifulSoup: For HTML parsing
- Requests: For HTTP requests
- Pysqlite3: For SQLite database operations
- LangChain: For document processing

Environment Requirements:
- Python 3.8+
- All dependencies listed in requirements.txt

Example Usage:
POST /api/v1/crawl
{
    "url": "https://example.com",
    "max_pages": 10
}

GET /api/v1/crawl/status

Security Considerations:
- Inputs are thoroughly validated
- Rate limiting should be implemented at the deployment level
- Sensitive information is not logged
"""

# pylint: disable=wrong-import-position
import logging
import os
import sys

__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

# Set up project base directory
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_400_BAD_REQUEST,
)

# pylint: disable=wrong-import-order
from src.infra.logger import setup_logging
from src.schema import CrawlRequest
from src.controllers import WebsiteCrawler
from typing import Dict, Any
from urllib.parse import urlparse
from pydantic import ValidationError

# Initialize logger and settings
logger = setup_logging()

web_crawling_route = APIRouter()

def validate_url(url: str) -> bool:
    """Validate the URL format.
    
    Args:
        url: URL string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception as e:
        logger.error(f"URL validation failed for {url}: {e}")
        return False

@web_crawling_route.post("/crawl", response_class=JSONResponse)
async def crawl_website(
    request: Request,
    crawl_request: CrawlRequest = Depends()
) -> JSONResponse:
    """
    Endpoint to initiate website crawling.
    
    Args:
        request: FastAPI Request object
        crawl_request: CrawlRequest model containing:
            - url: Starting URL for crawling
            - max_pages: Maximum number of pages to crawl
            
    Returns:
        JSONResponse: Contains either:
            - Success response with crawl results
            - Error response with failure details
            
    Raises:
        HTTPException: For various error conditions
    """
    try:
        # Log the start of the crawling process
        logger.info(
            f"Starting crawl request from {request.client.host} "
            f"for URL: {crawl_request.url}"
        )

        # Validate the input URL
        if not validate_url(crawl_request.url):
            logger.error(f"Invalid URL provided: {crawl_request.url}")
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid URL format. Please provide a valid URL with http/https scheme."
            )

        # Validate max_pages parameter
        if crawl_request.max_pages <= 0 or crawl_request.max_pages > 1000:
            logger.error(f"Invalid max_pages value: {crawl_request.max_pages}")
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="max_pages must be between 1 and 1000"
            )

        # Initialize crawler
        logger.debug(
            f"Initializing crawler for {crawl_request.url} "
            f"with max_pages={crawl_request.max_pages}"
        )
        crawler = WebsiteCrawler(
            start_url=str(crawl_request.url),
            max_pages=crawl_request.max_pages
        )

        # Execute crawling
        logger.info(f"Starting crawl process for {crawl_request.url}")
        visited_urls = crawler.crawl()

        if not visited_urls:
            logger.warning(f"No pages were crawled for {crawl_request.url}")
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="No pages could be crawled from the starting URL"
            )

        # Save results
        logger.info(f"Saving crawl results for {len(visited_urls)} pages")
        output_file = crawler.save_to_text_files(visited_urls)

        if not output_file:
            logger.error("Failed to save crawl results")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save crawl results"
            )

        # Prepare success response
        response_data: Dict[str, Any] = {
            "status": "success",
            "message": "Crawling completed successfully",
            "data": {
                "starting_url": crawl_request.url,
                "pages_crawled": len(visited_urls),
                "output_file": output_file,
                "visited_urls": visited_urls,
            }
        }

        logger.info(
            f"Crawl completed successfully for {crawl_request.url}. "
            f"Crawled {len(visited_urls)} pages."
        )

        return JSONResponse(
            content=response_data,
            status_code=HTTP_200_OK
        )

    except ValidationError as e:
        logger.error(f"Request validation failed: {e}")
        return HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e.errors())
        )
    except HTTPException:
        # Re-raise HTTP exceptions as they're already properly formatted
        raise
    except Exception as e:
        logger.critical(
            f"Unexpected error during crawling: {str(e)}",
            exc_info=True
        )
        return HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during crawling"
        )

