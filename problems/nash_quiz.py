from typing import List
from utils.display import print_header
from problems.random_nash_generator import generate_balanced_nash_game


# ===============================
# INPUT VALIDATION
# ===============================

def get_int_input(prompt: str, default: int, min_v: int, max_v: int) -> int:
    raw = input(prompt).strip()
    if raw == "":
        return default
    try:
        val = int(raw)
        if min_v <= val <= max_v:
            return val
    except ValueError:
        pass
    print(f"Valoare invalidă. Folosesc {default}.")
    return default


def get_difficulty() -> str:
    print("\nAlege dificultatea:")
    print("  1 - Ușor")
    print("  2 - Mediu")
    print("  3 - Greu")

    choice = input("Opțiune (1/2/3) [2]: ").strip()

    return {
        "1": "easy",
        "2": "medium",
        "3": "hard"
    }.get(choice, "medium")


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
            line += f"({u1:>3},{u2:<3})".center(16)
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
# DIFFICULTY SETTINGS
# ===============================

def difficulty_settings(diff: str):
    if diff == "easy":
        return dict(
            rows=2,
            cols=2,
            payoff_min=-3,
            payoff_max=3,
            prob_nash=0.7
        )
    if diff == "hard":
        return dict(
            rows=get_int_input("Număr rânduri [3-5] (default 4): ", 4, 3, 5),
            cols=get_int_input("Număr coloane [3-5] (default 4): ", 4, 3, 5),
            payoff_min=-10,
            payoff_max=10,
            prob_nash=0.3
        )
    # medium (default)
    return dict(
        rows=get_int_input("Număr rânduri [2-3] (default 2): ", 2, 2, 3),
        cols=get_int_input("Număr coloane [2-3] (default 2): ", 2, 2, 3),
        payoff_min=-5,
        payoff_max=5,
        prob_nash=0.5
    )


# ===============================
# QUIZ ENTRY POINT
# ===============================

def run_nash_quiz():
    print_header("Quiz: Echilibru Nash Pur")

    difficulty = get_difficulty()
    settings = difficulty_settings(difficulty)

    matrix, equilibria = generate_balanced_nash_game(
        rows=settings["rows"],
        cols=settings["cols"],
        payoff_min=settings["payoff_min"],
        payoff_max=settings["payoff_max"],
        prob_with_nash=settings["prob_nash"]
    )

    rows = generate_strategy_names("R", settings["rows"])
    cols = generate_strategy_names("C", settings["cols"])

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
