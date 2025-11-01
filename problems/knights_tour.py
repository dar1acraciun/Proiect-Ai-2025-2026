from typing import Any, Iterable, Tuple, List
from problems.base_problem import Problem

# Reprezentare: state = (r, c, visited_set (frozenset of positions))
# or simpler: path list of positions [(r,c), ...]

class KnightsTourProblem(Problem):
    MOVES = [(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)]

    def __init__(self, n: int, start=(0,0)):
        self.n = n
        self.start = start
        self.total = n * n

    def initial_state(self):
        return [self.start]  # path: list of positions, first is start

    def is_goal(self, state: List[tuple]) -> bool:
        return len(state) == self.total

    def in_bounds(self, r:int, c:int) -> bool:
        return 0 <= r < self.n and 0 <= c < self.n

    def successors(self, state: List[tuple]) -> Iterable[Tuple[List[tuple], float]]:
        r,c = state[-1]
        visited = set(state)
        for dr,dc in self.MOVES:
            nr, nc = r+dr, c+dc
            if self.in_bounds(nr,nc) and (nr,nc) not in visited:
                yield state + [(nr,nc)], 1.0

    def heuristic(self, state: List[tuple]) -> float:
        # Warnsdorff-like: prefer states with more visited
        return -len(state)
