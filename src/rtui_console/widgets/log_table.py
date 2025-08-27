"""
Log table panel widget
"""
from textual.app import ComposeResult
from textual.widgets import DataTable
from textual.widgets import Static

from ..events import LogMessageSelected
from ..models import LogLevel
from ..models import LogMessage


class LogTablePanel(Static):
    """Main log display panel with table"""

    DEFAULT_CSS = """
    LogTablePanel {
        height: 70%;
        border-bottom: inner $primary;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.table = DataTable(cursor_type="row")
        self.log_messages = []
        self.filtered_messages = []
        self.selected_node = "ALL"
        self.min_level = LogLevel.DEBUG
        self.filter_text = ""

    def compose(self) -> ComposeResult:
        yield self.table

    def on_mount(self) -> None:
        self.table.add_columns("Time", "Level", "Node", "Message")

    def add_log_message(self, log_msg: LogMessage):
        """Add a new log message"""
        self.log_messages.append(log_msg)

        # Limit total messages to prevent memory issues
        if len(self.log_messages) > 5000:
            self.log_messages = self.log_messages[-4000:]

        self.apply_filters()

    def set_node_filter(self, node_name: str):
        """Set node filter"""
        self.selected_node = node_name
        self.apply_filters()

    def set_level_filter(self, min_level: int):
        """Set minimum log level filter"""
        self.min_level = min_level
        self.apply_filters()

    def set_text_filter(self, text: str):
        """Set text filter"""
        self.filter_text = text.lower()
        self.apply_filters()

    def apply_filters(self):
        """Apply all filters to log messages"""
        filtered = self.log_messages.copy()

        # Filter by node
        if self.selected_node != "ALL":
            filtered = [msg for msg in filtered if msg.name ==
                        self.selected_node]

        # Filter by level
        filtered = [msg for msg in filtered if msg.level >= self.min_level]

        # Filter by text
        if self.filter_text:
            filtered = [
                msg for msg in filtered
                if self.filter_text in msg.msg.lower() or self.filter_text in msg.name.lower()
            ]

        self.filtered_messages = filtered
        self.update_table()

    def update_table(self):
        """Update table display"""
        self.table.clear()

        # Show latest messages first (reverse order)
        for msg in reversed(self.filtered_messages[-1000:]):
            level_name = LogLevel.NAMES.get(msg.level, "UNKNOWN")
            level_color = LogLevel.COLORS.get(msg.level, "white")
            time_str = msg.timestamp.strftime("%H:%M:%S.%f")[:-3]

            self.table.add_row(
                time_str,
                f"[{level_color}]{level_name}[/{level_color}]",
                msg.name,
                msg.msg
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection"""
        if event.cursor_row < len(self.filtered_messages):
            # Get the message (accounting for reverse order)
            msg_index = len(self.filtered_messages) - 1 - event.cursor_row
            if 0 <= msg_index < len(self.filtered_messages):
                selected_msg = self.filtered_messages[msg_index]
                self.post_message(LogMessageSelected(selected_msg))

    def clear_logs(self):
        """Clear all log messages"""
        self.log_messages.clear()
        self.filtered_messages.clear()
        self.update_table()

    def get_filtered_count(self) -> int:
        """Get count of filtered messages"""
        return len(self.filtered_messages)

    def get_total_count(self) -> int:
        """Get count of total messages"""
        return len(self.log_messages)
