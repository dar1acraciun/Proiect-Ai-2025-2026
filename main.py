from utils.io_utils import generate_question
from utils.timing import time_function
import algorithms.uninformed as uninformed
import algorithms.informed as informed
from problems.n_queens import NQueensProblem
from problems.hanoi import GeneralizedHanoi
from problems.graph_coloring import GraphColoringProblem
from problems.knights_tour import KnightsTourProblem
import random

# mapping nume algoritm -> funcție
ALGO_FUNCS = {
    "BFS": uninformed.bfs,
    "DFS": uninformed.dfs,
    "Uniform Cost": uninformed.uniform_cost,
    "IDDFS": uninformed.iddfs,
    "BKT": uninformed.backtracking,
    "Bidirectional": uninformed.bidirectional,  # note: generic bidirectional may be None for many problems
    "Greedy": informed.greedy,
    "Hill Climbing": informed.hill_climbing,
    "Simulated Annealing": informed.simulated_annealing,
    "Beam Search": informed.beam_search,
    "A*": informed.a_star
}

ALGO_LIST = list(ALGO_FUNCS.keys())


def choose_problem_and_instance(problem_name: str, prefill: bool = False, prefill_level: float = 0.0):
    # construct problem object from user params
    if problem_name == "N-Queens":
        n = int(input("Introduceți dimensiunea tablei (n, ex 8): "))
        prob = NQueensProblem(n)
    elif problem_name == "Generalized Hanoi":
        pegs = int(input("Număr de tije (>=3): "))
        discs = int(input("Număr de discuri: "))
        target = int(input(f"Peg țintă (1..{pegs}) default 2: ") or "2")
        prob = GeneralizedHanoi(pegs, discs, target)
    elif problem_name == "Graph Coloring":
        nodes = int(input("Număr de noduri: "))
        edges = int(input("Număr de muchii: "))
        # generați graf simplu random
        graph = {i:set() for i in range(nodes)}
        attempts = 0
        while attempts < edges:
            a,b = random.sample(range(nodes),2)
            if b not in graph[a]:
                graph[a].add(b); graph[b].add(a)
                attempts += 1
        colors = int(input("Număr de culori disponibile: "))
        prob = GraphColoringProblem(graph, colors)
    elif problem_name == "Knight’s Tour":
        size = int(input("Dimensiune tablă (n): "))
        start_r = int(input("Start row (0-index): ") or "0")
        start_c = int(input("Start col (0-index): ") or "0")
        prob = KnightsTourProblem(size, start=(start_r, start_c))
    else:
        raise ValueError("Problemă necunoscută")

    # apply automatic prefill if requested
    if prefill and hasattr(prob, "prefill_level"):
        try:
            prob.prefill_level(prefill_level)
        except Exception as e:
            print(f"Eroare la aplicare prefill: {e}")

    return prob

def benchmark_all_algos(problem):
    results = {}
    for name, func in ALGO_FUNCS.items():
        # unele funcții (bidirectional) sunt generice și pot fi None/nu aplicabile -> tratăm erorile
        try:
            # timpăm funcția (un timp limit? nu implementăm timeout here; doar măsurăm)
            _, t = time_function(func, problem)
            results[name] = t
        except Exception as e:
            results[name] = float('inf')
    return results

def main():
    print("=== Generator întrebări & benchmark algoritmi ===")
    q, problem_name = generate_question()
    print("\nÎntrebare generată:")
    print(q)
    choice = input("Generare instanță: [1] goală  [2] aproape completă validă (1/2) [1]: ").strip() or "1"
    if choice == "2":
        inp = input("Nivel prefill (0-100) default 90: ").strip()
        if inp == "":
            pct = 90.0
        else:
            try:
                pct = float(inp)
            except Exception:
                print("Valoare invalidă pentru nivel; folosesc 90%")
                pct = 90.0
        pct = max(0.0, min(100.0, pct))
        lvl = pct / 100.0
        print(f"Aplic prefill automat nivel {int(pct)}%")
        problem = choose_problem_and_instance(problem_name, prefill=True, prefill_level=lvl)
    else:
        problem = choose_problem_and_instance(problem_name, prefill=False, prefill_level=0.0)

    # show if a prefilled state was applied (if problem supports it)
    try:
        pre = getattr(problem, "prefilled", None)
        if pre is not None:
            print("Prefill aplicat (preview):", pre)
    except Exception:
        pass
# ...existing code...
    print("\nInstanță generată. Rulez benchmark pentru toți algoritmii (atenție: poate dura).")

    times = benchmark_all_algos(problem)
    # determină cel mai mic timp (ignora infinit)
    valid_times = {k:v for k,v in times.items() if v != float('inf')}
    best = min(valid_times, key=valid_times.get) if valid_times else None



    print("\nAlege algoritmul (scrie exact numele) pe care crezi că e cel mai potrivit:")
    for name in ALGO_LIST:
        print("  -", name)
    user_choice = input("Algoritm ales: ").strip()

    if user_choice not in ALGO_FUNCS:
        print("Algoritm invalid. Terminat.")
        return

    finite_values = [v for v in times.values() if v != float('inf')]
    best_time = min(finite_values)
    worst_time = max(finite_values)

    if user_choice == best:
        print("✅ Corect! Ai ales alg. cu cel mai mic timp. (Scorul tău: 100.00%)")
    else:
        user_time = times[user_choice]
        if user_time == float('inf'):
            user_score = "N/A"
        elif best_time == worst_time:
            user_score = "100.00%"
        else:
            user_score = f"{100 * (worst_time - user_time) / (worst_time - best_time):.2f}%"

        print(f"❌ Incorect. Ai ales {user_choice}, dar cel mai rapid a fost {best} cu {times[best]:.10f}s. (Scorul tău: {user_score})")

    print("\nTimpuri de execuție (sec):")

    # inf last
    sorted_times = sorted(times.items(), key=lambda kv: (kv[1] == float('inf'), kv[1]))

    for k, v in sorted_times:
        if v == float('inf'):
            s = "N/A"
            score = "N/A"
        else:
            if best_time == worst_time:
                norm = 100.0
            else:
                norm = 100 * (worst_time - v) / (worst_time - best_time)
            s = f"{v:.10f}"
            score = f"{norm:6.2f}%"

        print(f" - {k:<25s}: {s:>15s} | Scor: {score:>7s}")


if __name__ == "__main__":
    main()
