from typing import Any, Iterable, Tuple
from problems.base_problem import Problem

class GeneralizedHanoi(Problem):
    def __init__(self, num_towers: int, num_disks: int, target_tower: int = 2, initial_positions: Tuple[int, ...] = None):
        assert num_towers >= 3
        assert 1 <= target_tower <= num_towers
        self.num_towers = num_towers
        self.num_disks = num_disks
        self.target_tower = target_tower
        if initial_positions is not None:
            if len(initial_positions) != num_disks:
                raise ValueError("initial_positions length must equal num_disks")
            if not all(1 <= p <= num_towers for p in initial_positions):
                raise ValueError("initial_positions entries must be between 1 and num_towers (inclusive)")
            self._initial_positions = tuple(int(p) for p in initial_positions)
        else:
            self._initial_positions = None

    def initial_state(self) -> Tuple[int, ...]:
        if getattr(self, "prefilled", None) is not None:
            st = list(self.prefilled)
            if len(st) != self.num_disks:
                st = (st + [1] * self.num_disks)[: self.num_disks]
            return tuple([self.num_towers] + st)

       
        if self._initial_positions is not None:
            return tuple([self.num_towers] + list(self._initial_positions))

        
        return tuple([self.num_towers] + [1] * self.num_disks)

    def is_goal(self, state: Tuple[int, ...]) -> bool:
        n = state[0]
        disk_positions = state[1:]
        return all(t == self.target_tower for t in disk_positions)

    def successors(self, state: Tuple[int, ...]) -> Iterable[Tuple[Tuple[int, ...], float]]:
        n = state[0]
        towers = {i: [] for i in range(1, n + 1)}
        disks = state[1:]


        for disk_num, tower in enumerate(disks, start=1):
            towers[tower].append(disk_num)

        for i in range(1, n + 1):
            if not towers[i]:
                continue
            moving_disk = towers[i][0]  
            for j in range(1, n + 1):
                if i == j:
                    continue
                if not towers[j] or moving_disk < towers[j][0]: 
                    new_disks = list(disks)
                    new_disks[moving_disk - 1] = j
                    yield tuple([n] + new_disks), 1.0

    def heuristic(self, state: Tuple[int, ...]) -> float:
        disks = state[1:]
        not_on_target = sum(1 for t in disks if t != self.target_tower)
        return -not_on_target

    
    def prefill(self, positions: Any) -> None:
        if positions is None:
            self.prefilled = None
            return

        
        if isinstance(positions, (list, tuple)) and len(positions) == self.num_disks + 1:
            positions = list(positions)[1:]

        if isinstance(positions, (list, tuple)):
            pos_list = list(positions)
            if len(pos_list) < self.num_disks:
                pos_list = pos_list + [1] * (self.num_disks - len(pos_list))
            for p in pos_list:
                if not (1 <= int(p) <= self.num_towers):
                    raise ValueError(f"Disk position {p} out of range 1..{self.num_towers}")
            self.prefilled = pos_list
            return

        self.prefilled = positions

    def prefill_level(self, level: float) -> None:
        if level <= 0.0:
            self.prefilled = None
            return
        k = max(1, round(self.num_disks * level))
        pos = [self.target_tower if i < k else 1 for i in range(self.num_disks)]
        self.prefilled = pos

    def set_state(self, state: Any) -> None:
        if state is None:
            self.prefilled = None
            return
        if isinstance(state, tuple) and len(state) == self.num_disks + 1:
            self.prefilled = list(state[1:])
        elif isinstance(state, (list, tuple)) and len(state) == self.num_disks:
            self.prefilled = list(state)
        else:
            self.prefilled = state

    def to_dict(self) -> dict:
        return {"params": {"num_towers": self.num_towers, "num_disks": self.num_disks, "target_tower": self.target_tower},
                "state": getattr(self, "prefilled", None)}

    @classmethod
    def from_dict(cls, d: dict):
        p = cls(int(d["params"]["num_towers"]), int(d["params"]["num_disks"]), int(d["params"].get("target_tower", 2)))
        if d.get("state") is not None:
            p.prefill(d["state"])
        return p

    def validate_solution(self, solution: Any) -> tuple[bool, str]:
        """Validate a candidate state/solution. Accepts tuple state or list of positions."""
        if solution is None:
            return False, "Solution is empty"

        if isinstance(solution, tuple) and len(solution) == self.num_disks + 1:
            positions = list(solution[1:])
        elif isinstance(solution, (list, tuple)) and len(solution) == self.num_disks:
            positions = list(solution)
        else:
            return False, f"Unsupported solution format or wrong length (expected {self.num_disks})"

        for i, p in enumerate(positions, start=1):
            try:
                pv = int(p)
            except Exception:
                return False, f"Disk {i} has non-integer position {p}"
            if not (1 <= pv <= self.num_towers):
                return False, f"Disk {i} position {pv} out of bounds 1..{self.num_towers}"

        return True, ""
