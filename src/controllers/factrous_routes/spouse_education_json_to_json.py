import json
import re


def extract_spouse_education_table(input_path: str, output_path: str, label_key: str) -> None:
    """
    Extracts structured key-value pairs from a JSON table of spouse's education levels and
    outputs them as flattened SCREAMING_SNAKE_CASE keys with associated point values.

    Replaces empty or "N/A" values with 0 and keeps both spouse/without-spouse fields.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    converted = {}

    def normalize_key(k: str) -> str:
        return k.replace('\u00A0', ' ').strip()

    for row in data:
        row_normalized = {normalize_key(k): v for k, v in row.items()}

        label = row_normalized.get(label_key)
        if not label:
            print(f"Warning: missing label in row: {row}")
            continue

        with_spouse_key = next((k for k in row_normalized if "With spouse" in k), None)
        without_spouse_key = next((k for k in row_normalized if "Without spouse" in k), None)

        if not with_spouse_key or not without_spouse_key:
            print(f"Warning: missing spouse keys for: {label}")
            continue

        def normalize_value(value):
            if value in ("", "N/A", None):
                return 0
            try:
                return int(value)
            except (ValueError, TypeError):
                print(f"Warning: non-integer value found: {value}, defaulting to 0")
                return 0

        with_spouse_value = normalize_value(row_normalized[with_spouse_key])
        without_spouse_value = normalize_value(row_normalized[without_spouse_key])

        label_key_upper = re.sub(r'[^A-Z0-9]', '_', label.upper())
        label_key_upper = re.sub(r'_+', '_', label_key_upper).strip('_')

        converted[f"{label_key_upper}_WITH_SPOUSE"] = with_spouse_value
        converted[f"{label_key_upper}_WITHOUT_SPOUSE"] = without_spouse_value

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(converted, f, indent=2)


if __name__ == "__main__":
    extract_spouse_education_table(
        input_path="/workspaces/Chat-Immigration/assets/rules_factores/orginal_factores/www.canada.ca__en_immigration_refugees_citizenship_services_immigrate_canada_express_entry_check_score_crs_criteria_html_table_spouse.json",
        output_path="spouse_education_points_extracted.json",
        label_key="Spouse’s or common-law partner’s level of education"
    )
