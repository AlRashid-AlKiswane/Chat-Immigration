"""
Website Crawler Module

This module provides functionality to crawl websites, extract content from HTML pages and PDFs,
and save the extracted text to files. It uses LangChain for document processing and BeautifulSoup
for HTML parsing.

Features:
- Crawl websites up to a specified depth
- Handle both HTML and PDF content
- Save extracted text to organized files
- Comprehensive logging and error handling
"""

import logging
import os
import sys
from collections import deque
from urllib.parse import urljoin, urlparse
import tempfile
from typing import List, Optional

import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import PyPDFLoader

# Constants and Setup
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
from src.logs.logger import setup_logging
from src.helpers import get_settings, Settings

# Initialize application settings and logger
app_settings: Settings = get_settings()
logger = setup_logging()


class WebsiteCrawler:
    """A web crawler that extracts text content from websites and PDFs.

    Attributes:
        start_url (str): The URL to start crawling from
        max_pages (int): Maximum number of pages to crawl
        visited (set): Set of visited URLs
        to_visit (deque): Queue of URLs to visit
        queued (set): Set of URLs already in queue
        domain (str): Domain of the start URL
        headers (dict): HTTP headers for requests
        app_settings (Settings): Application configuration
        doc_dir (str): Directory to save extracted documents
    """

    def __init__(self, start_url: str, max_pages: int = 100):
        """Initialize the WebsiteCrawler.

        Args:
            start_url: URL to start crawling from
            max_pages: Maximum number of pages to crawl (default: 100)
        """
        self.start_url = start_url
        self.max_pages = max_pages
        self.visited = set()
        self.to_visit = deque([start_url])
        self.queued = set([start_url])
        self.domain = urlparse(start_url).netloc
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; WebCrawler/1.0; +https://example.com/bot)"
        }
        self.app_settings: Settings = get_settings()
        self.doc_dir = self.app_settings.DOC_LOCATION_SAVE

        try:
            os.makedirs(self.doc_dir, exist_ok=True)
            logger.info(f"Created document directory at {self.doc_dir}")
        except OSError as e:
            logger.error(f"Failed to create document directory: {e}")
            raise

    def crawl(self) -> List[str]:
        """Crawl the website starting from the initial URL.

        Returns:
            List of visited URLs

        Raises:
            RuntimeError: If crawling fails due to network issues
        """
        logger.info(f"Starting crawl from {self.start_url} with max {self.max_pages} pages")

        try:
            while self.to_visit and len(self.visited) < self.max_pages:
                url = self.to_visit.popleft()

                if url in self.visited:
                    logger.debug(f"Skipping already visited URL: {url}")
                    continue

                try:
                    logger.info(f"Processing URL: {url}")
                    response = requests.get(url, headers=self.headers, timeout=10)

                    if response.status_code != 200:
                        logger.warning(f"Non-200 status at {url}: {response.status_code}")
                        continue

                    soup = BeautifulSoup(response.text, "html.parser")
                    self.visited.add(url)
                    logger.debug(f"Successfully parsed {url}")

                    # Extract and queue new links
                    new_links = self._extract_links(url, soup)
                    logger.debug(f"Found {new_links} new links at {url}")

                except requests.RequestException as e:
                    logger.error(f"Network error visiting {url}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error processing {url}: {e}")
                    continue

            logger.info(f"Crawling finished. Visited {len(self.visited)} pages.")
            return list(self.visited)

        except Exception as e:
            logger.critical(f"Crawling failed: {e}")
            raise RuntimeError(f"Crawling failed: {e}") from e

    def _extract_links(self, base_url: str, soup: BeautifulSoup) -> int:
        """Extract and queue links from a page.

        Args:
            base_url: URL of the current page
            soup: BeautifulSoup object of the page

        Returns:
            Number of new links found
        """
        new_links = 0
        for link_tag in soup.find_all("a", href=True):
            href = link_tag.get("href")
            if not href or href.startswith(("#", "mailto:", "javascript:")):
                continue

            try:
                full_url = urljoin(base_url, href)
                parsed = urlparse(full_url)

                if parsed.netloc != self.domain:
                    logger.debug(f"Skipping external link: {full_url}")
                    continue

                norm_url = parsed.scheme + "://" + parsed.netloc + parsed.path
                if norm_url not in self.visited and norm_url not in self.queued:
                    self.to_visit.append(norm_url)
                    self.queued.add(norm_url)
                    new_links += 1
                    logger.debug(f"Queued new URL: {norm_url}")

            except Exception as e:
                logger.warning(f"Error processing link {href}: {e}")

        return new_links

    def save_to_text_files(self, all_pages: List[str]) -> Optional[str]:
        """Save extracted content from all pages to a text file.

        Args:
            all_pages: List of URLs to process

        Returns:
            Path to the saved file if successful, None otherwise

        Raises:
            ValueError: If no pages were provided
            IOError: If file writing fails
        """
        if not all_pages:
            logger.error("No pages provided for saving")
            raise ValueError("No pages provided for saving")

        logger.info(f"Starting to process {len(all_pages)} pages for text extraction")
        text_chunks = []

        for i, url in enumerate(all_pages, 1):
            try:
                logger.info(f"Processing page {i}/{len(all_pages)}: {url}")

                if url.lower().endswith(".pdf"):
                    text = self._process_pdf(url)
                else:
                    text = self._process_html(url)

                if text:
                    section_header = f"\n--- Page {i}: {url} ---\n"
                    text_chunks.append(section_header + text)
                    logger.debug(f"Successfully processed {url}")

            except Exception as e:
                logger.error(f"Failed to process {url}: {e}")
                continue

        if not text_chunks:
            logger.error("No content was extracted from any pages")
            return None

        try:
            url_name = self._sanitize_filename(self.start_url)
            output_file = os.path.join(self.doc_dir, f"{url_name}.txt")

            logger.info(f"Writing extracted content to {output_file}")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n\n".join(text_chunks))

            logger.info(f"Successfully saved content to {output_file}")
            return output_file

        except IOError as e:
            logger.error(f"Failed to write output file: {e}")
            raise

    def _process_pdf(self, url: str) -> Optional[str]:
        """Process a PDF URL and extract text.

        Args:
            url: URL of the PDF

        Returns:
            Extracted text if successful, None otherwise
        """
        try:
            logger.info(f"Downloading PDF: {url}")
            response = requests.get(url, timeout=15)

            if response.status_code != 200:
                logger.error(f"Failed to download PDF {url}: HTTP {response.status_code}")
                return None

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name

            try:
                loader = PyPDFLoader(tmp_file_path)
                docs = loader.load()
                text = "\n".join(doc.page_content for doc in docs)
                logger.debug(f"Extracted {len(text)} characters from PDF")
                return text
            finally:
                os.remove(tmp_file_path)
                logger.debug(f"Removed temporary PDF file {tmp_file_path}")

        except Exception as e:
            logger.error(f"Error processing PDF {url}: {e}")
            return None

    def _process_html(self, url: str) -> Optional[str]:
        """Process an HTML URL and extract text.

        Args:
            url: URL of the HTML page

        Returns:
            Extracted text if successful, None otherwise
        """
        try:
            logger.debug(f"Downloading HTML: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code != 200:
                logger.error(f"Non-200 status at {url}: {response.status_code}")
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove unwanted elements
            for tag in soup(["header", "footer", "nav", "script", "style", "iframe", "noscript"]):
                tag.decompose()

            body = soup.body.get_text(separator="\n", strip=True) if soup.body else ""
            logger.debug(f"Extracted {len(body)} characters from HTML")
            return body

        except Exception as e:
            logger.error(f"Error processing HTML {url}: {e}")
            return None

    @staticmethod
    def _sanitize_filename(url: str) -> str:
        """Sanitize URL to create a safe filename.

        Args:
            url: URL to sanitize

        Returns:
            Sanitized filename string
        """
        return "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in url)


if __name__ == "__main__":
    try:
        logger.info("Starting website crawler")
        base_url = "https://en.wikipedia.org/wiki/Machine_learning"

        crawler = WebsiteCrawler(start_url=base_url, max_pages=50)
        all_pages = crawler.crawl()

        if all_pages:
            output_file = crawler.save_to_text_files(all_pages)
            logger.info(f"Crawling completed. Results saved to {output_file}")
            print(f"Found {len(all_pages)} internal pages. Output saved to {output_file}")
        else:
            logger.warning("No pages were crawled")
            print("No pages were crawled.")

    except Exception as e:
        logger.critical(f"Application failed: {e}", exc_info=True)
        print(f"An error occurred: {e}")
        sys.exit(1)
