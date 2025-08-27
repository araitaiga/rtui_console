"""
Node tree panel widget
"""
import time

from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.containers import Vertical
from textual.widgets import Checkbox
from textual.widgets import Label
from textual.widgets import Static

from ..events import NodeSelected


class NodeTreePanel(Static):
    """Left panel showing ROS nodes with checkboxes for multi-selection"""

    DEFAULT_CSS = """
    NodeTreePanel {
        padding: 1;
        width: 100%;
        height: 100%;
        background: $surface;
        display: block;
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
        self.nodes = set()
        self.selected_nodes = set(["ALL"])
        self.node_checkboxes = {}

    def compose(self) -> ComposeResult:
        with ScrollableContainer():
            with Vertical():
                yield Label("🔧 Node Filter", classes="header-label")
                yield Checkbox("All Nodes", value=True, id="node_all")
                # Add initial dummy nodes to ensure panel is visible
                yield Checkbox("rtui_console_subscriber", value=False, id="node_debug_1")
                yield Checkbox("mission_manager_node", value=False, id="node_debug_2")

    def update_nodes(self, nodes: set):
        """Update the node checkboxes with new nodes"""
        if nodes == self.nodes:
            return

        self.nodes = nodes

        # Get container for mounting new checkboxes
        container = self.query_one(Vertical)

        # Remove existing node checkboxes safely
        for node_name in list(self.node_checkboxes.keys()):
            checkbox = self.node_checkboxes[node_name]
            try:
                checkbox.remove()
            except Exception:
                pass  # Widget might already be removed
        self.node_checkboxes.clear()

        # Add checkboxes for each node with guaranteed unique IDs
        for i, node in enumerate(sorted(nodes)):
            # Use timestamp + index to ensure unique IDs across updates
            unique_id = f"node_{i}_{int(time.time() * 1000000) % 1000000}"

            checkbox = Checkbox(node, value=False, id=unique_id)
            checkbox.node_name = node  # Store node name as attribute
            self.node_checkboxes[node] = checkbox
            container.mount(checkbox)

    @on(Checkbox.Changed)
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox state changes"""
        checkbox = event.checkbox

        if checkbox.id == "node_all":
            # All Nodes checkbox toggled
            if checkbox.value:
                # Select all nodes
                self.selected_nodes = {"ALL"}
                for node_checkbox in self.node_checkboxes.values():
                    node_checkbox.value = False
                # Also uncheck debug nodes
                try:
                    self.query_one("#node_debug_1", Checkbox).value = False
                    self.query_one("#node_debug_2", Checkbox).value = False
                except:
                    pass
            else:
                self.selected_nodes = set()
        else:
            # Individual node checkbox toggled
            node_name = getattr(checkbox, 'node_name', checkbox.label.plain)
            all_checkbox = self.query_one("#node_all", Checkbox)

            if checkbox.value:
                # Node selected
                self.selected_nodes.discard("ALL")
                self.selected_nodes.add(node_name)
                all_checkbox.value = False
            else:
                # Node deselected
                self.selected_nodes.discard(node_name)

                # If no nodes selected, select "All Nodes"
                if not self.selected_nodes:
                    self.selected_nodes.add("ALL")
                    all_checkbox.value = True

        # Send updated selection
        self.post_message(NodeSelected(list(self.selected_nodes)))

    def get_selected_nodes(self) -> set:
        """Get currently selected nodes"""
        return self.selected_nodes.copy()

    def clear_selection(self):
        """Clear all selections and select 'All Nodes'"""
        self.selected_nodes = {"ALL"}
        all_checkbox = self.query_one("#node_all", Checkbox)
        all_checkbox.value = True

        for checkbox in self.node_checkboxes.values():
            checkbox.value = False
