"""
Website Table Scraper Module

Extracts HTML tables from web pages, converts them to JSON format,
and saves them as separate JSON files.

Features:
- Extract tables from internal pages of a domain
- Save tables in structured JSON files
- Robust logging and error handling
"""
import os
import sys
import json
import io
import logging # Remove logging
from urllib.parse import urljoin, urlparse
from collections import deque

import requests
import pandas as pd
from bs4 import BeautifulSoup


# Project setup
# pylint: disable=wrong-import-position
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except Exception as e:
    logging.error(f"Setup failed: {e}")
    sys.exit(1)

# Custom imports
from src.logs.logger import setup_logging
from src.helpers import get_settings, Settings

logger = setup_logging()
app_settings: Settings = get_settings()

class TableScraper:
    """Scraper for extracting HTML tables from websites and converting them into JSON."""

    def __init__(self, start_url: str, max_pages: int = 30 ,  folder_name : str ="table"):
        self.start_url = start_url
        self.max_pages = max_pages
        self.visited = set()
        self.to_visit = deque([start_url])
        self.queued = set([start_url])
        self.domain = urlparse(start_url).netloc
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; TableScraper/1.0)"
        }
        self.output_dir = os.path.join(app_settings.DOC_LOCATION_SAVE,folder_name)

        try:
            os.makedirs(self.output_dir, exist_ok=True)
            print(f"Saving tables to: {self.output_dir}")
        except Exception as e:
            print(f"Failed to create table output directory: {e}")
            raise

    def crawl_and_scrape_tables(self) -> int:
        """Crawl pages and extract tables.

        Returns:
            Total number of tables extracted and saved
        """
        total_tables = 0
        logger.info(f"Starting crawl at: {self.start_url}")

        while self.to_visit and len(self.visited) < self.max_pages:
            url = self.to_visit.popleft()

            if url in self.visited:
                continue

            try:
                logger.info(f"Requesting URL: {url}")
                response = requests.get(url, headers=self.headers, timeout=10)

                if response.status_code != 200:
                    logger.warning(f"Failed to fetch {url} - Status: {response.status_code}")
                    continue

                soup = BeautifulSoup(response.text, "html.parser")
                self.visited.add(url)

                table_count = self._extract_and_save_tables(url, soup)
                total_tables += table_count
                logger.info(f"{table_count} table(s) saved from {url}")

                self._queue_internal_links(url, soup)

            except Exception as e:
                logger.error(f"Failed to process {url}: {e}")
                continue

        logger.info(f"Completed scraping. Total tables saved: {total_tables}")
        return total_tables

    def _queue_internal_links(self, base_url: str, soup: BeautifulSoup) -> None:
        for tag in soup.find_all("a", href=True):
            href = tag.get("href")
            if href.startswith(("#", "mailto:", "javascript:")):
                continue

            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)

            if parsed.netloc != self.domain:
                continue

            normalized_url = parsed.scheme + "://" + parsed.netloc + parsed.path
            if normalized_url not in self.visited and normalized_url not in self.queued:
                self.to_visit.append(normalized_url)
                self.queued.add(normalized_url)

    def _extract_and_save_tables(self, url: str, soup: BeautifulSoup) -> int:
        tables = soup.find_all("table")
        count = 0

        for i, table in enumerate(tables):
            try:
                df = pd.read_html(io.StringIO(str(table)), flavor='bs4')[0]
                json_data = self._convert_table_to_json(df)
                filename = self._generate_filename(url, i)

                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)

                count += 1
            except Exception as e:
                logger.warning(f"Failed to parse/save table {i} from {url}: {e}")
                continue

        return count

    def _convert_table_to_json(self, df: pd.DataFrame):
        """
        Convert any pandas DataFrame table to JSON structure:
        - If DataFrame has column headers (not default 0,1,2...), convert to list of dicts.
        - Otherwise, convert to list of lists.
        """
        df = df.fillna("")

        # Check if df columns are default integer indexes or meaningful headers
        if all(isinstance(col, int) for col in df.columns):
            # No meaningful header; return list of rows as lists
            return df.values.tolist()
        else:
            # Has headers; convert rows to list of dicts
            return df.to_dict(orient="records")

    def _generate_filename(self, url: str, index: int) -> str:
        safe_url = "".join(c if c.isalnum() else "_" for c in urlparse(url).path)
        base = f"{self.domain}_{safe_url or 'home'}_table_{index}.json"
        return os.path.join(self.output_dir, base)


if __name__ == "__main__":
    try:
        target_url = "https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/check-score/crs-criteria.html"
        scraper = TableScraper(start_url=target_url, max_pages=1 ,folder_name="tables")
        total = scraper.crawl_and_scrape_tables()
        logger.info(f"Scraping finished. Total tables saved: {total}")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)      