import os
import re
import sys
import json
import logging
import tqdm
from pathlib import Path
from typing import Dict, Any, List

# Ensure project path setup
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("❌ Failed to set up main directory path: %s", e, exc_info=True)
    sys.exit(1)

# Project-specific imports
from src.logs import setup_logging
from src.helpers import get_settings, Settings

# Setup base logger and config
logger = setup_logging(name="JSONBatchLoader")
app_settings: Settings = get_settings()




class JSONBatchLoader:
    """
    Loads multiple JSON files from a given directory and optionally exports them
    to `.py` rule constants based on recognizable column labels.
    """

    def __init__(self, data_dir: str, file_indices: List[int]):
        self.data_dir = data_dir
        self.file_indices = file_indices
        self.prefix = (
            "www.canada.ca__en_immigration_refugees_citizenship_services_"
            "immigrate_canada_express_entry_check_score_crs_criteria_html_table_"
        )
        self.suffix = ".json"

    def load_json_files(self) -> Dict[str, Any]:
        """
        Load multiple JSON files into a single dictionary keyed by table index.
        """
        combined_data = {}
        logger.info("📂 Starting to load JSON files...")

        for index in tqdm.tqdm(self.file_indices, desc="Loading JSON files", unit="file"):
            filename = f"{self.prefix}{index}{self.suffix}"
            filepath = os.path.join(self.data_dir, filename)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    combined_data[f"table_{index}"] = data
            except FileNotFoundError:
                logger.warning(f"⚠️ File not found: {filename}")
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON decode error in {filename}: {e}")
            except Exception as e:
                logger.exception(f"❌ Unexpected error loading {filename}: {e}")

        logger.info("✅ Finished loading all JSON files.")
        return combined_data

    def export_rules(
        self,
        combined_data: Dict[str, Any],
        output_dir: str,
        file_prefix: str = ".rules_"
    ) -> None:
        """
        Convert JSON table rows into Python constant `.py` files per category.
        """
        os.makedirs(output_dir, exist_ok=True)

        for table_name, rows in combined_data.items():
            if not isinstance(rows, list) or not rows:
                continue

            keys = rows[0].keys()
            category_key = next(
                (k for k in keys if k.lower() in ["age", "factors", "education", "experience"]),
                None
            )

            if not category_key:
                logger.warning(f"⚠️ Skipping {table_name}, no recognized category key.")
                continue

            filename = f"{file_prefix}{category_key.lower().replace(' ', '_')}"
            filepath = os.path.join(output_dir, filename)

            lines = ["# Auto-generated rule constants\n"]

            for row in rows:
                label = row.get(category_key, "").upper().strip()
                label = self._normalize_label(label)

                for col_key, val in row.items():
                    if col_key == category_key or not isinstance(val, (int, float)):
                        continue

                    col_norm = self._normalize_label(col_key)
                    const_name = f"{category_key.upper()}_{label}_{col_norm}"
                    const_name = re.sub(r"__+", "_", const_name).strip("_")
                    lines.append(f"{const_name}={val}")

            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))
                logger.info(f"✅ Saved Python rules: {filepath}")
            except Exception as e:
                logger.exception(f"❌ Failed to write {filepath}: {e}")

    @staticmethod
    def _normalize_label(label: str) -> str:
        """
        Convert text into a safe UPPER_CASE variable name.
        """
        label = label.replace("(", "").replace(")", "")
        label = label.replace("\u00a0", " ")
        label = re.sub(r"[^\w\s]", "", label)
        label = label.replace("-", " ").replace("/", " ")
        label = label.replace(" or more", "_OR_MORE")
        label = label.replace(" to ", "_TO_")
        label = label.replace(" ", "_")
        return label.upper().strip("_")


class JSONModelSplitter:
    """
    Splits combined JSON data into individual `.json` files mapped to Pydantic class names.
    """

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def split(self, combined_data: Dict[str, Any]) -> None:
        """
        Write individual `.json` files for each model from combined table data.
        """
        mapping = {
            "AgeWithSpouseFactors": ("table_1", "Age", "With a spouse or common-law partner (Maximum 100 points)", None),
            "AgeWithoutSpouseFactors": ("table_1", "Age", None, "Without a spouse or common-law partner (Maximum 110 points)"),
            "EducationWithSpouseFactors": ("table_2", "Level of Education", "With a spouse or common-law partner (Maximum 140 points)", None),
            "EducationWithoutSpouseFactors": ("table_2", "Level of Education", None, "Without a spouse or common-law partner (Maximum 150 points)"),
            "FirstLanguageWithSpouseFirstLanguageWithoutSpouse": ("table_3", "Canadian Language Benchmark (CLB) level per ability",
                                                                  "With a spouse or common-law partner (Maximum 128 points)",
                                                                  "Without a spouse or common-law partner (Maximum 136 points)"),
            "SecondLanguageWithSpouse": ("table_4", "Canadian Language Benchmark (CLB) level per ability",
                                         "With a spouse or common-law partner (Maximum 22 points)", None),
            "SecondLanguageWithoutSpouse": ("table_4", "Canadian Language Benchmark (CLB) level per ability",
                                            None, "Without a spouse or common-law partner (Maximum 24 points)"),
            "CanadianWorkExperienceWithSpouse": ("table_5", "Canadian work experience",
                                                 "With a spouse or common-law partner (Maximum 70 points)", None),
            "CanadianWorkExperienceWithoutSpouse": ("table_5", "Canadian work experience",
                                                    None, "Without a spouse or common-law partner (Maximum 80 points)"),
            "SpouseEducationWithSpouse": ("table_7", "Spouse’s or common-law partner’s level of education",
                                          "With spouse or common-law partner (Maximum 10 points)", None),
            "SpouseLanguageWithSpouse": ("table_8", "Canadian Language Benchmark (CLB) level per ability (reading, writing, speaking and listening)",
                                         "Maximum 20 points for section  Maximum 5 points per ability", None),
            "SpouseWorkExperienceWithSpouse": ("table_9", "Spouse's Canadian work experience",
                                               "Maximum 10 points", None),
            "CertificateCLB5To6": ("table_17", "Certificate of qualification (trade occupations) – With good official language proficiency (Canadian Language Benchmark Level [CLB] 5 or higher)",
                                   "Points for certificate of qualification + CLB 5 or more on all first official language abilities, one or more under 7 (Maximum 25 points)", None),
            "CertificateCLB7Plus": ("table_17", "Certificate of qualification (trade occupations) – With good official language proficiency (Canadian Language Benchmark Level [CLB] 5 or higher)",
                                    "Points for certificate of qualification + CLB 7 or more on all four first official language abilities (Maximum 50 points)", None),
            "CanadianWorkExp1Year": ("table_14", "With Canadian work experience and a post-secondary degree",
                                     "Points for education + 1 year of Canadian work experience (Maximum 25 points)", None),
            "CanadianWorkExp2PlusYears": ("table_14", "With Canadian work experience and a post-secondary degree",
                                          "Points for education + 2 years or more of Canadian work experience (Maximum 50 points)", None),
            "TransferabilityEducationCLB7To8": ("table_10", "Education", "Points (Maximum 50 points)", None),
            "TransferabilityEducationCLB9Plus": ("table_13", "With good official language proficiency (Canadian Language Benchmark Level [CLB] 7 or higher) and a post-secondary degree",
                                                 "Points for CLB 9 or more on all four first official language abilities (Maximum 50 points)", None),
            "ForeignWith1YearCanadian": ("table_16", "Years of experience",
                                         "Points for foreign work experience + 1 year of Canadian work experience (Maximum 25 points)", None),
            "ForeignWith2PlusYearsCanadian": ("table_16", "Years of experience",
                                              "Points for foreign work experience + 2 years or more of Canadian work experience (Maximum 50 points)", None),
            "ForeignWorkExpCLB7To8": ("table_11", "Foreign work experience", "Points (Maximum 50 points)", None),
            "ForeignWorkExpCLB9Plus": ("table_15", "Years of experience",
                                       "Points for foreign work experience + CLB 9 or more on all four first official language abilities (Maximum 50 points)", None),
            "AdditionalPoints": ("table_19", "Additional points", "Maximum 600 points", None),
        }

        for class_name, (table_key, label_col, with_spouse_col, without_spouse_col) in mapping.items():
            table = combined_data.get(table_key, [])
            values = []

            for row in table:
                item = {"label": row.get(label_col, "")}
                if with_spouse_col and with_spouse_col in row:
                    item["points_with_spouse"] = row[with_spouse_col]
                if without_spouse_col and without_spouse_col in row:
                    item["points_without_spouse"] = row[without_spouse_col]
                if "points_with_spouse" in item or "points_without_spouse" in item:
                    values.append(item)

            output_file = self.output_dir / f"{class_name}.json"
            with output_file.open("w", encoding="utf-8") as out:
                json.dump(values, out, indent=4, ensure_ascii=False)
            logger.info(f"✅ Wrote model file: {output_file}")


def main():
    """
    CLI use case: Load multiple JSON files and export both .py rules and .json model files.
    """
    file_indices = list(range(20))
    data_directory = os.path.join(MAIN_DIR, "assets/docs/", "table/")
    rules_output_directory = os.path.join(MAIN_DIR, "assets/rules_python/")
    model_output_directory = Path(MAIN_DIR) / "assets/rules_json"

    # Load
    loader = JSONBatchLoader(data_dir=data_directory, file_indices=file_indices)
    combined_data = loader.load_json_files()

    # Export .py rules
    loader.export_rules(combined_data, output_dir=rules_output_directory)

    # Split into per-model JSON
    splitter = JSONModelSplitter(output_dir=model_output_directory)
    splitter.split(combined_data)


if __name__ == "__main__":
    main()
