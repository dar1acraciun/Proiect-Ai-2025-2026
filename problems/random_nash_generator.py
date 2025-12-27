# problems/random_nash_generator.py

import random
from typing import List, Tuple

Payoff = Tuple[int, int]
Matrix = List[List[Payoff]]


# ===============================
# PURE NASH DETECTION
# ===============================

def find_pure_nash(matrix: Matrix) -> List[Tuple[int, int]]:
    rows = len(matrix)
    cols = len(matrix[0])
    equilibria = []

    for i in range(rows):
        for j in range(cols):
            u1, u2 = matrix[i][j]

            best_u1 = max(matrix[r][j][0] for r in range(rows))
            best_u2 = max(matrix[i][c][1] for c in range(cols))

            if u1 == best_u1 and u2 == best_u2:
                equilibria.append((i, j))

    return equilibria


# ===============================
# RANDOM MATRIX
# ===============================

def generate_random_matrix(
    rows: int,
    cols: int,
    payoff_min: int,
    payoff_max: int
) -> Matrix:
    return [
        [
            (random.randint(payoff_min, payoff_max),
             random.randint(payoff_min, payoff_max))
            for _ in range(cols)
        ]
        for _ in range(rows)
    ]


# ===============================
# BALANCED GENERATORS
# ===============================

def generate_matrix_with_nash(
    rows: int,
    cols: int,
    payoff_min: int,
    payoff_max: int,
    max_tries: int = 10_000
) -> tuple[Matrix, List[Tuple[int, int]]]:

    for _ in range(max_tries):
        m = generate_random_matrix(rows, cols, payoff_min, payoff_max)
        eq = find_pure_nash(m)
        if eq:
            return m, eq

    raise RuntimeError("Nu am reușit să generez joc cu echilibru Nash.")


def generate_matrix_without_nash(
    rows: int,
    cols: int,
    payoff_min: int,
    payoff_max: int,
    max_tries: int = 10_000
) -> Matrix:

    for _ in range(max_tries):
        m = generate_random_matrix(rows, cols, payoff_min, payoff_max)
        if not find_pure_nash(m):
            return m

    raise RuntimeError("Nu am reușit să generez joc fără echilibru Nash.")


# ===============================
# PUBLIC API (USED BY QUIZ)
# ===============================

def generate_balanced_nash_game(
    rows: int = 2,
    cols: int = 2,
    payoff_min: int = -5,
    payoff_max: int = 5,
    prob_with_nash: float = 0.5
) -> tuple[Matrix, List[Tuple[int, int]]]:

    if random.random() < prob_with_nash:
        return generate_matrix_with_nash(rows, cols, payoff_min, payoff_max)
    else:
        matrix = generate_matrix_without_nash(rows, cols, payoff_min, payoff_max)
        return matrix, []
