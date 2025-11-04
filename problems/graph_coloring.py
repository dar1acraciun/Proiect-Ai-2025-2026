from typing import Any, Iterable, Tuple, Dict, List, Set
from problems.base_problem import Problem
import random

# Reprezentare: graph as adjacency dict {node: set(neighbors)}
# state: dict node->color or partial mapping

class GraphColoringProblem(Problem):
    def __init__(self, graph: Dict[int, Set[int]], colors: int):
        self.graph = graph
        self.colors = colors
        self.nodes = list(graph.keys())
        self.prefilled = None

    def initial_state(self) -> Dict[int,int]:
        return {}  # niciun nod colorat

    def is_goal(self, state: Dict[int,int]) -> bool:
        return len(state) == len(self.nodes)

    def valid_assignment(self, state: Dict[int,int], node: int, color: int) -> bool:
        for nb in self.graph[node]:
            if nb in state and state[nb] == color:
                return False
        return True

    def successors(self, state: Dict[int,int]) -> Iterable[Tuple[Dict[int,int], float]]:
        # aleg următorul nod necolorat (deterministic)
        uncolored = [n for n in self.nodes if n not in state]
        if not uncolored:
            return
        node = uncolored[0]
        for c in range(self.colors):
            if self.valid_assignment(state, node, c):
                new_state = state.copy()
                new_state[node] = c
                yield new_state, 1.0

    def heuristic(self, state: Dict[int,int]) -> float:
        # heuristic: -numarul de noduri colorate
        return -len(state)

    # ---- optional hooks ----
    def prefill(self, mapping: Any) -> None:
        """Accepts dict node->color or list of pairs; stores as dict."""
        if mapping is None:
            self.prefilled = None
            return
        if isinstance(mapping, dict):
            self.prefilled = {int(k): int(v) for k, v in mapping.items()}
            return
        # list of pairs
        if isinstance(mapping, (list, tuple)):
            d = {}
            for item in mapping:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    d[int(item[0])] = int(item[1])
            self.prefilled = d
            return
        # fallback
        self.prefilled = mapping

    def prefill_level(self, level: float) -> None:
        """Greedy color k = round(n_nodes * level) nodes.
        Colors chosen are the smallest valid color for each selected node.
        """
        if level <= 0.0:
            self.prefilled = None
            return
        k = max(1, round(len(self.nodes) * level))
        colored = {}
        # deterministic order for repeatability
        for node in self.nodes:
            if len(colored) >= k:
                break
            for c in range(self.colors):
                if self.valid_assignment(colored, node, c):
                    colored[node] = c
                    break
        self.prefilled = colored

    def set_state(self, state: Any) -> None:
        if state is None:
            self.prefilled = None
        elif isinstance(state, dict):
            self.prefilled = {int(k): int(v) for k, v in state.items()}
        else:
            self.prefilled = state

    def to_dict(self) -> dict:
        return {"params": {"graph": {k: list(v) for k, v in self.graph.items()}, "colors": self.colors},
                "state": getattr(self, "prefilled", None)}

    @classmethod
    def from_dict(cls, d: dict):
        graph_raw = d["params"]["graph"]
        graph = {int(k): set(v) for k, v in graph_raw.items()}
        p = cls(graph, int(d["params"]["colors"]))
        if d.get("state") is not None:
            p.prefill(d["state"])
        return p

    def validate_solution(self, solution: Any) -> tuple[bool, str]:
        if solution is None:
            return False, "Solution empty"
        if not isinstance(solution, dict):
            return False, "Solution should be dict node->color"
        for node, color in solution.items():
            if int(node) not in self.graph:
                return False, f"Unknown node {node}"
            c = int(color)
            if not (0 <= c < self.colors):
                return False, f"Color {c} out of range for node {node}"
            for nb in self.graph[int(node)]:
                if nb in solution and int(solution[nb]) == c:
                    return False, f"Edge conflict between {node} and {nb} with color {c}"
        return True, ""
