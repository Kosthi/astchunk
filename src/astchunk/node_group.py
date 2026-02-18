"""
NodeGroup: a virtual node that groups multiple sibling tree-sitter nodes
so the chunking algorithm treats them as a single unit.

Primary use case: binding decorators to their function/class definitions
to prevent semantic breaks during chunking.
"""

from __future__ import annotations

import tree_sitter as ts


class NodeGroup:
    """
    Groups multiple sibling ts.Nodes into a single virtual node.

    Quacks like a ts.Node for the purposes of the chunking algorithm:
    - has start_byte / end_byte spanning the full group
    - has children (the grouped nodes themselves, for recursive splitting)
    - has a type (the type of the last "real" node, e.g. function_definition)
    """

    def __init__(self, nodes: list[ts.Node]):
        assert len(nodes) > 0, "NodeGroup must contain at least one node"
        self._nodes = nodes

    @property
    def start_byte(self) -> int:
        return self._nodes[0].start_byte

    @property
    def end_byte(self) -> int:
        return self._nodes[-1].end_byte

    @property
    def start_point(self):
        return self._nodes[0].start_point

    @property
    def end_point(self):
        return self._nodes[-1].end_point

    @property
    def children(self) -> list[ts.Node]:
        """
        When the group needs recursive splitting, expose the individual
        nodes as children so each can be assigned to windows independently.
        """
        return self._nodes

    @property
    def type(self) -> str:
        """Return the type of the primary (last) node in the group."""
        return self._nodes[-1].type

    @property
    def text(self) -> bytes:
        """Reconstruct the full text span (may include gaps)."""
        # Fallback: concatenate the text of all nodes
        # In practice the chunking algorithm uses byte ranges, not this
        return b"\n".join(n.text for n in self._nodes)

    def __repr__(self) -> str:
        types = [n.type for n in self._nodes]
        return f"NodeGroup({types}, bytes={self.start_byte}..{self.end_byte})"
