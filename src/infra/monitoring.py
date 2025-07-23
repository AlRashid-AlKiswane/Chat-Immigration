"""
System Resource Monitor

This script monitors and logs critical system resources including:
- CPU usage
- Memory usage
- Disk usage
- Battery status
- System temperature (if available)

It uses the `psutil` and `shutil` libraries to gather 
    metrics and logs all outputs using a structured logger.
The logger captures `info`, `warning`, and `error` messages 
    based on the severity of the readings or errors encountered during execution.

Functions:
    - setup_logger: Configures and returns a logger instance.
    - get_cpu_usage: Returns CPU usage percentage.
    - get_memory_usage: Returns memory usage statistics.
    - get_disk_usage: Returns disk usage statistics.
    - get_battery_status: Returns battery status, if available.
    - monitor_system_resources: Gathers all resource metrics and logs them.

Example:
    To run the monitoring script:

    ```bash
    python main_monitor.py
    ```

    You can import functions from this module into another script:

    ```python
    from main_monitor import monitor_system_resources
    monitor_system_resources()
    ```

Requirements:
    - Python 3.8+
    - psutil (install via `pip install psutil`)

Author:
    AlRashid AlKiswane

License:
    MIT License

Date:
    June 14, 2025
"""

# pylint: disable=logging-format-interpolation

import os
import sys
import logging
import shutil
from typing import Optional, Dict, Any
import psutil

# Constants should be uppercase
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable= wrong-import-position
from src.infra import setup_logging
from src.enums import MonitoringLogMsg

logger = setup_logging(name="MONITORING-RESCEOURCES")


class DeviceMonitor:
    """
    A class to monitor and retrieve system information such as CPU, memory,
    disk, battery, and temperature. Includes logging for each operation.
    """

    def __init__(self):
        """
        Initialize the DeviceMonitor with a configured logger.

        Args:
            logger_name (str): Name of the logger.
        """
        self.logger = logger

    def get_cpu_info(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve CPU usage and temperature information.

        Returns:
            dict: CPU percent usage and temperature.
        """
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            temps = psutil.sensors_temperatures()
            cpu_temp = (
                temps.get("coretemp", [None])[0].current
                if temps.get("coretemp")
                else None
            )
            self.logger.info("Retrieved CPU info.")
            return {"cpu_usage": cpu_usage, "cpu_temp": cpu_temp}
        except (psutil.Error, RuntimeError, AttributeError) as e:
            self.logger.error(MonitoringLogMsg.CPU_USAGE_ERROR.value.format(e))
            return None

    def get_memory_info(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve memory usage statistics.

        Returns:
            dict: Total, available, used memory, and percentage used.
        """
        try:
            mem = psutil.virtual_memory()
            return {
                "total": mem.total // (1024**2),
                "available": mem.available // (1024**2),
                "used": mem.used // (1024**2),
                "percent": mem.percent,
            }
        except psutil.Error as e:
            self.logger.error(MonitoringLogMsg.MEMORY_ERROR.value.format(e))
            return None

    def get_disk_info(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve disk space information.

        Returns:
            dict: Total, used, and free disk space.
        """
        try:
            total, used, free = shutil.disk_usage("/")
            return {
                "total": total // (1024**3),
                "used": used // (1024**3),
                "free": free // (1024**3),
            }
        except OSError as e:
            self.logger.error(MonitoringLogMsg.DISK_ERROR.value.format(e))
            return None

    def get_battery_info(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve battery percentage and charging status.

        Returns:
            dict: Battery percentage and whether plugged in.
            None: If battery info is not available or an error occurs.
        """
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {"percent": battery.percent, "plugged_in": battery.power_plugged}
            self.logger.warning(MonitoringLogMsg.BATTERY_WARNING.value)
            return None
        except (psutil.Error, RuntimeError) as e:
            self.logger.error(MonitoringLogMsg.BATTERY_ERROR.value.format(e))
            return None

    def monitor(self) -> None:
        """
        Log all collected system stats.
        """
        # pylint: disable=logging-format-interpolation
        self.logger.info(MonitoringLogMsg.MONITORING_START.value)

        cpu_info = self.get_cpu_info()
        if cpu_info:
            self.logger.info(
                MonitoringLogMsg.CPU_USAGE.value.format(
                    cpu_info["cpu_usage"],
                    cpu_info["cpu_temp"] if cpu_info["cpu_temp"] is not None else 0.0
                )
            )

        memory_info = self.get_memory_info()
        if memory_info:
            self.logger.info(
                MonitoringLogMsg.MEMORY_USAGE.value.format(
                    memory_info["total"],
                    memory_info["available"],
                    memory_info["used"],
                    memory_info["percent"]
                )
            )

        disk_info = self.get_disk_info()
        if disk_info:
            self.logger.info(
                MonitoringLogMsg.DISK_USAGE.value.format(
                    disk_info["total"],
                    disk_info["used"],
                    disk_info["free"]
                )
            )

        battery_info = self.get_battery_info()
        if battery_info:
            self.logger.info(
                MonitoringLogMsg.BATTERY_STATUS.value.format(
                    battery_info["percent"],
                    battery_info["plugged_in"]
                )
            )


if __name__ == "__main__":
    monitor = DeviceMonitor()
    monitor.monitor()
