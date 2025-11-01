from typing import Any, Iterable, Tuple, List
from problems.base_problem import Problem

# Reprezentare: state = list unde index = coloana și valoarea = rândul unde a fost pusă regina.
# De exemplu state = [1, 3, 0] înseamnă:
# - col 0 -> row 1, col1 -> row3, col2 -> row0
# Un state partial poate avea lungime < n.

class NQueensProblem(Problem):
    def __init__(self, n: int):
        self.n = n

    def initial_state(self) -> List[int]:
        return []  

    def is_goal(self, state: List[int]) -> bool:
        return len(state) == self.n

    def valid_position(self, state: List[int], row: int, col: int) -> bool:
        for c, r in enumerate(state):
            if r == row or abs(r - row) == abs(c - col):
                return False
        return True

    def successors(self, state: List[int]) -> Iterable[Tuple[List[int], float]]:
        col = len(state)
        for row in range(self.n):
            if self.valid_position(state, row, col):
                new_state = state + [row]
                yield new_state, 1.0

    def heuristic(self, state: List[int]) -> float:
        # heuristic: negative number of placed queens (mai multe e mai aproape de goal)
        return -len(state)
