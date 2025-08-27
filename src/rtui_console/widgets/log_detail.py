"""
Log detail panel widget
"""
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

    def update_display(self):
        """Update the detail display"""
        if self.selected_message is None:
            self.update("Select a log message to view details")
            return

        msg = self.selected_message
        level_name = LogLevel.NAMES.get(msg.level, "UNKNOWN")
        level_color = LogLevel.COLORS.get(msg.level, "white")

        details = f"""[b]Log Message Details[/b]

[b]Timestamp:[/b] {msg.timestamp.isoformat()}
[b]Level:[/b] [{level_color}]{level_name}[/{level_color}]
[b]Node:[/b] {msg.name}
[b]Message:[/b] {msg.msg}

[b]Source Info:[/b]
  File: {msg.file or 'N/A'}
  Function: {msg.function or 'N/A'}
  Line: {msg.line or 'N/A'}
"""
        self.update(details)

    def clear_details(self):
        """Clear the details display"""
        self.selected_message = None
        self.update("Logs cleared")
