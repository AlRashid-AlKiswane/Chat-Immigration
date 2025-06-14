"""System Resource Monitoring Module.

This module provides centralized monitoring capabilities for system resources including
CPU, memory, and disk usage. It includes predefined log messages and alerting functionality
for tracking system health and performance thresholds.

The main components include:
- MonitoringLogMsg: Standardized enumeration of log messages for all monitoring scenarios
- ResourceMonitor: Core monitoring class (if present in your module)
- AlertManager: Threshold-based alerting system (if present in your module)

Key Features:
- Real-time resource utilization tracking
- Configurable threshold-based alerting
- Unified logging interface
- Extensible monitoring framework

Example Usage:
    >>> from monitoring import ResourceMonitor
    >>> monitor = ResourceMonitor(
    ...     cpu_threshold=80,
    ...     memory_threshold=85,
    ...     disk_threshold=90
    ... )
    >>> monitor.start_monitoring()

Configuration:
    Thresholds can be set via environment variables:
    - CPU_ALERT_THRESHOLD
    - MEMORY_ALERT_THRESHOLD
    - DISK_ALERT_THRESHOLD

Note:
    GPU monitoring is currently not implemented (see GPU_MONITOR_PLACEHOLDER).

Author: [Your Name/Team Name]
Version: 0.1.0
License: [Your License, e.g., "MIT"]
"""

from enum import Enum


class MonitoringLogMsg(Enum):
    """Enumeration of monitoring log messages for system resource tracking.

    This class provides standardized log messages for various monitoring scenarios,
    including CPU, memory, and disk usage tracking, as well as error conditions.
    """

    CPU_USAGE = "CPU Usage: {}%"
    """Message template for reporting current CPU usage percentage."""

    CPU_USAGE_ERROR = "Failed to get CPU usage: {}"
    """Error message when CPU usage cannot be retrieved."""

    MEMORY_USAGE = "Memory Usage: {}%"
    """Message template for reporting current memory usage percentage."""

    MEMORY_USAGE_ERROR = "Failed to get memory usage: {}"
    """Error message when memory usage cannot be retrieved."""

    DISK_USAGE = "Disk Usage: {}%"
    """Message template for reporting current disk usage percentage."""

    DISK_USAGE_ERROR = "Failed to get disk usage: {}"
    """Error message when disk usage cannot be retrieved."""

    BATTERY_USAGE = ""
    """ """
    BATTERY_WARNING = "Battery info not available."
    """ """

    BATTERY_ERROR = "Failed to retrieve battery info: {}"
    """ """

    SYSTEM_TEMPERATURE = " "
    """ """
    SYSTEM_TEMPERATURE_WARNING = "vcgencmd not found. {}"
    """"""
    SYSTEM_TEMPERATURE_ERROR = "Failed to retrieve system temperature: {}"
    """ """

    MONITORING_STARTED = "System resource monitoring started."
    """Message indicating that system resource monitoring has begun."""

    GPU_MONITOR_PLACEHOLDER = "GPU monitoring is not yet implemented."
    """Placeholder message indicating GPU monitoring is not available."""

    MEMORY_ERROR = "Failed to get memory usage: %s"
    DISK_ERROR = "Failed to get disk usage: %s"
