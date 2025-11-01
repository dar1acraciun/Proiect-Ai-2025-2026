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
