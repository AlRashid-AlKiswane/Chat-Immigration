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
    """Standardized monitoring messages with format placeholders for system metrics."""

    # CPU Monitoring
    CPU_USAGE = "CPU Usage: {:.1f}% | Temp: {:.1f}°C"  # Matches get_cpu_info() return
    CPU_USAGE_ERROR = "CPU monitoring failed: {}"

    # Memory Monitoring
    MEMORY_USAGE = (
        "Memory: {used}MB/{total}MB ({percent:.1f}%)"  # Matches get_memory_info()
    )
    MEMORY_ERROR = "Memory monitoring failed: {}"

    # Disk Monitoring
    DISK_USAGE = (
        "Disk: {used}GB/{total}GB ({percent:.1f}% used)"  # Matches get_disk_info()
    )
    DISK_ERROR = "Disk monitoring failed: {}"

    # Battery Monitoring
    BATTERY_STATUS = (
        "Battery: {percent:.1f}% | Charging: {plugged_in}"  # Matches get_battery_info()
    )
    BATTERY_WARNING = "Battery monitoring not available on this system"
    BATTERY_ERROR = "Battery monitoring failed: {}"

    # Temperature Monitoring
    TEMPERATURE_READING = (
        "System Temperature: {:.1f}°C"  # Matches get_system_temperature_linux()
    )
    TEMPERATURE_WARNING = "Temperature monitoring not available"
    TEMPERATURE_ERROR = "Temperature monitoring failed: {}"

    # System
    MONITORING_START = "Starting system monitoring"
    MONITORING_COMPLETE = "Monitoring cycle completed"
