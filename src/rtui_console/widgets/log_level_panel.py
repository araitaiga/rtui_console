"""
Log level selection panel widget
"""
from textual.app import ComposeResult
from textual.widgets import Static
from textual.widgets import Tree

from ..events import LevelFilterChanged
from ..models import LogLevel


class LogLevelPanel(Static):
    """Left panel showing log levels in a tree structure"""

    DEFAULT_CSS = """
    LogLevelPanel {
        padding-left: 2;
        width: 30%;
        height: 30%;
        border-top: inner $primary;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.level_tree = Tree("Log Levels")
        self.level_tree.auto_expand = True
        self.selected_level = "ALL"

    def compose(self) -> ComposeResult:
        yield self.level_tree

    def on_mount(self) -> None:
        """Initialize the level tree"""
        self.update_levels()

    def update_levels(self):
        """Update the level tree with all available levels"""
        self.level_tree.clear()

        # Add "All Levels" option
        all_levels = self.level_tree.root.add("All Levels", "ALL")

        # Add individual log levels with color indicators
        levels = [
            ("🔵 DEBUG", str(LogLevel.DEBUG)),
            ("🟢 INFO", str(LogLevel.INFO)),
            ("🟡 WARN", str(LogLevel.WARN)),
            ("🔴 ERROR", str(LogLevel.ERROR)),
            ("🟣 FATAL", str(LogLevel.FATAL))
        ]

        for display_name, level_value in levels:
            self.level_tree.root.add_leaf(display_name, level_value)

    def on_tree_node_selected(self, event: Tree.NodeSelected[str]) -> None:
        """Handle level selection"""
        if event.node.is_root or event.node.data is None:
            return

        self.selected_level = event.node.data
        self.post_message(LevelFilterChanged(event.node.data))

    def set_selected_level(self, level: str):
        """Set the selected level programmatically"""
        self.selected_level = level
        # Could add visual indication of selection here if needed
