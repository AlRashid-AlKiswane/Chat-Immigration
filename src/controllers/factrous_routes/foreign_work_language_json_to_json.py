import json
import logging
from typing import Any

logger = logging.getLogger("EXTRACT_FOREIGN_WORK_LANG")

def extract_foreign_work_language_points(input_path: str, output_path: str, label_key: str) -> None:
    with open(input_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    mapped_data: dict[str, Any] = {}

    for row in raw_data:
        label = row.get(label_key, "").strip().upper()

        if label == "NO FOREIGN WORK EXPERIENCE":
            mapped_data["NO_FOREIGN_WORK_EXPERIENCE_CLB7"] = row.get("Points for foreign work experience + CLB 7 or more on all first official language abilities, one or more under 9 (Maximum 25 points)", 0)
            mapped_data["NO_FOREIGN_WORK_EXPERIENCE_CLB9"] = row.get("Points for foreign work experience + CLB 9 or more on all four first official language abilities (Maximum 50 points)", 0)
        elif "1 OR 2 YEARS" in label:
            mapped_data["ONE_OR_TWO_YEARS_OF_FOREIGN_WORK_EXPERIENCE_CLB7"] = row.get("Points for foreign work experience + CLB 7 or more on all first official language abilities, one or more under 9 (Maximum 25 points)", 0)
            mapped_data["ONE_OR_TWO_YEARS_OF_FOREIGN_WORK_EXPERIENCE_CLB9"] = row.get("Points for foreign work experience + CLB 9 or more on all four first official language abilities (Maximum 50 points)", 0)
        elif "3 YEARS" in label:
            mapped_data["THREE_YEARS_OR_MORE_OF_FOREIGN_WORK_EXPERIENCE_CLB7"] = row.get("Points for foreign work experience + CLB 7 or more on all first official language abilities, one or more under 9 (Maximum 25 points)", 0)
            mapped_data["THREE_YEARS_OR_MORE_OF_FOREIGN_WORK_EXPERIENCE_CLB9"] = row.get("Points for foreign work experience + CLB 9 or more on all four first official language abilities (Maximum 50 points)", 0)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(mapped_data, f, indent=2)

    logger.info("Extraction complete. Output saved to: %s", output_path)
