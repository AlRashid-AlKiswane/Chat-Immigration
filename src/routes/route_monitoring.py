"""
System Monitoring API Module

This module provides endpoints for monitoring system resources including:
- Battery status
- CPU usage
- Disk usage
- Memory usage

The API returns standardized JSON responses with detailed system information.
"""

# pylint: disable=wrong-import-position
import logging
import os
import sys
from typing import Dict, Any

__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

# Set up project base directory
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

# pylint: disable=wrong-import-order
from src.infra.logger import setup_logging
from src.infra import DeviceMonitor

# Initialize logger and settings
logger = setup_logging()

monitoring_route = APIRouter()

@monitoring_route.get("/resources", response_class=JSONResponse)
async def get_system_resources() -> JSONResponse:
    """
    Get comprehensive system resource information
    
    Returns:
        JSONResponse: Contains system resource data including:
            - battery: Battery status information
            - cpu: CPU usage information
            - disk: Disk usage information
            - memory: Memory usage information
    
    Raises:
        HTTPException: If any monitoring operation fails
    """
    try:
        logger.info("Starting system resource monitoring")
        device_monitor = DeviceMonitor()

        resources: Dict[str, Any] = {
            "battery": device_monitor.get_battery_info(),
            "cpu": device_monitor.get_cpu_info(),
            "disk": device_monitor.get_disk_info(),
            "memory": device_monitor.get_memory_info()
        }

        logger.debug("Successfully gathered system resources")
        return JSONResponse(
            content={
                "status": "success",
                "data": resources
            },
            status_code=HTTP_200_OK
        )

    except Exception as e:
        logger.error(f"Failed to monitor system resources: {str(e)}", exc_info=True)
        return HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system resources"
        )

