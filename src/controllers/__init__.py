"""
controller package

This package contains all core controller modules responsible for processing,
extracting, and transforming immigration rule data from diverse sources such
as JSON files, HTML tables, and web pages. These modules handle structured
extraction, normalization, and preparation of rule data for downstream
consumption by scoring models and other components of the system.

Modules included:
- `file_preprocessing`: Generates unique filenames to avoid overwrites.
- `docs_to_chunks`: Loads documents and splits them into manageable chunks.
- `web_scraping`: Crawls websites and extracts relevant content.
- `table_scraping`: Extracts tabular data from HTML pages.
- Extraction modules (e.g. `age_extraction_json_to_json`, 
  `education_extraction_json_to_json`, etc.): Convert raw scraped JSON tables 
  into clean, structured formats based on scoring categories.

Main categories of extractors:
- Core human factors: Age, education, languages, work experience.
- Spouse factors: Education, languages, and work experience.
- Combination factors: Education + language, Canadian + foreign work experience.
- Additional points: Certificates and other bonus point sources.

This centralized import exposes all controller functionality in one namespace.
"""

from .file_preprocessing import generate_unique_filename
from .docs_to_chunks import load_and_chunk
from .web_scraping import WebsiteCrawler
from .table_scraping import TableScraper

from .age_extraction_json_to_json import extract_age_json
from .education_extraction_json_to_json import extract_education_table
from .first_languageextraction_json_to_json import extract_language_table
from .second_language_json_to_json import extract_second_language_table
from .canadian_work_experience_json_to_json import extract_key_value_table
from .spouse_education_json_to_json import extract_spouse_education_table
from .spouse_language_json_to_json import extract_spouse_language_table
from .spouse_work_json_to_json import extract_spouse_work_table
from .additional_json_to_json import extract_additional_points
from .language_education_json_to_json import extract_language_education_points
from .work_education_json_to_json import extract_canadian_work_edu_points
from .foreign_work_language_json_to_json import extract_foreign_work_language_points
from .foreign_canadian_work_json_to_json import extract_foreign_canadian_work_points
from .certificate_of_qualification_json_to_json import extract_certificate_of_qualification
from .score_to_clb import convert_score_to_clb

__all__ = [
    "generate_unique_filename",
    "load_and_chunk",
    "WebsiteCrawler",
    "TableScraper",
    "extract_age_json",
    "extract_education_table",
    "extract_language_table",
    "extract_second_language_table",
    "extract_key_value_table",
    "extract_spouse_education_table",
    "extract_spouse_language_table",
    "extract_spouse_work_table",
    "extract_additional_points",
    "extract_language_education_points",
    "extract_canadian_work_edu_points",
    "extract_foreign_work_language_points",
    "extract_foreign_canadian_work_points",
    "extract_certificate_of_qualification",
    "convert_score_to_clb",
]
