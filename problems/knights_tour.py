from typing import Any, Iterable, Tuple, List
from problems.base_problem import Problem

class KnightsTourProblem(Problem):
    MOVES = [(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)]

    def __init__(self, n: int, start=(0,0)):
        self.n = n
        self.start = start
        self.total = n * n
        self.prefilled = None

    def initial_state(self):
        return [self.start]  

    def is_goal(self, state: List[tuple]) -> bool:
        return len(state) == self.total

    def in_bounds(self, r:int, c:int) -> bool:
        return 0 <= r < self.n and 0 <= c < self.n

    def successors(self, state: List[tuple]) -> Iterable[Tuple[List[tuple], float]]:
        r,c = state[-1]
        visited = set(state)
        
        possible_moves = []
        for dr,dc in self.MOVES:
            nr, nc = r+dr, c+dc
            if self.in_bounds(nr,nc) and (nr,nc) not in visited:
                onward_moves = 0
                for dr2, dc2 in self.MOVES:
                    nr2, nc2 = nr + dr2, nc + dc2
                    if self.in_bounds(nr2, nc2) and (nr2, nc2) not in visited:
                        onward_moves += 1
                possible_moves.append((onward_moves, (nr, nc)))
        
        possible_moves.sort(key=lambda x: x[0])
        
        for _, (nr, nc) in possible_moves:
            yield state + [(nr,nc)], 1.0

    def heuristic(self, state: List[tuple]) -> float:
        
        if len(state) == self.total:
            return 0.0  
        
        r, c = state[-1]
        visited = set(state)
        accessibility_sum = 0
        
        for dr, dc in self.MOVES:
            nr, nc = r + dr, c + dc
            if self.in_bounds(nr, nc) and (nr, nc) not in visited:
                onward_moves = 0
                for dr2, dc2 in self.MOVES:
                    nr2, nc2 = nr + dr2, nc + dc2
                    if self.in_bounds(nr2, nc2) and (nr2, nc2) not in visited and (nr2, nc2) != (r, c):
                        onward_moves += 1
                accessibility_sum += onward_moves
        
        return -accessibility_sum

    def prefill(self, path: Any) -> None:
        if path is None:
            self.prefilled = None
            return
        if isinstance(path, (list, tuple)):
            self.prefilled = [tuple(p) for p in path]
            return
        self.prefilled = path

    def prefill_level(self, level: float) -> None:
        if level <= 0.0:
            self.prefilled = None
            return
        k = max(1, round(self.total * level))
        path = [tuple(self.start)]
        for _ in range(k - 1):
            r, c = path[-1]
            moved = False
            for dr, dc in self.MOVES:
                nr, nc = r + dr, c + dc
                if self.in_bounds(nr, nc) and (nr, nc) not in path:
                    path.append((nr, nc))
                    moved = True
                    break
            if not moved:
                break
        self.prefilled = path

    def set_state(self, state: Any) -> None:
        if state is None:
            self.prefilled = None
        else:
            self.prefilled = [tuple(p) for p in state]

    def to_dict(self) -> dict:
        return {"params": {"n": self.n, "start": list(self.start)}, "state": getattr(self, "prefilled", None)}

    @classmethod
    def from_dict(cls, d: dict):
        p = cls(int(d["params"]["n"]), start=tuple(d["params"].get("start", (0, 0))))
        if d.get("state") is not None:
            p.prefill(d["state"])
        return p

    def validate_solution(self, solution: Any) -> tuple[bool, str]:
        if solution is None:
            return False, "Solution empty"
        if not isinstance(solution, (list, tuple)):
            return False, "Solution should be a list of positions"
        visited = set()
        prev = None
        for idx, pos in enumerate(solution):
            if not (isinstance(pos, (list, tuple)) and len(pos) == 2):
                return False, f"Invalid position at index {idx}: {pos}"
            r, c = int(pos[0]), int(pos[1])
            if not self.in_bounds(r, c):
                return False, f"Position {pos} out of bounds"
            if (r, c) in visited:
                return False, f"Position {pos} repeated"
            if prev is not None:
                dr, dc = abs(r - prev[0]), abs(c - prev[1])
                if (dr, dc) not in [(2,1),(1,2)]:
                    return False, f"Illegal knight move from {prev} to {(r,c)}"
            visited.add((r, c))
            prev = (r, c)
        return True, ""
