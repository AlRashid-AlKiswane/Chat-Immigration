"""
Route definition for crawling web pages and scraping HTML tables.

This module defines a FastAPI route that accepts a POST request with a starting URL
and maximum number of pages to crawl. It uses the `TableScraper` controller to extract
HTML tables from the crawled web pages and returns the total number of tables found.

Includes full error handling, logging, and validation.

Author: Rama Amairy
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

from fastapi import APIRouter, HTTPException
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
from src.schema import ScrabingTables
from src.controllers import TableScraper

from pydantic import ValidationError

# Initialize logger
logger = setup_logging()

tables_crawling_route = APIRouter()

@tables_crawling_route.post("/tables_crawling", response_class=JSONResponse)
async def tables_crawling(body: ScrabingTables) -> JSONResponse:
    """
    Endpoint to crawl web pages starting from a URL and scrape HTML tables.

    Args:
        body (ScrabingTables): A validated request body with `url` and `max_pages`.

    Returns:
        JSONResponse: A JSON response containing the number of scraped tables or an error message.
    """
    logger.info(
        "Received request to scrape tables from URL: %s | Max pages: %d", body.url, body.max_pages)

    try:
        scraper = TableScraper(start_url=body.url, max_pages=body.max_pages)
        total_tables = scraper.crawl_and_scrape_tables()

        if total_tables == 0:
            logger.warning("No tables were found for URL: %s", body.url)
            return JSONResponse(
                status_code=HTTP_404_NOT_FOUND,
                content={"detail": "No tables found on the provided pages."}
            )

        logger.info("Scraping completed. Total tables found: %d", total_tables)
        return JSONResponse(
            status_code=HTTP_200_OK,
            content={"total_tables_found": total_tables}
        )

    except ValidationError as ve:
        logger.error("Validation error during table scraping: %s", ve)
        return HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )

    except ValueError as ve:
        logger.error("Value error: %s", ve)
        return HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )

    except Exception as e:
        logger.exception("Unexpected error during table scraping: %s", e)
        return HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while scraping tables."
        )
