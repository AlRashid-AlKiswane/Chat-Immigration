"""
Module for preparing document chunks for database insertion.

This module provides functionality to transform extracted document chunks
into a format suitable for database insertion.
"""

from typing import Dict, List


def prepare_chunks_for_insertion(data: Dict[str, List[str]]) -> List[Dict[str, str]]:
    """
    Convert extracted chunks dict into a list of dictionaries ready for DB insertion.

    Args:
        data: Dictionary with keys 'chunks', 'pages', 'sources', 'authors'

    Returns:
        List of dictionaries with keys 'text', 'pages', 'sources', 'authors'
    """
    return [
        {
            "text": chunk,
            "pages": str(data["pages"][i]),
            "sources": data["sources"][i],
            "authors": data["authors"][i],
        }
        for i, chunk in enumerate(data["chunks"])
    ]
