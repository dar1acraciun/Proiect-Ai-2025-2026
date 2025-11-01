from collections import deque
import heapq
from typing import Any, Dict, Iterable, Tuple, List, Callable, Optional, Set
import math

# Algorithms implementate generic pentru Problem (folosesc metoda successors/is_goal/heuristic/distance)
# Acceptă un obiect problem cu interfața din base_problem.

def bfs(problem, max_nodes: int = 10_000):
    start = problem.initial_state()
    q = deque([start])
    visited = set()
    def key(s): return repr(s)
    while q and len(visited) < max_nodes:
        state = q.popleft()
        if key(state) in visited:
            continue
        visited.add(key(state))
        if problem.is_goal(state):
            return state
        for neigh, _ in problem.successors(state):
            if key(neigh) not in visited:
                q.append(neigh)
    return None

def dfs(problem, max_nodes: int = 10_000):
    start = problem.initial_state()
    stack = [start]
    visited = set()
    def key(s): return repr(s)
    while stack and len(visited) < max_nodes:
        state = stack.pop()
        if key(state) in visited:
            continue
        visited.add(key(state))
        if problem.is_goal(state):
            return state
        for neigh, _ in problem.successors(state):
            if key(neigh) not in visited:
                stack.append(neigh)
    return None

def uniform_cost(problem, max_nodes: int = 100000):
    start = problem.initial_state()
    d = {repr(start): 0.0}
    pq = [(0.0, start)]
    visited = set()
    while pq:
        dist, state = heapq.heappop(pq)
        key = repr(state)
        if key in visited:
            continue
        visited.add(key)
        if problem.is_goal(state):
            return state
        for neigh, cost in problem.successors(state):
            nk = repr(neigh)
            nd = dist + cost
            if nk not in d or nd < d[nk]:
                d[nk] = nd
                heapq.heappush(pq, (nd, neigh))
    return None

def iddfs(problem, max_depth=20):
    def dls(state, depth, visited):
        if problem.is_goal(state):
            return state
        if depth == 0:
            return None
        for neigh, _ in problem.successors(state):
            key = repr(neigh)
            if key in visited:
                continue
            visited.add(key)
            res = dls(neigh, depth-1, visited)
            if res is not None:
                return res
            visited.remove(key)
        return None

    for depth in range(max_depth+1):
        visited = set()
        start = problem.initial_state()
        visited.add(repr(start))
        res = dls(start, depth, visited)
        if res is not None:
            return res
    return None

def backtracking(problem, max_nodes=100000):
    # classic backtracking (BKT)
    nodes = 0
    def bt(partial):
        nonlocal nodes
        nodes += 1
        if nodes > max_nodes:
            return None
        if problem.is_goal(partial):
            return partial
        for neigh, _ in problem.successors(partial):
            res = bt(neigh)
            if res is not None:
                return res
        return None
    return bt(problem.initial_state())

def bidirectional(problem, reverse_state_generator=None, max_nodes=100000):
    # Implementare generică: încercăm doar dacă problem poate fi "reversed" (user may provide reverse generator)
    if reverse_state_generator is None:
        # nu putem face bidirectional generic fără reverser
        return None
    start = problem.initial_state()
    goal_states = []
    # Încearcă să generezi un final posibil - pentru probleme cu final unic avem nevoie de un final cunoscut
    # Here we assume reverse_state_generator can give reversed neighbors from a final state
    f_q = deque([start]); b_q = deque([reverse_state_generator()])
    f_vis = {repr(start): None}
    b_vis = {repr(reverse_state_generator()): None}
    steps = 0
    while f_q and b_q and steps < max_nodes:
        steps += 1
        f_state = f_q.popleft()
        if repr(f_state) in b_vis:
            return f_state
        for neigh, _ in problem.successors(f_state):
            if repr(neigh) not in f_vis:
                f_vis[repr(neigh)] = f_state
                f_q.append(neigh)
        # backward side handled by reverse_state_generator externally (not generic)
        return None
