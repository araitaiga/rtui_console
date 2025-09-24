"""
Log table panel widget
"""
import re

from textual.app import ComposeResult
from textual.widgets import DataTable
from textual.widgets import Static

from ..events import LogMessageSelected
from ..models import LogLevel
from ..models import LogMessage


class LogTablePanel(Static):
    """Main log display panel with table"""

    # Constants for log management
    MAX_TOTAL_MESSAGES = 10000
    MAX_DISPLAY_MESSAGES = 5000
    MAX_MESSAGE_LENGTH = 500
    MESSAGE_TRUNCATE_LENGTH = 497

    DEFAULT_CSS = """
    LogTablePanel {
        height: 70%;
        border-bottom: inner $primary;
    }
    """
    CSS_PATH = "../css/widgets/log_table.tcss"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.table = DataTable(cursor_type="row")
        self.log_messages = []
        self.filtered_messages = []
        self.selected_nodes = ["ALL"]
        self.selected_levels = ["ALL"]
        self.filter_text = ""
        self._saved_scroll_x = 0
        self._selected_log = None  # 選択されたログメッセージを保存

    def compose(self) -> ComposeResult:
        yield self.table

    def on_mount(self) -> None:
        self.table.add_columns("Time", "Level", "Node", "Message")
        # Set fixed height for the table to prevent scrollbar position changes
        self.table.styles.height = "100%"

    def add_log_message(self, log_msg: LogMessage):
        """Add a new log message"""
        self.log_messages.append(log_msg)

        # Limit total messages to prevent memory issues
        if len(self.log_messages) > self.MAX_TOTAL_MESSAGES:
            self.log_messages = self.log_messages[-(
                self.MAX_TOTAL_MESSAGES - 1000):]

        self.apply_filters()

    def set_node_filter(self, node_names):
        """Set node filter (multiple nodes supported)"""
        self.selected_nodes = ([node_names] if isinstance(node_names, str)
                               else list(node_names) if node_names else ["ALL"])
        self.apply_filters()

    def set_level_filter(self, levels):
        """Set level filter (multiple levels supported)"""
        self.selected_levels = ([levels] if isinstance(levels, str)
                                else list(levels) if levels else ["ALL"])
        self.apply_filters()

    def set_text_filter(self, text: str):
        """Set text filter"""
        self.filter_text = text.lower()
        self.apply_filters()

    def apply_filters(self):
        """Apply all filters to log messages with OR logic for multi-selection"""
        filtered = self.log_messages.copy()

        # Filter by nodes (OR logic)
        if self.selected_nodes and "ALL" not in self.selected_nodes:
            filtered = [
                msg for msg in filtered if msg.name in self.selected_nodes]

        # Filter by levels (OR logic)
        if self.selected_levels and "ALL" not in self.selected_levels:
            level_values = []
            for level_str in self.selected_levels:
                try:
                    level_values.append(int(level_str))
                except (ValueError, TypeError):
                    pass

            if level_values:
                filtered = [
                    msg for msg in filtered if msg.level in level_values]

        # Filter by text
        if self.filter_text:
            filtered = [
                msg for msg in filtered
                if self.filter_text in msg.msg.lower() or self.filter_text in msg.name.lower()
            ]

        self.filtered_messages = filtered
        self.update_table()

    def _sanitize_text_for_table(self, text):
        """Sanitize text for safe display in DataTable"""
        if not isinstance(text, str):
            text = str(text)

        # Replace control characters and non-printable characters
        # Keep only printable ASCII and common Unicode characters
        sanitized = re.sub(r'[^\x20-\x7E\u00A0-\uFFFF]', '', text)

        # Truncate very long messages to prevent UI issues
        if len(sanitized) > self.MAX_MESSAGE_LENGTH:
            sanitized = sanitized[:self.MESSAGE_TRUNCATE_LENGTH] + "..."

        return sanitized

    def update_table(self):
        """Update table display"""
        # Save current scroll positions
        saved_scroll_x = getattr(self.table, 'scroll_x', 0)
        saved_scroll_y = getattr(self.table, 'scroll_y', 0)

        # Clear and rebuild table
        self.table.clear()

        # Show latest messages first (reverse order)
        for msg in reversed(self.filtered_messages[-self.MAX_DISPLAY_MESSAGES:]):
            level_name = LogLevel.NAMES.get(msg.level, "UNKNOWN")
            level_color = LogLevel.COLORS.get(msg.level, "white")
            time_str = msg.timestamp.strftime("%H:%M:%S.%f")[:-3]

            # Sanitize text fields for safe display
            safe_node = self._sanitize_text_for_table(msg.name)
            safe_message = self._sanitize_text_for_table(msg.msg)

            self.table.add_row(
                time_str,
                f"[{level_color}]{level_name}[/{level_color}]",
                safe_node,
                safe_message
            )

        # Restore scroll positions immediately after table is updated
        if hasattr(self.table, 'scroll_x') and saved_scroll_x > 0:
            self.table.scroll_x = saved_scroll_x
        if hasattr(self.table, 'scroll_y') and saved_scroll_y > 0:
            self.table.scroll_y = saved_scroll_y

        # 選択されたログのハイライトを復元
        if self._selected_log is not None:
            self._restore_selected_log_highlight()

    def _restore_selected_log_highlight(self):
        """選択されたログのハイライトを復元"""
        if self._selected_log is None:
            return

        # フィルタされたメッセージから選択されたログを探す
        for i, msg in enumerate(self.filtered_messages):
            if (msg.timestamp == self._selected_log.timestamp and
                msg.level == self._selected_log.level and
                msg.name == self._selected_log.name and
                    msg.msg == self._selected_log.msg):
                # テーブルの行インデックスを計算（逆順なので）
                table_row = len(self.filtered_messages) - 1 - i
                if 0 <= table_row < len(self.filtered_messages):
                    # move_cursorメソッドを使用してカーソルを移動
                    self.table.move_cursor(row=table_row, animate=False)
                break

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection"""
        if event.cursor_row < len(self.filtered_messages):
            # Get the message (accounting for reverse order)
            msg_index = len(self.filtered_messages) - 1 - event.cursor_row
            if 0 <= msg_index < len(self.filtered_messages):
                selected_msg = self.filtered_messages[msg_index]

                # 同じログが既に選択されている場合は選択を解除
                if (self._selected_log is not None and
                    self._selected_log.timestamp == selected_msg.timestamp and
                    self._selected_log.level == selected_msg.level and
                    self._selected_log.name == selected_msg.name and
                        self._selected_log.msg == selected_msg.msg):
                    # 選択状態を解除
                    self._selected_log = None
                    self.post_message(LogMessageSelected(None))
                else:
                    # 新しいログを選択
                    self._selected_log = selected_msg
                    self.post_message(LogMessageSelected(selected_msg))

    def clear_logs(self):
        """Clear all log messages"""
        self.log_messages.clear()
        self.filtered_messages.clear()
        self._saved_scroll_x = 0  # Reset scroll position when clearing logs
        self._selected_log = None  # Reset selected log when clearing logs
        self.update_table()

    def get_filtered_count(self) -> int:
        """Get count of filtered messages"""
        return len(self.filtered_messages)

    def get_total_count(self) -> int:
        """Get count of total messages"""
        return len(self.log_messages)
