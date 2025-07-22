import json
import re
from pathlib import Path

def extract_additional_points(input_path: str, output_path: str, label_key: str) -> None:
    """
    Extracts and flattens additional points from a JSON table.
    Converts label values into SCREAMING_SNAKE_CASE keys and handles missing values.
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
        label = normalize_key(row.get(label_key, ""))
        value = normalize_value(row.get("Maximum 600 points", 0))

        label_key_upper = re.sub(r'[^A-Z0-9]', '_', label.upper())
        label_key_upper = re.sub(r'_+', '_', label_key_upper).strip('_')

        converted[label_key_upper] = value

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(converted, f, indent=2)

if __name__ == "__main__":
    extract_additional_points(
        input_path="path/to/input.json",
        output_path="extracted_additional_points.json",
        label_key="Additional points"
    )
