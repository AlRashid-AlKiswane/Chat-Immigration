

from pydantic import BaseModel, Field

class ScrabingTables(BaseModel):
    """
    Model for validating website scrabing requests.

    Attributes:
        url: The starting URL for the web scrabing (must be a valid HTTP/HTTPS URL)
        max_pages: Maximum number of pages to scrabing (1-1000)

    Examples:
        >>> valid_request = scrabingRequest(url="https://example.com", max_pages=10)
        >>> invalid_request = scrabingRequest(url="not-a-url", max_pages=0)
            # Will raise ValidationError
    """
    url: str = Field(
        ...,
        description="The starting URL for the web scrabing. Must include http:// or https://"
    )
    max_pages: int = Field(
        default=30,
        ge=1,
        le=1000,
        description="Maximum number of pages to scrabing (1-1000)"
    )
