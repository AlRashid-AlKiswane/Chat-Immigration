

import json
import re

def exteact_age_json(input_path, output_path):
    # Read the input JSON file
    with open(input_path, 'r') as f:
        data = json.load(f)
    
    # Create a dictionary to store the new key-value pairs
    converted_data = {}
    
    for item in data:
        age = item['Age']
        # Handle both regular space and non-breaking space cases
        with_spouse = item.get('With a spouse or common-law partner (Maximum 100 points)') or \
                     item.get('With a spouse or common-law partner (Maximum 100 points)')
        without_spouse = item.get('Without a spouse or common-law partner (Maximum 110 points)') or \
                       item.get('Without a spouse or common-law partner (Maximum 110 points)')
        
        if with_spouse is None or without_spouse is None:
            print(f"Warning: Could not find point values for age group: {age}")
            continue
        
        # Convert age description to uppercase and replace spaces/special characters
        age_key = age.upper()
        age_key = re.sub(r'[^A-Z0-9]', '_', age_key)
        age_key = re.sub(r'_+', '_', age_key)
        age_key = age_key.strip('_')
        
        # Create keys for with and without spouse
        key_with = f"{age_key}_WITH_SPOUSE"
        key_without = f"{age_key}_WITHOUT_SPOUSE"
        
        # Add to the converted data
        converted_data[key_with] = with_spouse
        converted_data[key_without] = without_spouse
    
    # Write the converted data to a new JSON file
    with open(output_path, 'w') as f:
        json.dump(converted_data, f, indent=2)



if __name__ == "__main__":
    # Example usage:
    exteact_age_json('/workspaces/Chat-Immigration/assets/docs/table/www.canada.ca__en_immigration_refugees_citizenship_services_immigrate_canada_express_entry_check_score_crs_criteria_html_table_1.json', 'output.json')
