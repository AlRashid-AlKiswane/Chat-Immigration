"""
Logging module for application-wide logging with colored output.

This module provides a centralized logging system with full log levels:
- INFO (blue)
- DEBUG (green)
- WARNING (yellow)
- ERROR (red)
- CRITICAL (magenta)

Logs are saved to 'app.log' in the logs directory and include logger names.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os
import sys

# Setup main project directory path
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    print(f"Failed to set up main directory path: {e}")
    sys.exit(1)

# Log level to ANSI color mapping
COLORS = {
    "DEBUG": "\033[92m",    # Green
    "INFO": "\033[94m",     # Blue
    "WARNING": "\033[93m",  # Yellow
    "ERROR": "\033[91m",    # Red
    "CRITICAL": "\033[95m", # Magenta
    "END": "\033[0m",       # Reset
}


class ColoredFormatter(logging.Formatter):
    """
    Formatter that colors the entire log line based on level.
    """
    def format(self, record):
        message = super().format(record)
        color = COLORS.get(record.levelname, "")
        return f"{color}{message}{COLORS['END']}"


def setup_logging(
    name: str = "logger_app",
    log_dir: str = f"{MAIN_DIR}/logs",
    log_file: str = "app.log",
    console_level: int = logging.DEBUG,
) -> logging.Logger:
    """
    Set up logging configuration with colored console output and rotating file logging.

    Args:
        name (str): Name of the logger.
        log_dir (str): Directory to store log files.
        log_file (str): Name of the log file.
        console_level (int): Console log level (e.g., logging.DEBUG).

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger__ = logging.getLogger(name)
    logger__.setLevel(logging.DEBUG)

    # Always clear existing handlers to avoid duplicates and ensure formatter is applied
    if logger__.hasHandlers():
        logger__.handlers.clear()

    logger__.propagate = False

    # Ensure log directory exists
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_path = Path(log_dir) / log_file

    # Formatter string
    formatter_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Console handler (with color)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(ColoredFormatter(formatter_str))
    logger__.addHandler(console_handler)

    # Rotating file handler (without color)
    file_handler = RotatingFileHandler(log_path, maxBytes=100_000_000_000_000, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(formatter_str))
    logger__.addHandler(file_handler)

    return logger__


# Example usage when run as a script
def log_examples():
    logger = setup_logging("TEST")
    logger.debug("This is a debug message - detailed technical information.")
    logger.info("This is an info message - general application flow.")
    logger.warning("This is a warning message - something unexpected happened.")
    logger.error("This is an error message - something failed.")
    logger.critical("This is a critical message - application might crash.")


if __name__ == "__main__":
    log_examples()
