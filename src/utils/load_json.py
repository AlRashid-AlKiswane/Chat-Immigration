"""
A module for safely loading JSON files with comprehensive error handling.

This module provides functionality to read and parse JSON files while handling
various error scenarios including file access issues, JSON parsing errors,
and permission problems. The main function `load_json_file` returns either
the parsed JSON data or detailed error information.

Functions:
    load_json_file: Load and parse a JSON file with full error handling.
"""

import json
import os
from typing import Union, Dict, List, Any, Tuple

def load_json_file(file_path: str) -> Tuple[bool, Union[Dict[str, Any], List[Any], str]]:
    """
    Load and parse a JSON file with comprehensive error handling.

    This function attempts to read a JSON file from the specified path, handling
    various error conditions that might occur during file access or parsing.

    Args:
        file_path (str): The path to the JSON file to be loaded.

    Returns:
        Tuple[bool, Union[Dict[str, Any], List[Any], str]]: A tuple where:
            - First element (bool): True if loading was successful, False otherwise
            - Second element: On success, returns the parsed JSON data (dict or list).
                              On failure, returns an error message string.

    Possible error scenarios handled:
        - File not found
        - Permission denied when accessing file
        - File is not valid JSON
        - File is empty
        - Other IO errors
        - JSON decoding errors

    Examples:
        >>> success, data = load_json_file('config.json')
        >>> if success:
        ...     print(data['key'])
        ... else:
        ...     print(f"Error: {data}")

        >>> success, data = load_json_file('nonexistent.json')
        >>> print(success, data)
        False, "File not found: 'nonexistent.json'"
    """
    # Check if file exists
    if not os.path.exists(file_path):
        return False, f"File not found: '{file_path}'"

    # Check if path points to a file (not directory)
    if not os.path.isfile(file_path):
        return False, f"Path is not a file: '{file_path}'"

    # Check file readability
    if not os.access(file_path, os.R_OK):
        return False, f"Permission denied: Cannot read file '{file_path}'"

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Check if file is empty
            if os.stat(file_path).st_size == 0:
                return False, f"Empty JSON file: '{file_path}'"

            try:
                json_data = json.load(file)
                return True, json_data
            except json.JSONDecodeError as e:
                return False, f"Invalid JSON in file '{file_path}': {str(e)}"
            except UnicodeDecodeError as e:
                return False, f"Encoding error in file '{file_path}': {str(e)}"

    except IOError as e:
        return False, f"I/O error while reading '{file_path}': {str(e)}"
    except Exception as e:
        return False, f"Unexpected error loading '{file_path}': {str(e)}"
