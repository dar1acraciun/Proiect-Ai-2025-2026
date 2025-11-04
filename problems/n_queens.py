from typing import Any, Iterable, Tuple, List
from problems.base_problem import Problem
import random

# Reprezentare: state = list unde index = coloana și valoarea = rândul unde a fost pusă regina.
# De exemplu state = [1, 3, 0] înseamnă:
# - col 0 -> row 1, col1 -> row3, col2 -> row0
# Un state partial poate avea lungime < n.

class NQueensProblem(Problem):
    def __init__(self, n: int):
        self.n = n
        # optional prefilled state: list of rows per column (length <= n)
        self.prefilled: List[int] | None = None

    def initial_state(self) -> List[int]:
        # If a prefilled partial state exists, return a shallow copy so callers
        # don't accidentally mutate the stored prefill.
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
        # heuristic: negative number of placed queens (mai multe e mai aproape de goal)
        return -len(state)

    # --- optional hooks for instance generation / validation / serialization ---

    def prefill(self, positions: Any) -> None:
        """
        Accepts either:
         - list of ints => interpreted as rows for columns 0..k-1
         - list of (row,col) tuples => converted to list indexed by column
        Stores result in self.prefilled.
        """
        if positions is None:
            self.prefilled = None
            return

        if isinstance(positions, list) and positions and isinstance(positions[0], int):
            self.prefilled = list(positions)
            return

        # list of tuples (r,c)
        if isinstance(positions, list) and positions and isinstance(positions[0], (list, tuple)):
            max_col = max(c for (_, c) in positions)
            arr: List[int | None] = [None] * (max_col + 1)
            for r, c in positions:
                arr[c] = r
            # trim trailing None
            while arr and arr[-1] is None:
                arr.pop()
            # type: ignore[attr-defined]
            self.prefilled = [x for x in arr if x is not None]
            return

        # fallback: try to coerce if possible
        try:
            self.prefilled = list(positions)
        except Exception:
            # store raw if nothing else works
            self.prefilled = positions

    def prefill_level(self, level: float) -> None:
        """Greedy prefill: place k = round(n * level) queens by columns left-to-right.
        Ensures no conflicts among placed queens.
        """
        if level <= 0.0:
            self.prefilled = None
            return
        k = max(1, round(self.n * level))
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
                # can't place in this column without conflict; skip column
                continue
        self.prefilled = result

    def set_state(self, state: Any) -> None:
        # expected as list of rows
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
        """
        Validate a candidate solution.
        Accepts either list of rows length n, or list of (r,c) tuples.
        Returns (True, "") if valid else (False, reason).
        """
        if solution is None:
            return False, "Solution is empty"
        rows: List[int] | None = None
        if isinstance(solution, list) and solution and isinstance(solution[0], int):
            rows = solution  # type: ignore[assignment]
        elif isinstance(solution, list) and solution and isinstance(solution[0], (list, tuple)):
            max_col = max(c for (_, c) in solution)
            arr: List[int | None] = [None] * (max_col + 1)
            for r, c in solution:
                if arr[c] is not None:
                    return False, f"Duplicate column {c}"
                arr[c] = r
            # ensure full length n
            if len(arr) != self.n:
                return False, f"Solution covers {len(arr)} columns, expected {self.n}"
            # convert
            rows = [x if x is not None else -1 for x in arr]  # type: ignore[assignment]
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
