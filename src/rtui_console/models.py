"""
Data models for ROS2 Console Viewer
"""
from datetime import datetime
from typing import Optional


class LogLevel:
    """Log level constants matching ROS2 log levels"""
    DEBUG = 10
    INFO = 20
    WARN = 30
    ERROR = 40
    FATAL = 50

    NAMES = {
        DEBUG: "DEBUG",
        INFO: "INFO",
        WARN: "WARN",
        ERROR: "ERROR",
        FATAL: "FATAL"
    }

    COLORS = {
        DEBUG: "white",
        INFO: "green",
        WARN: "yellow",
        ERROR: "red",
        FATAL: "magenta"
    }


class LogMessage:
    """Represents a single log message"""

    def __init__(self, msg=None, timestamp=None, level=None, name=None, text=None, file=None, function=None, line=None):
        # Check if ROS2 imports are available
        try:
            from rcl_interfaces.msg import Log
            ros2_available = True
        except ImportError:
            ros2_available = False

        if msg is not None and ros2_available:
            # From ROS2 Log message
            self.timestamp = datetime.fromtimestamp(
                msg.stamp.sec + msg.stamp.nanosec * 1e-9
            )
            self.level = msg.level
            self.name = msg.name
            self.msg = msg.msg
            self.file = msg.file
            self.function = msg.function
            self.line = msg.line
        else:
            # Manual creation (for test logs)
            self.timestamp = timestamp or datetime.now()
            self.level = level or LogLevel.INFO
            self.name = name or "unknown"
            self.msg = text or ""
            self.file = file or ""
            self.function = function or ""
            self.line = line or 0

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'node': self.name,
            'message': self.msg,
            'file': self.file,
            'function': self.function,
            'line': self.line
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'LogMessage':
        """Create LogMessage from dictionary"""
        return cls(
            timestamp=datetime.fromisoformat(
                data.get('timestamp', datetime.now().isoformat())),
            level=data.get('level', LogLevel.INFO),
            name=data.get('node', 'unknown'),
            text=data.get('message', ''),
            file=data.get('file', ''),
            function=data.get('function', ''),
            line=data.get('line', 0)
        )
