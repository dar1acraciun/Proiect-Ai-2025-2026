from typing import List
from utils.display import print_header
from problems.random_nash_generator import generate_balanced_nash_game


# ===============================
# INPUT VALIDATION
# ===============================

def get_matrix_dimension(name: str, default: int = 2, min_v: int = 2, max_v: int = 5) -> int:
    raw = input(f"Număr de {name} [{min_v}-{max_v}] (default {default}): ").strip()

    if raw == "":
        return default

    try:
        value = int(raw)
        if min_v <= value <= max_v:
            return value
        else:
            print(f"Valoare invalidă. Folosesc {default}.")
            return default
    except ValueError:
        print(f"Input invalid. Folosesc {default}.")
        return default


# ===============================
# HELPERS
# ===============================

def generate_strategy_names(prefix: str, count: int) -> List[str]:
    return [f"{prefix}{i+1}" for i in range(count)]


def print_matrix(matrix, rows, cols):
    print("\nMatricea de payoff-uri:\n")
    print(" " * 14 + " ".join(f"{c:^16}" for c in cols))
    for i, r in enumerate(rows):
        line = f"{r:<12} "
        for j in range(len(cols)):
            u1, u2 = matrix[i][j]
            line += f"({u1:>2},{u2:<2})".center(16)
        print(line)


def print_nash_results(equilibria, rows, cols, score, reason):
    print("\n" + "-" * 60)
    print("REZULTAT CORECT")
    print("-" * 60)

    if equilibria:
        print("Echilibre Nash pure:")
        for i, j in equilibria:
            print(f" - ({rows[i]}, {cols[j]})")
    else:
        print("Nu există echilibru Nash pur.")

    print(f"\nScorul tău: {score:.2f}%")
    print("Motiv:", reason)
    print("-" * 60)


# ===============================
# QUIZ ENTRY POINT
# ===============================

def run_nash_quiz():
    print_header("Quiz: Echilibru Nash Pur")

    # Ask user for matrix size
    rows_count = get_matrix_dimension("rânduri")
    cols_count = get_matrix_dimension("coloane")

    # Generate balanced random game
    matrix, equilibria = generate_balanced_nash_game(
        rows=rows_count,
        cols=cols_count
    )

    rows = generate_strategy_names("R", rows_count)
    cols = generate_strategy_names("C", cols_count)

    print_matrix(matrix, rows, cols)

    exists = len(equilibria) > 0
    user_ans = input("\nExistă echilibru Nash pur? (y/n): ").strip().lower()

    score = 0.0
    reason = ""

    # 50% — existence
    if (user_ans == 'y') == exists:
        score = 50.0
    else:
        reason = "Răspuns greșit privind existența echilibrului."
        print_nash_results(equilibria, rows, cols, score, reason)
        return

    # If Nash exists, ask strategy
    if exists:
        print("\nIntrodu strategiile pentru echilibru:")
        print("Strategii Player 1:", ", ".join(rows))
        print("Strategii Player 2:", ", ".join(cols))

        r = input("Player 1 (rând): ").strip()
        c = input("Player 2 (coloană): ").strip()

        try:
            ri = rows.index(r)
            ci = cols.index(c)

            if (ri, ci) in equilibria:
                score = 100.0
                reason = "Răspuns complet corect."
            else:
                score = 50.0
                reason = "Existența este corectă, dar strategia aleasă nu este echilibru Nash."
        except ValueError:
            score = 50.0
            reason = "Strategii introduse invalide."

    else:
        score = 100.0
        reason = "Corect: jocul nu are echilibru Nash pur."

    print_nash_results(equilibria, rows, cols, score, reason)
