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
        self._updating_ui = False  # Flag to prevent event loops

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
        # Skip if we're programmatically updating UI
        if self._updating_ui:
            return

        checkbox = event.checkbox

        if checkbox.id == "level_all":
            # All Levels checkbox toggled
            if checkbox.value:
                # Select all levels - clear individual selections
                self.selected_levels = {"ALL"}
                self._updating_ui = True
                for level_checkbox in self.level_checkboxes.values():
                    level_checkbox.value = False
                self._updating_ui = False
            else:
                # "All Levels" manually unchecked
                # Remove "ALL" from selection but keep individual levels
                self.selected_levels.discard("ALL")
        else:
            # Individual level checkbox toggled
            level_value = getattr(checkbox, 'level_value', None)
            if not level_value:
                return

            all_checkbox = self.query_one("#level_all", Checkbox)

            if checkbox.value:
                # Level selected - remove "ALL" and add specific level
                self.selected_levels.discard("ALL")
                self.selected_levels.add(level_value)
                # Safely update "All Levels" checkbox without triggering events
                self._updating_ui = True
                all_checkbox.value = False
                self._updating_ui = False
            else:
                # Level deselected
                self.selected_levels.discard(level_value)

                # If no levels selected, select "All Levels"
                if not self.selected_levels:
                    self.selected_levels.add("ALL")
                    self._updating_ui = True
                    all_checkbox.value = True
                    self._updating_ui = False

        # Send updated selection
        self.post_message(LevelFilterChanged(list(self.selected_levels)))
