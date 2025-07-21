import json
import re
from pathlib import Path

def extract_language_education_points(input_path: str, output_path: str, label_key: str) -> None:
    """
    Extracts combined education + language skill factors and creates SCREAMING_SNAKE_CASE keys
    with associated CLB7/CLB9 point values.
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

    label_key = normalize_key(label_key)

    for row in data:
        row = {normalize_key(k): v for k, v in row.items()}

        label = normalize_key(row.get(label_key, ""))

        clb7_value = normalize_value(row.get(
            "Points for CLB 7 or more on all first official language abilities, with one or more under CLB 9 (Maximum 25 points)", 0))
        clb9_value = normalize_value(row.get(
            "Points for CLB 9 or more on all four first official language abilities (Maximum 50 points)", 0))

        label_key_upper = re.sub(r'[^A-Z0-9]', '_', label.upper())
        label_key_upper = re.sub(r'_+', '_', label_key_upper).strip('_')

        converted[f"{label_key_upper}_CLB7"] = clb7_value
        converted[f"{label_key_upper}_CLB9"] = clb9_value

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(converted, f, indent=2)

if __name__ == "__main__":
    extract_language_education_points(
        input_path="path/to/input.json",
        output_path="extracted_language_education_points.json",
        label_key="With good official language proficiency (Canadian Language Benchmark Level [CLB] 7 or higher) and a post-secondary degree"
    )
