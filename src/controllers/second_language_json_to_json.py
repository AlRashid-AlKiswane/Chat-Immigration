import json
import re


def extract_second_language_table(input_path: str, output_path: str, label_key: str) -> None:
    """
    Extracts structured key-value pairs from a JSON table of CLB language benchmarks and
    outputs them as flattened SCREAMING_SNAKE_CASE keys with associated point values.

    Args:
        input_path (str): Path to the input JSON file.
        output_path (str): Path to write the transformed JSON output.
        label_key (str): The field name used for row identifiers, e.g., "Canadian Language Benchmark (CLB) level per ability".
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

        with_spouse_key = next((k for k in row_normalized if "With a spouse" in k), None)
        without_spouse_key = next((k for k in row_normalized if "Without a spouse" in k), None)

        if not with_spouse_key or not without_spouse_key:
            print(f"Warning: missing spouse keys for: {label}")
            continue

        with_spouse = row_normalized[with_spouse_key]
        without_spouse = row_normalized[without_spouse_key]

        label_key_upper = re.sub(r'[^A-Z0-9]', '_', label.upper())
        label_key_upper = re.sub(r'_+', '_', label_key_upper).strip('_')

        converted[f"{label_key_upper}_WITH_SPOUSE"] = with_spouse
        converted[f"{label_key_upper}_WITHOUT_SPOUSE"] = without_spouse

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(converted, f, indent=2)


if __name__ == "__main__":
    extract_second_language_table(
        input_path="/workspaces/Chat-Immigration/assets/rules_factores/orginal_factores/www.canada.ca__en_immigration_refugees_citizenship_services_immigrate_canada_express_entry_check_score_crs_criteria_html_table_4.json",  
        output_path="second_language_points_extracted.json",
        label_key="Canadian Language Benchmark (CLB) level per ability"
    )
