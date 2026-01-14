"""
Activity Logger for tracking application events
Provides logging to file and UI display
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from collections import deque


class ActivityLogger:
    """Manages application activity logging with UI integration"""

    LOG_LEVELS = {
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "SUCCESS": logging.INFO,
        "DEBUG": logging.DEBUG
    }

    def __init__(self, log_file: str = "activity.log", max_display_lines: int = 5):
        """
        Initialize the activity logger

        Args:
            log_file: Name of the log file
            max_display_lines: Maximum lines to keep for UI display
        """
        self.log_file = self._get_log_path(log_file)
        self.max_display_lines = max_display_lines
        self.recent_logs: deque = deque(maxlen=max_display_lines)

        # Callbacks for UI updates
        self.on_log_callback: Optional[callable] = None

        # Setup file logging
        self._setup_logging()

    def _get_log_path(self, filename: str) -> Path:
        """Get the log file path"""
        log_dir = Path.home() / "AppData" / "Roaming" / "TSProtectorPro" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir / filename

    def _setup_logging(self):
        """Configure Python logging"""
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # File handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

        # Remove existing handlers
        root_logger.handlers.clear()

        # Add handlers
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

    def log(self, message: str, level: str = "INFO"):
        """
        Log a message with specified level

        Args:
            message: Message to log
            level: Log level (INFO, WARNING, ERROR, SUCCESS)
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] [{level}] {message}"

        # Add to recent logs for UI
        self.recent_logs.append({
            'timestamp': timestamp,
            'level': level,
            'message': message,
            'formatted': formatted_message
        })

        # Log to file using Python logging
        log_level = self.LOG_LEVELS.get(level, logging.INFO)
        logger = logging.getLogger('TSProtectorPro')
        logger.log(log_level, message)

        # Notify UI callback
        if self.on_log_callback:
            try:
                self.on_log_callback(formatted_message, level)
            except Exception as e:
                logging.error(f"Error in log callback: {e}")

    def info(self, message: str):
        """Log an info message"""
        self.log(message, "INFO")

    def warning(self, message: str):
        """Log a warning message"""
        self.log(message, "WARNING")

    def error(self, message: str):
        """Log an error message"""
        self.log(message, "ERROR")

    def success(self, message: str):
        """Log a success message"""
        self.log(message, "SUCCESS")

    def get_recent_logs(self, count: Optional[int] = None) -> List[dict]:
        """
        Get recent log entries

        Args:
            count: Number of logs to return (None = all recent)

        Returns:
            List of log entry dicts
        """
        if count is None:
            count = self.max_display_lines

        logs = list(self.recent_logs)
        return logs[-count:]

    def set_callback(self, callback: callable):
        """
        Set callback function for new log entries

        Args:
            callback: Function(message: str, level: str) to call on new logs
        """
        self.on_log_callback = callback

    def clear_logs(self):
        """Clear recent logs cache"""
        self.recent_logs.clear()

    def get_log_file_path(self) -> str:
        """Get the path to the log file"""
        return str(self.log_file)
