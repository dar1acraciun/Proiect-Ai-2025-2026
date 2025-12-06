"""Minimax tree problem generator and solver."""
import random
from typing import Tuple, Union

Node = Union[int, list]  # leaf is int, internal node is list of children


class MinimaxTreeProblem:
    """Generate a minimax tree for exercises."""

    def __init__(
        self,
        branching: int = 2,
        depth: int = 3,
        leaf_min: int = -10,
        leaf_max: int = 10,
    ):
        """Initialize tree with random generation."""
        self.branching = max(1, int(branching))
        self.depth = max(1, int(depth))
        self.leaf_min = int(leaf_min)
        self.leaf_max = int(leaf_max)
        self.root = self._generate_node(self.depth)

    def _generate_node(self, depth: int) -> Node:
        """Recursively generate a tree node with guaranteed depth."""
        if depth == 1:
            return random.randint(self.leaf_min, self.leaf_max)
        # Ensure at least 2 children to maintain depth (except at deepest level)
        min_children = 2 if depth > 1 else 1
        num_children = random.randint(min_children, self.branching)
        return [self._generate_node(depth - 1) for _ in range(num_children)]

    def run_minimax_alphabeta(self) -> Tuple[int, int]:
        """
        Run Minimax with Alpha-Beta pruning on the tree.
        Returns: (root_value, leaf_nodes_visited)
        """

        def max_value(node, alpha, beta) -> Tuple[int, int]:
            if isinstance(node, int):
                return node, 1
            v = -10**18
            total_visited = 0
            for child in node:
                child_val, child_vis = min_value(child, alpha, beta)
                total_visited += child_vis
                if child_val > v:
                    v = child_val
                if v >= beta:
                    return v, total_visited
                if v > alpha:
                    alpha = v
            return v, total_visited

        def min_value(node, alpha, beta) -> Tuple[int, int]:
            if isinstance(node, int):
                return node, 1
            v = 10**18
            total_visited = 0
            for child in node:
                child_val, child_vis = max_value(child, alpha, beta)
                total_visited += child_vis
                if child_val < v:
                    v = child_val
                if v <= alpha:
                    return v, total_visited
                if v < beta:
                    beta = v
            return v, total_visited

        root_val, leaves = max_value(self.root, -10**18, 10**18)
        return root_val, leaves

    def total_leaves(self) -> int:
        """Count total leaves in the tree."""
        def rec(node):
            if isinstance(node, int):
                return 1
            return sum(rec(c) for c in node)
        return rec(self.root)
