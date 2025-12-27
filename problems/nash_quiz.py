from typing import List, Tuple
from utils.display import print_header
from problems.random_nash_generator import generate_balanced_nash_game


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
    return {"1": "easy", "2": "medium", "3": "hard"}.get(choice, "medium")


def difficulty_settings(diff: str):
    if diff == "easy":
        return dict(rows=2, cols=2, payoff_min=-3, payoff_max=3, prob_nash=0.7)
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


def explain_cell(matrix, i, j, rows, cols) -> str:
    u1, u2 = matrix[i][j]

    # Best responses
    best_p1 = max(matrix[r][j][0] for r in range(len(matrix)))
    best_p2 = max(matrix[i][c][1] for c in range(len(matrix[0])))

    lines = []
    lines.append(f"Strategia ({rows[i]}, {cols[j]}) cu payoff ({u1}, {u2}):")

    if u1 == best_p1:
        lines.append(f" ✔ Player 1 NU poate îmbunătăți payoff-ul (max = {best_p1}).")
    else:
        better = [rows[r] for r in range(len(matrix)) if matrix[r][j][0] == best_p1]
        lines.append(f" ✘ Player 1 poate devia la {better} și obține {best_p1} > {u1}.")

    if u2 == best_p2:
        lines.append(f" ✔ Player 2 NU poate îmbunătăți payoff-ul (max = {best_p2}).")
    else:
        better = [cols[c] for c in range(len(matrix[0])) if matrix[i][c][1] == best_p2]
        lines.append(f" ✘ Player 2 poate devia la {better} și obține {best_p2} > {u2}.")

    if u1 == best_p1 and u2 == best_p2:
        lines.append(" ⇒ Aceasta ESTE un echilibru Nash pur.")
    else:
        lines.append(" ⇒ Aceasta NU este un echilibru Nash pur.")

    return "\n".join(lines)


def explain_equilibria(matrix, equilibria, rows, cols):
    print("\nEXPLICAȚII:")

    if equilibria:
        for i, j in equilibria:
            print("-" * 60)
            print(explain_cell(matrix, i, j, rows, cols))
    else:
        print("Niciun profil NU este echilibru Nash pur.")
        print("Pentru fiecare strategie, cel puțin un jucător are un stimulent să devieze.")



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
        explain_equilibria(matrix, equilibria, rows, cols)
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
                print("\nDe ce strategia aleasă NU este Nash:")
                print(explain_cell(matrix, ri, ci, rows, cols))
        except ValueError:
            score = 50.0
            reason = "Strategii introduse invalide."

    else:
        score = 100.0
        reason = "Corect: jocul nu are echilibru Nash pur."

    print_nash_results(equilibria, rows, cols, score, reason)
    explain_equilibria(matrix, equilibria, rows, cols)
