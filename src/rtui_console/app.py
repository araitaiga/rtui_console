"""
Main application for ROS2 Console Viewer
"""
from datetime import datetime
import os
import queue
from typing import Optional

from textual import on
from textual.app import App
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.containers import Vertical
from textual.widgets import Button
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import Input
from textual.widgets import Select

from .events import LevelFilterChanged
from .events import LogMessageSelected
from .events import LogsCleared
from .events import NodeSelected
from .events import TestLogsGenerated
from .events import TextFilterChanged
from .models import LogLevel
from .models import LogMessage
from .ros_client import LogGenerator
from .ros_client import ROS2Client
from .widgets import ControlPanel
from .widgets import LogDetailPanel
from .widgets import LogLevelPanel
from .widgets import LogTablePanel
from .widgets import NodeTreePanel
from .widgets import TextFilterPanel


class ConsoleApp(App):
    """Main TUI application following rtui design patterns"""

    CSS = """
    Screen {
        layout: vertical;
    }

    .container {
        height: 100%;
        background: $panel;
    }

    #left-panel {
        width: 30%;
        layout: vertical;
    }

    NodeTreePanel {
        padding: 0 1;
        height: 40%;
    }

    LogLevelPanel {
        padding: 0 1;
        height: 30%;
        border-top: inner $primary;
    }

    TextFilterPanel {
        padding: 0 1;
        height: 30%;
        border-top: inner $primary;
    }

    #main {
        border-left: inner $primary;
        width: 70%;
    }

    LogTablePanel {
        height: 70%;
        border-bottom: inner $primary;
    }

    LogDetailPanel {
        height: 30%;
        padding: 1 2;
    }

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

    TITLE = "ROS2 Console Viewer"
    BINDINGS = [
        Binding("r", "reload", "Reload", key_display="r"),
        Binding("c", "clear", "Clear", key_display="c"),
        Binding("p", "toggle_pause", "Pause/Resume", key_display="p"),
        Binding("t", "test_logs", "Test Logs", key_display="t"),
        Binding("q", "quit", "Quit", key_display="q"),
    ]

    def __init__(self):
        super().__init__()
        self.log_queue = queue.Queue(maxsize=10000)
        self.paused = False

        # ROS2 client
        self.ros_client = ROS2Client(self.log_queue)

        # UI Components
        self.node_tree_panel = NodeTreePanel(id="node_tree")
        self.log_level_panel = LogLevelPanel(id="log_level")
        self.text_filter_panel = TextFilterPanel(id="text_filter")
        self.log_table_panel = LogTablePanel(id="log_table")
        self.log_detail_panel = LogDetailPanel(id="log_detail")
        self.control_panel = ControlPanel(id="controls")

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(classes="container"):
            with Vertical(id="left-panel"):
                yield self.node_tree_panel
                yield self.log_level_panel
                yield self.text_filter_panel

            with Vertical(id="main"):
                yield self.log_table_panel
                yield self.log_detail_panel

        yield self.control_panel
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the application"""
        # Check ROS2 environment
        self._check_ros_environment()

        # Start ROS2 subscriber if available
        if self.ros_client.is_available():
            success = self.ros_client.start_subscriber()
            if not success:
                self.notify("Failed to start ROS2 subscriber",
                            severity="error")
        else:
            self.notify(
                "ROS2 packages not found. Use 'Test Logs' button or 't' key to try the interface.",
                severity="warning",
                timeout=10
            )

        # Start periodic update of UI
        self.set_interval(0.1, self._update_logs)

    def _check_ros_environment(self):
        """Check ROS2 environment setup"""
        env_ok, message = self.ros_client.check_environment()
        if env_ok:
            self.notify(message, timeout=3)
        else:
            self.notify(message, severity="warning", timeout=5)

    def _update_logs(self):
        """Update log display from queue"""
        if self.paused:
            return

        # Process new messages from queue
        new_messages = []
        nodes = set()

        while True:
            try:
                log_msg = self.log_queue.get_nowait()
                new_messages.append(log_msg)
                nodes.add(log_msg.name)
            except queue.Empty:
                break

        if new_messages:
            # Update node tree
            all_nodes = set()
            for msg in self.log_table_panel.log_messages + new_messages:
                all_nodes.add(msg.name)
            self.node_tree_panel.update_nodes(all_nodes)

            # Add messages to table
            for msg in new_messages:
                self.log_table_panel.add_log_message(msg)

    # Event Handlers (rtui pattern)
    def on_node_selected(self, event: NodeSelected) -> None:
        """Handle node selection from tree"""
        self.log_table_panel.set_node_filter(event.node_name)

    def on_log_message_selected(self, event: LogMessageSelected) -> None:
        """Handle log message selection from table"""
        self.log_detail_panel.set_message(event.log_message)

    def on_logs_cleared(self, event: LogsCleared) -> None:
        """Handle logs cleared event"""
        self.log_detail_panel.clear_details()
        self.node_tree_panel.update_nodes(set())

    def on_test_logs_generated(self, event: TestLogsGenerated) -> None:
        """Handle test logs generated event"""
        self.notify(f"Generated {event.count} test logs")

    def on_level_filter_changed(self, event: LevelFilterChanged) -> None:
        """Handle log level filter change"""
        if event.level == "ALL":
            self.log_table_panel.set_level_filter(LogLevel.DEBUG)
        else:
            self.log_table_panel.set_level_filter(int(event.level))

    def on_text_filter_changed(self, event: TextFilterChanged) -> None:
        """Handle text filter change"""
        self.log_table_panel.set_text_filter(event.text)

    @on(Button.Pressed, "#pause_btn")
    def on_pause_pressed(self) -> None:
        """Handle pause/resume button"""
        self.action_toggle_pause()

    @on(Button.Pressed, "#clear_btn")
    def on_clear_pressed(self) -> None:
        """Handle clear button"""
        self.action_clear()

    @on(Button.Pressed, "#test_btn")
    def on_test_pressed(self) -> None:
        """Handle test logs button"""
        self.action_test_logs()

    @on(Button.Pressed, "#save_btn")
    def on_save_pressed(self) -> None:
        """Handle save button"""
        self.save_logs()

    # Actions (rtui pattern)
    def action_reload(self) -> None:
        """Reload/refresh logs"""
        # Could implement reconnection logic here
        self.notify("Reload functionality not yet implemented")

    def action_clear(self) -> None:
        """Clear all logs"""
        self.log_table_panel.clear_logs()
        self.post_message(LogsCleared())
        self.notify("Logs cleared")

    def action_toggle_pause(self) -> None:
        """Toggle pause/resume"""
        self.paused = not self.paused
        self.control_panel.update_pause_button(self.paused)
        status = "paused" if self.paused else "resumed"
        self.notify(f"Log reception {status}")

    def action_test_logs(self) -> None:
        """Generate test logs"""
        count = LogGenerator.generate_test_logs(self.log_queue)
        self.post_message(TestLogsGenerated(count))

    def save_logs(self):
        """Save filtered logs to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ros_logs_{timestamp}.txt"

        try:
            with open(filename, 'w') as f:
                for msg in self.log_table_panel.filtered_messages:
                    level_name = LogLevel.NAMES.get(msg.level, "UNKNOWN")
                    f.write(
                        f"{msg.timestamp.isoformat()} [{level_name}] {msg.name}: {msg.msg}\n")

            self.notify(f"Logs saved to {filename}")
        except Exception as e:
            self.notify(f"Error saving logs: {e}", severity="error")

    def get_stats(self) -> dict:
        """Get application statistics"""
        return {
            "total_logs": self.log_table_panel.get_total_count(),
            "filtered_logs": self.log_table_panel.get_filtered_count(),
            "ros_status": self.ros_client.get_status(),
            "paused": self.paused,
            "nodes_count": len(self.node_tree_panel.nodes)
        }
