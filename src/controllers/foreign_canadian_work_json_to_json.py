import json
import logging
from typing import Any

logger = logging.getLogger("EXTRACT_FOREIGN_CANADIAN_WORK")


def extract_foreign_canadian_work_points(input_path: str, output_path: str, label_key: str) -> None:
    with open(input_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    mapped_data: dict[str, Any] = {}

    for row in raw_data:
        label = row.get(label_key, "").strip().upper()

        points_1yr = row.get("Points for foreign work experience + 1 year of Canadian work experience (Maximum 25 points)", 0)
        points_2yrs = row.get("Points for foreign work experience + 2 years or more of Canadian work experience (Maximum 50 points)", 0)

        if "NO FOREIGN" in label:
            mapped_data["NO_FOREIGN_WORK_EXPERIENCE_CANADIAN_1YR"] = points_1yr
            mapped_data["NO_FOREIGN_WORK_EXPERIENCE_CANADIAN_2YRS"] = points_2yrs
        elif "1 OR 2 YEARS" in label:
            mapped_data["ONE_OR_TWO_YEARS_FOREIGN_WORK_CANADIAN_1YR"] = points_1yr
            mapped_data["ONE_OR_TWO_YEARS_FOREIGN_WORK_CANADIAN_2YRS"] = points_2yrs
        elif "3 YEARS" in label:
            mapped_data["THREE_YEARS_OR_MORE_FOREIGN_WORK_CANADIAN_1YR"] = points_1yr
            mapped_data["THREE_YEARS_OR_MORE_FOREIGN_WORK_CANADIAN_2YRS"] = points_2yrs

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(mapped_data, f, indent=2)

    logger.info("Foreign+Canadian work experience points extracted to: %s", output_path)
