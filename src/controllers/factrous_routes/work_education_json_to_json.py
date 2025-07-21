import json
import re
from pathlib import Path

def extract_canadian_work_edu_points(input_path: str, output_path: str, label_key: str) -> None:
    """
    Extracts Canadian work experience + education combination points
    and creates SCREAMING_SNAKE_CASE keys with associated 1YR/2YR point values.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    converted = {}

    def normalize_key(k: str) -> str:
        return k.replace('\u00A0', ' ').strip()

    def normalize_value(value) -> int:
        if value in ("", "N/A", None):
            return 0
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0

    for row in data:
        row = {normalize_key(k): v for k, v in row.items()}
        label = normalize_key(row.get(label_key, ""))

        one_year_value = normalize_value(row.get(
            "Points for education + 1 year of Canadian work experience (Maximum 25 points)", 0))
        two_years_value = normalize_value(row.get(
            "Points for education + 2 years or more of Canadian work experience (Maximum 50 points)", 0))

        label_key_upper = re.sub(r'[^A-Z0-9]', '_', label.upper())
        label_key_upper = re.sub(r'_+', '_', label_key_upper).strip('_')

        converted[f"{label_key_upper}_1YR"] = one_year_value
        converted[f"{label_key_upper}_2YR"] = two_years_value

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(converted, f, indent=2)

if __name__ == "__main__":
    extract_canadian_work_edu_points(
        input_path="path/to/input.json",
        output_path="extracted_canadian_work_edu_points.json",
        label_key="With Canadian work experience and a post-secondary degree"
    )
