"""
Log detail panel widget
"""
import re
from typing import Optional

from textual.widgets import Static

from ..models import LogLevel
from ..models import LogMessage


class LogDetailPanel(Static):
    """Bottom panel showing selected log message details"""

    DEFAULT_CSS = """
    LogDetailPanel {
        height: 30%;
        padding: 1 2;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.selected_message = None

    def set_message(self, log_message: LogMessage):
        """Set the message to display details for"""
        self.selected_message = log_message
        self.update_display()

    def _sanitize_text(self, text):
        """Sanitize text for safe display in Textual markup"""
        if not isinstance(text, str):
            text = str(text)

        # Replace control characters and non-printable characters
        # Keep only printable ASCII and common Unicode characters
        sanitized = re.sub(r'[^\x20-\x7E\u00A0-\uFFFF]', '�', text)

        # Escape Textual markup characters
        sanitized = sanitized.replace('[', '\\[')
        sanitized = sanitized.replace(']', '\\]')

        return sanitized

    def update_display(self):
        """Update the detail display"""
        if self.selected_message is None:
            self.update("Select a log message to view details")
            return

        msg = self.selected_message
        level_name = LogLevel.NAMES.get(msg.level, "UNKNOWN")
        level_color = LogLevel.COLORS.get(msg.level, "white")

        # Sanitize all text fields
        safe_node = self._sanitize_text(msg.name)
        safe_message = self._sanitize_text(msg.msg)
        safe_file = self._sanitize_text(msg.file or 'N/A')
        safe_function = self._sanitize_text(msg.function or 'N/A')
        safe_line = self._sanitize_text(str(msg.line or 'N/A'))

        details = f"""[b]Log Message Details[/b]

[b]Timestamp:[/b] {msg.timestamp.isoformat()}
[b]Level:[/b] [{level_color}]{level_name}[/{level_color}]
[b]Node:[/b] {safe_node}
[b]Message:[/b] {safe_message}

[b]Source Info:[/b]
  File: {safe_file}
  Function: {safe_function}
  Line: {safe_line}
"""
        self.update(details)

    def clear_details(self):
        """Clear the details display"""
        self.selected_message = None
        self.update("Logs cleared")
