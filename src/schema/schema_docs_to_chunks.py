

from pydantic import BaseModel, Field
from typing import List


class ChunkData(BaseModel):
    chunks: List[str] = Field(..., description="List of text chunks from the document")
    pages: List[int] = Field(..., description="List of page numbers for each chunk")
    sources: List[str] = Field(..., description="List of source file paths or names for each chunk")
    authors: List[str] = Field(..., description="List of authors for each chunk")
