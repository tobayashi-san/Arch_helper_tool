"""
Core Module - Backend Logic for Arch Config Tool
"""

from .dependency_check import DependencyChecker
from .config_manager import ConfigManager, ConfigCategory, ConfigItem
from .command_executor import CommandExecutor, CommandResult, CommandStatus
from .logger import Logger, get_logger, init_logger

__version__ = "1.0.0"
__author__ = "Arch Config Tool"

__all__ = [
    "DependencyChecker",
    "ConfigManager",
    "ConfigCategory",
    "ConfigItem",
    "CommandExecutor",
    "CommandResult",
    "CommandStatus",
    "Logger",
    "get_logger",
    "init_logger"
]
