from typing import Any, Iterable, Tuple, List
from problems.base_problem import Problem
import random

class NQueensProblem(Problem):
    def __init__(self, n: int):
        self.n = n
        self.prefilled: List[int] | None = None

    def initial_state(self) -> List[int]:
        if getattr(self, "prefilled", None) is not None:
            return list(self.prefilled)
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
        
        return -len(state)

  
    def prefill(self, positions: Any) -> None:
        if positions is None:
            self.prefilled = None
            return

        if isinstance(positions, list) and positions and isinstance(positions[0], int):
            self.prefilled = list(positions)
            return

        
        if isinstance(positions, list) and positions and isinstance(positions[0], (list, tuple)):
            max_col = max(c for (_, c) in positions)
            arr: List[int | None] = [None] * (max_col + 1)
            for r, c in positions:
                arr[c] = r
            
            while arr and arr[-1] is None:
                arr.pop()
            self.prefilled = [x for x in arr if x is not None]
            return

        
        try:
            self.prefilled = list(positions)
        except Exception:
            self.prefilled = positions

    def prefill_level(self, level: float) -> None:
        if level <= 0.0:
            self.prefilled = None
            return
        k = max(1, round(self.n * level))
        
        # Generate a complete valid solution first
        complete_solution = self._find_valid_solution()
        
        if complete_solution:
            # Take first k placements from the valid solution
            self.prefilled = complete_solution[:k]
        else:
            # Fallback: greedy placement
            result: List[int] = []
            for col in range(self.n):
                if len(result) >= k:
                    break
                placed = False
                for row in range(self.n):
                    if self.valid_position(result, row, col):
                        result.append(row)
                        placed = True
                        break
                if not placed:
                    continue
            self.prefilled = result
    
    def _find_valid_solution(self) -> List[int] | None:
        """Find a complete valid N-Queens solution using backtracking."""
        def backtrack(col: int, state: List[int]) -> bool:
            if col == self.n:
                return True
            for row in range(self.n):
                if self.valid_position(state, row, col):
                    state.append(row)
                    if backtrack(col + 1, state):
                        return True
                    state.pop()
            return False
        
        solution: List[int] = []
        if backtrack(0, solution):
            return solution
        return None

    def set_state(self, state: Any) -> None:
        self.prefilled = list(state) if state is not None else None

    def to_dict(self) -> dict:
        return {"params": {"n": self.n}, "state": getattr(self, "prefilled", None)}

    @classmethod
    def from_dict(cls, d: dict):
        n = int(d["params"]["n"])
        p = cls(n)
        if d.get("state") is not None:
            p.prefill(d["state"])
        return p

    def validate_solution(self, solution: Any) -> tuple[bool, str]:
        if solution is None:
            return False, "Solution is empty"
        rows: List[int] | None = None
        if isinstance(solution, list) and solution and isinstance(solution[0], int):
            rows = solution 
        elif isinstance(solution, list) and solution and isinstance(solution[0], (list, tuple)):
            max_col = max(c for (_, c) in solution)
            arr: List[int | None] = [None] * (max_col + 1)
            for r, c in solution:
                if arr[c] is not None:
                    return False, f"Duplicate column {c}"
                arr[c] = r
            if len(arr) != self.n:
                return False, f"Solution covers {len(arr)} columns, expected {self.n}"
            rows = [x if x is not None else -1 for x in arr]  
        else:
            return False, "Unsupported solution format"

        if len(rows) != self.n:
            return False, f"Solution length {len(rows)} != n ({self.n})"
        for c, r in enumerate(rows):
            if not (0 <= r < self.n):
                return False, f"Row {r} out of bounds for column {c}"
            for c2, r2 in enumerate(rows):
                if c2 == c:
                    continue
                if r == r2 or abs(r - r2) == abs(c - c2):
                    return False, f"Conflict between col {c} and {c2}"
        return True, ""
