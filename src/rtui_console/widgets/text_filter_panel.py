"""
Text filter panel widget
"""
from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Input
from textual.widgets import Label
from textual.widgets import Static

from ..events import TextFilterChanged


class TextFilterPanel(Static):
    """Left panel showing text filter input"""

    DEFAULT_CSS = """
    TextFilterPanel {
        padding: 1;
        width: 100%;
        height: 30%;
        border-top: inner $primary;
    }

    .filter-container {
        layout: vertical;
        height: 100%;
        width: 100%;
    }

    Input {
        width: 100%;
        margin-top: 1;
    }

    Label {
        width: 100%;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.filter_input = Input(
            placeholder="Filter by message content or node name...",
            id="text_filter_input"
        )

    def compose(self) -> ComposeResult:
        with Container(classes="filter-container"):
            yield Label("🔍 Text Filter", classes="filter-label")
            yield self.filter_input

    @on(Input.Changed, "#text_filter_input")
    def on_filter_input_changed(self, event: Input.Changed) -> None:
        """Handle filter input change"""
        self.post_message(TextFilterChanged(event.value))

    def clear_filter(self):
        """Clear the filter input"""
        self.filter_input.value = ""

    def set_filter_text(self, text: str):
        """Set filter text programmatically"""
        self.filter_input.value = text
