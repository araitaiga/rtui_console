"""
Custom events for ROS2 Console Viewer
"""
from textual.message import Message

from .models import LogMessage


class NodeSelected(Message):
    """Event when a node is selected from the tree"""

    def __init__(self, node_name: str) -> None:
        super().__init__()
        self.node_name = node_name


class LogMessageSelected(Message):
    """Event when a log message is selected"""

    def __init__(self, log_message: LogMessage) -> None:
        super().__init__()
        self.log_message = log_message


class LogsCleared(Message):
    """Event when logs are cleared"""
    pass


class TestLogsGenerated(Message):
    """Event when test logs are generated"""

    def __init__(self, count: int) -> None:
        super().__init__()
        self.count = count


class LevelFilterChanged(Message):
    """Event when log level filter is changed"""

    def __init__(self, level: str) -> None:
        super().__init__()
        self.level = level


class TextFilterChanged(Message):
    """Event when text filter is changed"""

    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text
