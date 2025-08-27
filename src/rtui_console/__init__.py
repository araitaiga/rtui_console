"""
ROS2 Console Viewer - TUI version of rqt_console using Textual

A professional terminal-based log viewer for ROS2 systems,
designed with rtui-inspired interface patterns.
"""

from .app import ConsoleApp
from .events import LogMessageSelected
from .events import LogsCleared
from .events import NodeSelected
from .events import TestLogsGenerated
from .models import LogLevel
from .models import LogMessage
from .ros_client import LogGenerator
from .ros_client import ROS2Client

__version__ = "1.0.0"
__author__ = "ROS2 Console Viewer Team"

__all__ = [
    "ConsoleApp",
    "LogLevel",
    "LogMessage",
    "NodeSelected",
    "LogMessageSelected",
    "LogsCleared",
    "TestLogsGenerated",
    "ROS2Client",
    "LogGenerator",
]
