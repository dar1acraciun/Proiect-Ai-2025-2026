from typing import Any, Iterable, Tuple
from problems.base_problem import Problem

# Representation:
# state = (n, t1, t2, ..., tm)
# where n = number of towers, and ti is the tower index (1..n) where disk i is placed.
# Disks are numbered 1..m (1 = smallest, m = largest).

class GeneralizedHanoi(Problem):
    def __init__(self, num_towers: int, num_disks: int, target_tower: int = 2):
        assert num_towers >= 3
        assert 1 <= target_tower <= num_towers
        self.num_towers = num_towers
        self.num_disks = num_disks
        self.target_tower = target_tower

    def initial_state(self) -> Tuple[int, ...]:
        # all disks start on tower 1
        return tuple([self.num_towers] + [1] * self.num_disks)

    def is_goal(self, state: Tuple[int, ...]) -> bool:
        n = state[0]
        disk_positions = state[1:]
        return all(t == self.target_tower for t in disk_positions)

    def successors(self, state: Tuple[int, ...]) -> Iterable[Tuple[Tuple[int, ...], float]]:
        n = state[0]
        towers = {i: [] for i in range(1, n + 1)}
        disks = state[1:]

        # build towers content (top = smallest disk last in list)
        for disk_num, tower in enumerate(disks, start=1):
            towers[tower].append(disk_num)

        # for each tower with disks, move top disk to another tower if legal
        for i in range(1, n + 1):
            if not towers[i]:
                continue
            moving_disk = towers[i][0]  # smallest disk on that tower (since appended in order)
            for j in range(1, n + 1):
                if i == j:
                    continue
                if not towers[j] or moving_disk < towers[j][0]:  # legal move
                    new_disks = list(disks)
                    new_disks[moving_disk - 1] = j
                    yield tuple([n] + new_disks), 1.0

    def heuristic(self, state: Tuple[int, ...]) -> float:
        # simple heuristic: number of disks not on target tower
        disks = state[1:]
        not_on_target = sum(1 for t in disks if t != self.target_tower)
        return -not_on_target
