"""
Document Processing Module

This module provides functionality to load and chunk documents (PDF/text) using LangChain.
It handles document loading, text splitting, and metadata extraction.

Features:
- Supports PDF and text file formats
- Configurable chunking parameters
- Comprehensive error handling and logging
"""

import logging
import os
import sys
from typing import Any, Dict, Optional
from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Set up main directory path
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
# pylint: disable=logging-format-interpolation

from src.logs.logger import setup_logging
from src.helpers import get_settings, Settings
from src.enums import DocToChunksMsg

# Initialize application settings and logger
app_settings: Settings = get_settings()
logger = setup_logging()


def load_and_chunk(file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load text or PDF documents and split them into chunks using LangChain's text splitter.

    Args:
        file_path: Optional single file path to process. If not provided,
                  all valid files in the configured directory will be used.

    Returns:
        Dictionary containing document chunks and associated metadata.
        Returns empty dictionary on failure.

    Raises:
        OSError: For file system related errors
        RuntimeError: For document processing errors
    """
    total_chunks = 0
    all_chunks = []

    # Determine which files to process
    if file_path:
        files_to_process = [file_path]
    else:
        try:
            files_to_process = [
                os.path.join(app_settings.DOC_LOCATION_SAVE, f)
                for f in os.listdir(app_settings.DOC_LOCATION_SAVE)
                if Path(f).suffix.lower().lstrip(".") in app_settings.FILE_TYPES
            ]
        except OSError as e:
            logger.error(DocToChunksMsg.DIRECTORY_ERROR.value, e)
            return {}
        except Exception as e:  # pylint: disable=broad-except
            logger.error(DocToChunksMsg.UNEXPECTED_LISTING_ERROR.value, e)
            return {}

    if not files_to_process:
        logger.warning(DocToChunksMsg.NO_FILES_WARNING.value)
        return {}

    # Process each file
    for file in files_to_process:
        try:
            extension = Path(file).suffix.lower().lstrip(".")
            loader = None

            if extension in app_settings.FILE_TYPES:
                try:
                    loader = PyMuPDFLoader(file)
                    logger.debug(DocToChunksMsg.PDF_LOAD_SUCCESS.value, file)
                except RuntimeError as e:
                    logger.warning(DocToChunksMsg.PDF_LOAD_FAILURE.value, e)
                    try:
                        loader = TextLoader(file)
                        logger.debug(DocToChunksMsg.FALLBACK_TEXT_LOAD.value, file)
                    except RuntimeError as e:
                        logger.error(DocToChunksMsg.TEXT_LOAD_FAILURE.value, e)
                        continue
            else:
                logger.debug(DocToChunksMsg.UNSUPPORTED_TYPE.value, extension)
                continue

            documents = loader.load()

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=app_settings.CHUNKS_SIZE,
                chunk_overlap=app_settings.CHUNKS_OVERLAP,
            )

            chunks = splitter.split_documents(documents)
            all_chunks.extend(chunks)
            total_chunks += len(chunks)
            logger.info(DocToChunksMsg.CHUNKING_SUCCESS.value, len(chunks), file)

        except RuntimeError as e:
            logger.error(DocToChunksMsg.PROCESSING_ERROR.value, file, e)
        except Exception as e:  # pylint: disable=broad-except
            logger.error(DocToChunksMsg.UNEXPECTED_ERROR.value, file, e)

    if not all_chunks:
        logger.warning(DocToChunksMsg.NO_CHUNKS_WARNING.value)
        return {}

    try:
        data = {
            "chunks": [doc.page_content for doc in all_chunks],
            "pages": [doc.metadata.get("page", -1) for doc in all_chunks],
            "sources": [doc.metadata.get("source", "") for doc in all_chunks],
            "authors": [doc.metadata.get("author", "") for doc in all_chunks],
        }
        return data
    except (AttributeError, KeyError) as e:
        logger.error(DocToChunksMsg.OUTPUT_ERROR.value, e)
        return {}
