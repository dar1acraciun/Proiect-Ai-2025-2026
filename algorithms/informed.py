import heapq
import random
import math
from typing import Any

def state_key(state):
    if isinstance(state, list):
        return tuple(state)          # list of positions → hashable tuple
    elif isinstance(state, dict):
        return tuple(sorted(state.items()))  # dict → sorted tuple of items
    return state  # already hashable

def greedy(problem, max_nodes=100000):
    start = problem.initial_state()
    pq = [(problem.heuristic(start), start)]
    visited = set()
    while pq:
        h, state = heapq.heappop(pq)
        if repr(state) in visited:
            continue
        visited.add(repr(state))
        if problem.is_goal(state):
            return state
        for neigh, _ in problem.successors(state):
            if repr(neigh) not in visited:
                heapq.heappush(pq, (problem.heuristic(neigh), neigh))
    return None

def hill_climbing(problem, max_steps=10000):
    state = problem.initial_state()
    steps = 0
    while steps < max_steps:
        if problem.is_goal(state):
            return state
        neighbors = list(problem.successors(state))
        if not neighbors:
            return None
        # eligible: neighbors with heuristic >= current (since we use negative for progress, adapt)
        cur_h = problem.heuristic(state)
        elig = [n for n,_ in neighbors if problem.heuristic(n) >= cur_h]
        if not elig:
            return None
        state = random.choice(elig)
        steps += 1
    return None

def simulated_annealing(problem, max_steps=5000):
    state = problem.initial_state()
    T0 = 1.0
    for t in range(1, max_steps+1):
        if problem.is_goal(state):
            return state
        neighs = [n for n,_ in problem.successors(state)]
        if not neighs:
            return None
        nxt = random.choice(neighs)
        cur_h = problem.heuristic(state)
        nxt_h = problem.heuristic(nxt)
        if nxt_h > cur_h:
            state = nxt
        else:
            # probability to accept worse moves
            T = T0 / math.log(2 + t)
            p = math.exp((nxt_h - cur_h) / T) if T > 0 else 0
            if random.random() < p:
                state = nxt
    return None

def beam_search(problem, k=3, max_iters=1000):
    start = problem.initial_state()
    beam = [start]
    visited = set([repr(start)])
    for _ in range(max_iters):
        if not beam:
            return None
        # check goal
        best = max(beam, key=lambda s: problem.heuristic(s))
        if problem.is_goal(best):
            return best
        new_beam = []
        candidates = []
        for state in beam:
            for neigh, _ in problem.successors(state):
                if repr(neigh) not in visited:
                    visited.add(repr(neigh))
                    candidates.append(neigh)
        # sort candidates by heuristic desc and keep top k
        candidates.sort(key=lambda s: problem.heuristic(s), reverse=True)
        beam = candidates[:k]
    return None

def a_star(problem, max_nodes=100_000):
    start = problem.initial_state()
    came_from = {}
    d = {state_key(start): 0.0}
    f = {state_key(start): problem.heuristic(start)}
    pq = [(f[state_key(start)], start)]
    visited = set()

    while pq:
        _, state = heapq.heappop(pq)
        k = state_key(state)
        if k in visited:
            continue
        visited.add(k)

        if problem.is_goal(state):
            return state

        for neigh, cost in problem.successors(state):
            nk = state_key(neigh)
            nd = d[k] + cost
            if nk not in d or nd < d[nk]:
                d[nk] = nd
                f[nk] = nd + problem.heuristic(neigh)
                came_from[nk] = state
                heapq.heappush(pq, (f[nk], neigh))

    return None
