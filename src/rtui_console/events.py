"""
Custom events for ROS2 Console Viewer
"""
from textual.message import Message

from .models import LogMessage


class NodeSelected(Message):
    """Event when nodes are selected from the tree"""

    def __init__(self, node_names) -> None:
        super().__init__()
        # Handle both single string and list of strings
        if isinstance(node_names, str):
            self.node_names = [node_names]
        else:
            self.node_names = list(node_names) if node_names else []


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
    """Event when log level filters are changed"""

    def __init__(self, levels) -> None:
        super().__init__()
        # Handle both single string and list of strings
        if isinstance(levels, str):
            self.levels = [levels]
        else:
            self.levels = list(levels) if levels else []


class TextFilterChanged(Message):
    """Event when text filter is changed"""

    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text
