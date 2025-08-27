"""
Control panel widget
"""
from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Button
from textual.widgets import Static


class ControlPanel(Static):
    """Control panel with buttons and filters"""

    DEFAULT_CSS = """
    ControlPanel {
        height: auto;
        padding: 1 2;
        border-top: inner $primary;
    }

    .controls-row {
        layout: horizontal;
        height: auto;
        margin: 1 0;
    }

    .control-item {
        margin: 0 1;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.paused = False

    def compose(self) -> ComposeResult:
        with Container(classes="controls-row"):
            yield Button("Pause", id="pause_btn", variant="primary", classes="control-item")
            yield Button("Clear", id="clear_btn", variant="warning", classes="control-item")
            yield Button("Test Logs", id="test_btn", variant="success", classes="control-item")
            yield Button("Load File", id="load_btn", classes="control-item")
            yield Button("Save", id="save_btn", classes="control-item")

    def update_pause_button(self, paused: bool):
        """Update pause button state"""
        self.paused = paused
        try:
            pause_btn = self.query_one("#pause_btn", Button)
            pause_btn.label = "Resume" if paused else "Pause"
            pause_btn.variant = "warning" if paused else "primary"
        except:
            pass  # Button not found or not mounted yet
