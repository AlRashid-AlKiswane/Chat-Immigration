"""
Crawl Request Schema Module

This module defines the Pydantic model for validating website crawl requests.
It ensures that incoming crawl requests have properly formatted URLs and
reasonable limits for the maximum number of pages to crawl.

The schema serves as both documentation and validation for the API endpoint,
providing clear expectations for request parameters.
"""

from pydantic import BaseModel, HttpUrl, Field

class CrawlRequest(BaseModel):
    """
    Model for validating website crawl requests.

    Attributes:
        url: The starting URL for the web crawl (must be a valid HTTP/HTTPS URL)
        max_pages: Maximum number of pages to crawl (1-1000)

    Examples:
        >>> valid_request = CrawlRequest(url="https://example.com", max_pages=10)
        >>> invalid_request = CrawlRequest(url="not-a-url", max_pages=0)
            # Will raise ValidationError
    """
    url: str = Field(
        ...,
        description="The starting URL for the web crawl. Must include http:// or https://"
    )
    max_pages: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of pages to crawl (1-1000)"
    )
