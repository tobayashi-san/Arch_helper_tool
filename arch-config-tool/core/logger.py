"""
Logger
Handles application logging with file and console output and log rotation
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path
from logging.handlers import RotatingFileHandler

class Logger:
    def __init__(self, log_file: str = "data/arch-config-tool.log", log_level: str = "INFO", use_rotation: bool = True):
        self.log_file = log_file
        self.use_rotation = use_rotation
        self.logger = logging.getLogger("ArchConfigTool")
        self.setup_logger(log_level)

    def setup_logger(self, log_level: str = "INFO"):
        """Setup logging configuration with optional rotation"""
        # Ensure log directory exists
        log_dir = os.path.dirname(self.log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        # Clear existing handlers
        self.logger.handlers.clear()

        # Set log level
        level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger.setLevel(level)

        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )

        # File handler with optional rotation
        try:
            if self.use_rotation:
                file_handler = self.setup_rotating_logs()
            else:
                file_handler = logging.FileHandler(self.log_file, encoding='utf-8')

            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not create log file {self.log_file}: {e}")

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # Log startup
        self.logger.info("Logger initialized")

    def setup_rotating_logs(self) -> RotatingFileHandler:
        """Implementiere Log-Rotation für große Log-Dateien"""
        handler = RotatingFileHandler(
            self.log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        return handler

    def log_command(self, command: str, success: bool, output: str, error: str = "", execution_time: float = 0):
        """Log executed commands with details"""
        status = "SUCCESS" if success else "FAILED"

        log_entry = f"COMMAND [{status}]: {command}"
        if execution_time > 0:
            log_entry += f" (took {execution_time:.2f}s)"

        if success:
            self.logger.info(log_entry)
            if output.strip():
                self.logger.debug(f"STDOUT: {output.strip()}")
        else:
            self.logger.error(log_entry)
            if error.strip():
                self.logger.error(f"STDERR: {error.strip()}")
            if output.strip():
                self.logger.debug(f"STDOUT: {output.strip()}")

    def log_config_update(self, source: str, success: bool, details: str = ""):
        """Log configuration updates"""
        status = "SUCCESS" if success else "FAILED"
        message = f"CONFIG UPDATE [{status}] from {source}"
        if details:
            message += f": {details}"

        if success:
            self.logger.info(message)
        else:
            self.logger.error(message)

    def log_dependency_check(self, tool: str, available: bool, details: str = ""):
        """Log dependency check results"""
        status = "AVAILABLE" if available else "MISSING"
        message = f"DEPENDENCY [{status}]: {tool}"
        if details:
            message += f" - {details}"

        if available:
            self.logger.info(message)
        else:
            self.logger.warning(message)

    def log_error(self, message: str, exception: Optional[Exception] = None):
        """Log errors with optional exception details"""
        if exception:
            self.logger.error(f"{message}: {str(exception)}", exc_info=True)
        else:
            self.logger.error(message)

    def log_info(self, message: str):
        """Log informational messages"""
        self.logger.info(message)

    def log_warning(self, message: str):
        """Log warning messages"""
        self.logger.warning(message)

    def log_debug(self, message: str):
        """Log debug messages"""
        self.logger.debug(message)

    def get_log_stats(self) -> dict:
        """Get logging statistics including rotation info"""
        try:
            stats = {"rotation_enabled": self.use_rotation}

            if not os.path.exists(self.log_file):
                stats["error"] = "Log file not found"
                return stats

            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            stats.update({
                "total_lines": len(lines),
                "error_count": sum(1 for line in lines if "ERROR" in line),
                "warning_count": sum(1 for line in lines if "WARNING" in line),
                "info_count": sum(1 for line in lines if "INFO" in line),
                "command_count": sum(1 for line in lines if "COMMAND" in line),
                "file_size_kb": round(os.path.getsize(self.log_file) / 1024, 2),
                "last_modified": datetime.fromtimestamp(os.path.getmtime(self.log_file)).isoformat()
            })

            # Check for rotated log files if rotation is enabled
            if self.use_rotation:
                rotated_files = []
                for i in range(1, 6):  # backupCount = 5
                    rotated_file = f"{self.log_file}.{i}"
                    if os.path.exists(rotated_file):
                        rotated_files.append({
                            "file": rotated_file,
                            "size_kb": round(os.path.getsize(rotated_file) / 1024, 2),
                            "modified": datetime.fromtimestamp(os.path.getmtime(rotated_file)).isoformat()
                        })
                stats["rotated_files"] = rotated_files
                stats["total_log_files"] = len(rotated_files) + 1

            return stats

        except Exception as e:
            return {"error": f"Could not read log stats: {e}"}

    def clear_logs(self):
        """Clear log file and rotated files"""
        try:
            # Clear main log file
            if os.path.exists(self.log_file):
                os.remove(self.log_file)

            # Clear rotated log files if rotation is enabled
            if self.use_rotation:
                for i in range(1, 6):  # backupCount = 5
                    rotated_file = f"{self.log_file}.{i}"
                    if os.path.exists(rotated_file):
                        os.remove(rotated_file)

            self.setup_logger()  # Recreate logger
            self.logger.info("All log files cleared")
            return True
        except Exception as e:
            self.logger.error(f"Could not clear log files: {e}")
            return False

    def get_recent_logs(self, lines: int = 50) -> list:
        """Get recent log entries"""
        try:
            if not os.path.exists(self.log_file):
                return []

            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()

            # Return last N lines
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            return [line.strip() for line in recent_lines]

        except Exception as e:
            self.logger.error(f"Could not read recent logs: {e}")
            return []

    def get_all_logs(self) -> list:
        """Get all logs from current and rotated files"""
        try:
            all_logs = []

            # Read rotated files first (oldest to newest)
            if self.use_rotation:
                for i in range(5, 0, -1):  # Read from .5 to .1
                    rotated_file = f"{self.log_file}.{i}"
                    if os.path.exists(rotated_file):
                        with open(rotated_file, 'r', encoding='utf-8') as f:
                            all_logs.extend([line.strip() for line in f.readlines()])

            # Read current log file (newest)
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    all_logs.extend([line.strip() for line in f.readlines()])

            return all_logs

        except Exception as e:
            self.logger.error(f"Could not read all logs: {e}")
            return []


# Global logger instance
_global_logger: Optional[Logger] = None

def get_logger() -> Logger:
    """Get the global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = Logger()
    return _global_logger

def init_logger(log_file: str = "data/arch-config-tool.log", log_level: str = "INFO", use_rotation: bool = True) -> Logger:
    """Initialize the global logger with optional rotation"""
    global _global_logger
    _global_logger = Logger(log_file, log_level, use_rotation)
    return _global_logger


# Test function with rotation testing
if __name__ == "__main__":
    print("🧪 Teste Logger mit Log-Rotation...")

    # Initialize logger with rotation
    logger = Logger("data/test.log", use_rotation=True)

    # Test different log levels
    logger.log_info("Application started")
    logger.log_debug("Debug message")
    logger.log_warning("This is a warning")
    logger.log_error("This is an error")

    # Test command logging
    logger.log_command("sudo pacman -Syu", True, "System updated successfully", execution_time=30.5)
    logger.log_command("invalid-command", False, "", "Command not found", execution_time=0.1)

    # Test dependency logging
    logger.log_dependency_check("pacman", True, "Found at /usr/bin/pacman")
    logger.log_dependency_check("yay", False, "Not installed")

    # Test config logging
    logger.log_config_update("GitHub", True, "Downloaded 150 tools in 9 categories")
    logger.log_config_update("Local cache", False, "Cache file corrupted")

    # Test large log generation to trigger rotation
    print("📝 Generiere große Log-Einträge zum Testen der Rotation...")
    for i in range(1000):
        logger.log_info(f"Test log entry {i:04d} - " + "x" * 100)  # Large entries

    # Show enhanced stats
    print("\n📊 Enhanced Log Statistics:")
    stats = logger.get_log_stats()
    for key, value in stats.items():
        if key == "rotated_files":
            print(f"   {key}:")
            for rotated in value:
                print(f"     - {rotated['file']}: {rotated['size_kb']} KB")
        else:
            print(f"   {key}: {value}")

    # Show recent logs
    print("\n📋 Recent Logs (last 5):")
    recent = logger.get_recent_logs(5)
    for log_line in recent:
        print(f"   {log_line}")

    print("\n✅ Logger mit Rotation test completed!")
    print(f"📁 Log-Dateien befinden sich in: {os.path.abspath('data/')}")
