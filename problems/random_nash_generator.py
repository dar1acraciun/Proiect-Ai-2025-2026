# problems/random_nash_generator.py

import random
from typing import List, Tuple

Payoff = Tuple[int, int]
Matrix = List[List[Payoff]]


def find_pure_nash(matrix: Matrix) -> list[tuple[int, int]]:
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


def generate_random_matrix(
    rows: int = 2,
    cols: int = 2,
    payoff_min: int = -5,
    payoff_max: int = 5
) -> Matrix:
    return [
        [
            (random.randint(payoff_min, payoff_max),
             random.randint(payoff_min, payoff_max))
            for _ in range(cols)
        ]
        for _ in range(rows)
    ]


def generate_matrix_with_nash(
    rows: int = 2,
    cols: int = 2,
    max_tries: int = 10_000
) -> tuple[Matrix, list[tuple[int, int]]]:

    for _ in range(max_tries):
        m = generate_random_matrix(rows, cols)
        eq = find_pure_nash(m)

        if eq:
            return m, eq

    raise RuntimeError("Nu am reușit să generez joc cu echilibru Nash.")


def generate_matrix_without_nash(
    rows: int = 2,
    cols: int = 2,
    max_tries: int = 10_000
) -> Matrix:

    for _ in range(max_tries):
        m = generate_random_matrix(rows, cols)
        eq = find_pure_nash(m)

        if not eq:
            return m

    raise RuntimeError("Nu am reușit să generez joc fără echilibru Nash.")



def generate_balanced_nash_game(
    rows: int = 2,
    cols: int = 2,
    prob_with_nash: float = 0.5
) -> tuple[Matrix, list[tuple[int, int]]]:

    if random.random() < prob_with_nash:
        return generate_matrix_with_nash(rows, cols)
    else:
        m = generate_matrix_without_nash(rows, cols)
        return m, []


def pretty_print_matrix(matrix: Matrix):
    print("\nMatrice payoff:")
    for row in matrix:
        print(" ".join(f"{cell!s:>8}" for cell in row))


if __name__ == "__main__":
    for _ in range(5):
        m, eq = generate_balanced_nash_game()
        pretty_print_matrix(m)
        print("Echilibre Nash:", eq or "NU EXISTA")
        print("-" * 40)
