"""
chat history mangment
"""

import asyncio
import time
import os
import sys
import logging
from functools import lru_cache
from typing import Literal,Optional, List, Dict, Awaitable

from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage


# Set up main directory path
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
# pylint: disable=logging-format-interpolation

from src.logs.logger import setup_logging
from src.schema import ProviderChatHistory






logger = setup_logging()