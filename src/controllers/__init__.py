

from .file_preprocessing import generate_unique_filename
from .docs_to_chunks import load_and_chunk
from .web_scraping import WebsiteCrawler
from .table_scraping import TableScraper

from .factrous_routes import (extract_age_json,
                              extract_education_table,
                              extract_language_table,
                              extract_second_language_table,
                              extract_key_value_table,
                              extract_spouse_education_table,extract_spouse_language_table,
                              extract_spouse_work_table,
                              extract_additional_points,
                              extract_language_education_points,
                              extract_canadian_work_edu_points,
                              extract_foreign_work_language_points,
                              extract_foreign_canadian_work_points,extract_certificate_of_qualification)

