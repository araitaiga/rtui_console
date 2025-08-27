"""
Custom filter tab panel widget
"""
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.widgets import Button
from textual.widgets import Static


class FilterTabPanel(Static):
    """Custom tab panel for filters with manual tab switching"""

    DEFAULT_CSS = """
    FilterTabPanel {
        width: 100%;
        height: 100%;
        layout: vertical;
        background: $panel;
        border: inner $primary;
    }

    .tab-buttons {
        layout: grid;
        grid-size: 3 1;
        height: 3;
        width: 100%;
        background: $boost;
    }

    .tab-button {
        height: 3;
        width: 100%;
        margin: 0;
        padding: 0;
        text-align: center;
    }

    .tab-button.active {
        background: $accent;
        color: $text;
    }

    .tab-content {
        height: 1fr;
        width: 100%;
        overflow: hidden;
    }

    .tab-panel {
        width: 100%;
        height: 100%;
        display: none;
    }

    .tab-panel.active {
        display: block;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.current_tab = "nodes"
        self.node_tree_panel = None
        self.log_level_panel = None
        self.text_filter_panel = None

    def set_panels(self, node_tree_panel, log_level_panel, text_filter_panel):
        """Set the filter panels"""
        self.node_tree_panel = node_tree_panel
        self.log_level_panel = log_level_panel
        self.text_filter_panel = text_filter_panel

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal(classes="tab-buttons"):
                yield Button("🔧 Nodes", id="tab-btn-nodes", classes="tab-button active")
                yield Button("📊 Levels", id="tab-btn-levels", classes="tab-button")
                yield Button("🔍 Text", id="tab-btn-text", classes="tab-button")

            with Vertical(classes="tab-content"):
                yield Static(classes="tab-panel active", id="panel-nodes")
                yield Static(classes="tab-panel", id="panel-levels")
                yield Static(classes="tab-panel", id="panel-text")

    def on_mount(self) -> None:
        """Mount panels after the widget is mounted"""
        if self.node_tree_panel:
            self.query_one("#panel-nodes").mount(self.node_tree_panel)
        if self.log_level_panel:
            self.query_one("#panel-levels").mount(self.log_level_panel)
        if self.text_filter_panel:
            self.query_one("#panel-text").mount(self.text_filter_panel)

    @on(Button.Pressed, ".tab-button")
    def on_tab_button_pressed(self, event: Button.Pressed) -> None:
        """Handle tab button presses"""
        button_id = event.button.id

        if button_id == "tab-btn-nodes":
            self.switch_to_tab("nodes")
        elif button_id == "tab-btn-levels":
            self.switch_to_tab("levels")
        elif button_id == "tab-btn-text":
            self.switch_to_tab("text")

    def switch_to_tab(self, tab_name: str):
        """Switch to the specified tab"""
        if tab_name == self.current_tab:
            return

        # Update button states
        for button_id in ["tab-btn-nodes", "tab-btn-levels", "tab-btn-text"]:
            try:
                button = self.query_one(f"#{button_id}", Button)
                if button_id == f"tab-btn-{tab_name}":
                    button.add_class("active")
                else:
                    button.remove_class("active")
            except:
                pass

        # Update panel visibility
        panels = {
            "nodes": "panel-nodes",
            "levels": "panel-levels",
            "text": "panel-text"
        }

        for panel_name, panel_id in panels.items():
            try:
                panel = self.query_one(f"#{panel_id}", Static)
                if panel_name == tab_name:
                    panel.add_class("active")
                else:
                    panel.remove_class("active")
            except:
                pass

        self.current_tab = tab_name
