"""
Node tree panel widget
"""
from textual.app import ComposeResult
from textual.widgets import Static
from textual.widgets import Tree

from ..events import NodeSelected


class NodeTreePanel(Static):
    """Left panel showing ROS nodes in a tree structure"""

    DEFAULT_CSS = """
    NodeTreePanel {
        padding: 0;
        width: 100%;
        height: 40%;
    }

    Tree {
        width: 100%;
        scrollbar-size: 1 1;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.node_tree = Tree("ROS Nodes")
        self.node_tree.auto_expand = True
        self.nodes = set()

    def compose(self) -> ComposeResult:
        yield self.node_tree

    def update_nodes(self, nodes: set):
        """Update the node tree with new nodes"""
        if nodes == self.nodes:
            return

        self.nodes = nodes
        self.node_tree.clear()

        # Add "All Nodes" option
        all_node = self.node_tree.root.add("All Nodes", "ALL")

        # Group nodes by namespace (simple grouping)
        namespaces = {}
        for node in sorted(nodes):
            if '/' in node and node != '/':
                # Extract namespace
                parts = node.split('/')
                namespace = '/' + parts[1] if len(parts) > 2 else '/'
                if namespace not in namespaces:
                    namespaces[namespace] = []
                namespaces[namespace].append(node)
            else:
                if 'root' not in namespaces:
                    namespaces['root'] = []
                namespaces['root'].append(node)

        # Add nodes to tree
        for namespace, node_list in namespaces.items():
            if len(node_list) == 1 and namespace == 'root':
                # Single root node, add directly
                self.node_tree.root.add_leaf(node_list[0], node_list[0])
            else:
                # Multiple nodes or namespace, create group
                group_node = self.node_tree.root.add(namespace)
                for node in node_list:
                    group_node.add_leaf(node, node)

    def on_tree_node_selected(self, event: Tree.NodeSelected[str]) -> None:
        if event.node.is_root or event.node.data is None:
            return
        self.post_message(NodeSelected(event.node.data))
