import warnings
import logging
from logging.handlers import RotatingFileHandler  # Optional for file rotation

# Suppress specific warnings
warnings.filterwarnings(
    "ignore",
    message='directory "/run/secrets" does not exist',
    category=UserWarning,
)

# Create logger
logger = logging.getLogger('app_logger')
logger.propagate = False  # Prevent duplicate logs
logger.setLevel(logging.DEBUG)  # Set minimum log level to capture
