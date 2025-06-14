"""System resource monitoring module.

Provides functionality to monitor CPU, memory, disk, and GPU usage.
Logs alerts when usage exceeds predefined thresholds from environment settings.
"""

import logging
import os
import sys
import time
from typing import Dict, Union

import psutil

try:
    MAIN_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../")
    )
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)

    from src.helpers.settings import Settings, get_settings
    from src.logs import setup_logging
    from src.enums import MonitoringLogMsg

    logger = setup_logging()

except ModuleNotFoundError as e:
    logging.error("Module not found: %s", e, exc_info=True)
except ImportError as e:
    logging.error("Import error: %s", e, exc_info=True)
except Exception as e:
    logging.critical("Unexpected setup error: %s", e, exc_info=True)
    raise


class SystemMonitor:
    """Monitors system resource usage (CPU, Memory, Disk, GPU)."""

    def __init__(self) -> None:
        self.app_settings: Settings = get_settings()
        self.cpu_threshold = self.app_settings.CPU_THRESHOLD
        self.memory_threshold = self.app_settings.MEMORY_THRESHOLD
        self.disk_threshold = self.app_settings.DISK_THRESHOLD
        self.gpu_threshold = self.app_settings.GPUs_THRESHOLD
        self.gpu_available = self.app_settings.GPU_AVAILABLE

    def check_cpu_usage(self) -> Dict[str, Union[float, str]]:
        """Check CPU usage and log alerts if thresholds are exceeded."""
        try:
            usage = psutil.cpu_percent(interval=1)
            logger.info(MonitoringLogMsg.CPU_USAGE.value + "%%", usage)
            if usage > self.cpu_threshold:
                logger.warning(
                    MonitoringLogMsg.CPU_THRESHOLD_EXCEEDED.value + "%% > %%", 
                    usage, self.cpu_threshold
                )
            return {"cpu_usage": usage}
        except psutil.Error as err:
            logger.error(MonitoringLogMsg.CPU_USAGE_ERROR.value, str(err))
            return {"error": str(err)}

    def check_memory_usage(self) -> Dict[str, Union[float, str]]:
        """Check memory usage and log alerts if thresholds are exceeded."""
        try:
            memory = psutil.virtual_memory()
            logger.info(MonitoringLogMsg.MEMORY_USAGE.value + "%%", memory.percent)
            if memory.percent > self.memory_threshold:
                logger.warning(
                    MonitoringLogMsg.MEMORY_THRESHOLD_EXCEEDED.value + "%% > %%", 
                    memory.percent, self.memory_threshold
                )
            return {"memory_usage": memory.percent}
        except psutil.Error as err:
            logger.error(MonitoringLogMsg.MEMORY_USAGE_ERROR.value, str(err))
            return {"error": str(err)}

    def check_disk_usage(self) -> Dict[str, Union[float, str]]:
        """Check disk usage and log alerts if thresholds are exceeded."""
        try:
            disk = psutil.disk_usage("/")
            logger.info(MonitoringLogMsg.DISK_USAGE.value + "%%", disk.percent)
            if disk.percent > self.disk_threshold:
                logger.warning(
                    MonitoringLogMsg.DISK_THRESHOLD_EXCEEDED.value + "%% > %%", 
                    disk.percent, self.disk_threshold
                )
            return {"disk_usage": disk.percent}
        except psutil.Error as err:
            logger.error(MonitoringLogMsg.DISK_USAGE_ERROR.value, str(err))
            return {"error": str(err)}

    def check_gpu_usage(self) -> Dict[str, Union[float, str]]:
        """Check GPU usage and log alerts if thresholds are exceeded."""
        if not self.gpu_available:
            return {"gpu_usage": MonitoringLogMsg.GPU_MONITOR_PLACEHOLDER.value}

        try:
            from pynvml import (
                nvmlInit,
                nvmlDeviceGetHandleByIndex,
                nvmlDeviceGetUtilizationRates,
            )

            nvmlInit()
            handle = nvmlDeviceGetHandleByIndex(0)
            util = nvmlDeviceGetUtilizationRates(handle)
            usage = util.gpu
            logger.info("GPU Usage: %d%%", usage)
            if usage > self.gpu_threshold:
                logger.warning(
                    "[ALERT] GPU usage exceeded threshold: %d%% > %d%%",
                    usage,
                    self.gpu_threshold,
                )
            return {"gpu_usage": usage}
        except ImportError:
            logger.error("pynvml not installed for GPU monitoring.")
            return {"error": "pynvml not installed"}
        except Exception as err:
            logger.error("GPU monitoring error: %s", err)
            return {"error": str(err)}

    def start_monitoring(self) -> None:
        """Begin continuous monitoring loop."""
        logger.info(MonitoringLogMsg.MONITORING_STARTED.value)
        interval = self.app_settings.MONITOR_INTERVAL

        while True:
            self.check_cpu_usage()
            self.check_memory_usage()
            self.check_disk_usage()
            if self.gpu_available:
                self.check_gpu_usage()
            time.sleep(interval)


if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.start_monitoring()
