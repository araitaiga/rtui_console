"""
Log level selection panel widget
"""
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.containers import Vertical
from textual.widgets import Checkbox
from textual.widgets import Label
from textual.widgets import Static

from ..events import LevelFilterChanged
from ..models import LogLevel


class LogLevelPanel(Static):
    """Left panel showing log levels with checkboxes for multi-selection"""

    DEFAULT_CSS = """
    LogLevelPanel {
        padding: 0;
        width: 100%;
        height: 100%;
    }

    ScrollableContainer {
        width: 100%;
        height: 100%;
        scrollbar-size: 1 1;
    }

    Checkbox {
        width: 100%;
        margin: 0;
    }

    .header-label {
        width: 100%;
        background: $accent;
        color: $text;
        padding: 0 1;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.selected_levels = {"ALL"}
        self.level_checkboxes = {}

    def compose(self) -> ComposeResult:
        with ScrollableContainer():
            with Vertical():
                yield Label("📊 Level Filter", classes="header-label")
                yield Checkbox("All Levels", value=True, id="level_all")

                # Add checkboxes for each log level
                levels = [
                    ("🔵 DEBUG", str(LogLevel.DEBUG)),
                    ("🟢 INFO", str(LogLevel.INFO)),
                    ("🟡 WARN", str(LogLevel.WARN)),
                    ("🔴 ERROR", str(LogLevel.ERROR)),
                    ("🟣 FATAL", str(LogLevel.FATAL))
                ]

                for display_name, level_value in levels:
                    checkbox = Checkbox(
                        display_name, value=False, id=f"level_{level_value}")
                    checkbox.level_value = level_value  # Store level value
                    self.level_checkboxes[level_value] = checkbox
                    yield checkbox

    @on(Checkbox.Changed)
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox state changes"""
        checkbox = event.checkbox

        if checkbox.id == "level_all":
            # All Levels checkbox toggled
            if checkbox.value:
                # Select all levels
                self.selected_levels = {"ALL"}
                for level_checkbox in self.level_checkboxes.values():
                    level_checkbox.value = False
            else:
                self.selected_levels = set()
        else:
            # Individual level checkbox toggled
            level_value = getattr(checkbox, 'level_value', None)
            if not level_value:
                return

            all_checkbox = self.query_one("#level_all", Checkbox)

            if checkbox.value:
                # Level selected
                self.selected_levels.discard("ALL")
                self.selected_levels.add(level_value)
                all_checkbox.value = False
            else:
                # Level deselected
                self.selected_levels.discard(level_value)

                # If no levels selected, select "All Levels"
                if not self.selected_levels:
                    self.selected_levels.add("ALL")
                    all_checkbox.value = True

        # Send updated selection
        self.post_message(LevelFilterChanged(list(self.selected_levels)))

    def get_selected_levels(self) -> set:
        """Get currently selected levels"""
        return self.selected_levels.copy()

    def clear_selection(self):
        """Clear all selections and select 'All Levels'"""
        self.selected_levels = {"ALL"}
        all_checkbox = self.query_one("#level_all", Checkbox)
        all_checkbox.value = True

        for checkbox in self.level_checkboxes.values():
            checkbox.value = False
