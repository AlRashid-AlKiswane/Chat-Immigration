"""
Logging module for application-wide logging with colored output.

This module provides a centralized logging system with four log levels:
- INFO (blue)
- DEBUG (green)
- WARNING (yellow)
- ERROR (red)

Logs are saved to 'application.log' in the logs directory.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os
import sys

try:
    # Setup import path
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if not os.path.exists(MAIN_DIR):
        raise FileNotFoundError(f"Project directory not found at: {MAIN_DIR}")

    # Add to Python path only if it's not already there
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.helpers import get_settings, Settings

except ModuleNotFoundError as e:
    logging.error("Module not found: %s", e, exc_info=True)
except ImportError as e:
    logging.error("Import error: %s", e, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise

app_settings: Settings = get_settings()

# Define log colors
COLORS = {
    "INFO": "\033[94m",  # Blue
    "DEBUG": "\033[92m",  # Green
    "WARNING": "\033[93m",  # Yellow
    "ERROR": "\033[91m",  # Red
    "END": "\033[0m",  # Reset color
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log messages."""

    def format(self, record):
        """Format the log record with appropriate color."""
        levelname = record.levelname
        message = super().format(record)
        if levelname in COLORS:
            message = f"{COLORS[levelname]}{message}{COLORS['END']}"
        return message


def setup_logging(
    log_dir=f"{MAIN_DIR}/logs",
    log_file=app_settings.log_file,
    console_level=app_settings.log_level,
):
    """
    Set up logging configuration with colored console output and file logging.

    Args:
        log_dir (str): Directory to store log files. Defaults to 'logs'.
        log_file (str): Name of the log file. Defaults to 'application.log'.
        console_level (int): Minimum log level for console output. Defaults to DEBUG.

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Create logs directory if it doesn't exist
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_path = Path(log_dir) / log_file

    # Create logger
    logger__ = logging.getLogger("app_logger")
    logger__.setLevel(logging.DEBUG)  # Capture all levels at logger level

    # Prevent duplicate handlers
    if logger__.handlers:
        return logger__

    # Create formatters
    console_format = ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s")
    file_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Console handler (colored output)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)  # Now configurable
    console_handler.setFormatter(console_format)

    # File handler (all levels)
    file_handler = RotatingFileHandler(log_path, maxBytes=1024 * 1024, backupCount=5)
    file_handler.setLevel(logging.DEBUG)  # All levels to file
    file_handler.setFormatter(file_format)

    # Add handlers
    logger__.addHandler(console_handler)
    logger__.addHandler(file_handler)

    return logger__


# Initialize the logger when module is imported
logger = setup_logging(console_level=logging.DEBUG)  # Now shows DEBUG messages


# Example usage functions
def log_examples():
    """Demonstrate different log levels with sample messages."""
    logger.debug("This is a debug message - detailed technical information.")
    logger.info("This is an info message - general application flow.")
    logger.warning("This is a warning message - something unexpected happened.")
    logger.error("This is an error message - something failed.")


if __name__ == "__main__":
    log_examples()
