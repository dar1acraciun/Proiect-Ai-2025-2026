from utils.io_utils import generate_question
from utils.timing import time_function
import algorithms.uninformed as uninformed
import algorithms.informed as informed
from problems.n_queens import NQueensProblem
from problems.hanoi import GeneralizedHanoi
from problems.graph_coloring import GraphColoringProblem
from problems.knights_tour import KnightsTourProblem
import random
import time
import inspect

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
        if n > 12:
            print("Atenție: n mare poate duce la timpi mari de calcul pentru unele algoritmi. Voi folosi n=12.")
            n=12
        prob = NQueensProblem(n)
    elif problem_name == "Generalized Hanoi":
        pegs = int(input("Număr de tije (>=3): "))
        if pegs>5:
            print("Atenție: număr mare de tije poate duce la timpi mari de calcul pentru unele algoritmi. Voi folosi 5 tije.")
            pegs=5
        discs = int(input("Număr de discuri: "))
        if discs>6:
            print("Atenție: număr mare de discuri poate duce la timpi mari de calcul pentru unele algoritmi. Voi folosi 6 discuri.")
            discs=6
        target = int(input(f"Peg țintă (1..{pegs}) default 2: ") or "2")
        if not (1 <= target <= pegs):
            print(f"Peg țintă invalidă, folosesc 2.")
            target = 2
        prob = GeneralizedHanoi(pegs, discs, target)
    elif problem_name == "Graph Coloring":
        nodes = int(input("Număr de noduri: "))
        if nodes>10:
            print("Atenție: număr mare de noduri poate duce la timpi mari de calcul pentru unele algoritmi. Voi folosi 10 noduri.")
            nodes=10
        if nodes<2:
            print("Număr minim de noduri este 2, setez la 2.")
            nodes=2
        edges = int(input("Număr de muchii: "))
        max_possible_edges = nodes * (nodes - 1) // 2
        if edges > max_possible_edges:
            print(f"Număr de muchii prea mare pentru {nodes} noduri, setez la maxim {max_possible_edges}.")
            edges = max_possible_edges
        # generați graf simplu random
        graph = {i:set() for i in range(nodes)}
        attempts = 0
        while attempts < edges:
            a,b = random.sample(range(nodes),2)
            if b not in graph[a]:
                graph[a].add(b); graph[b].add(a)
                attempts += 1
        colors = int(input("Număr de culori disponibile: "))
        if colors>nodes:
            print("Limitez numărul de culori la numărul de noduri.")
            colors = nodes
        prob = GraphColoringProblem(graph, colors)
    elif problem_name == "Knight’s Tour":
        size = int(input("Dimensiune tablă (n): "))
        if size>6:
            print("Atenție: dimensiune mare a tablei poate duce la timpi mari de calcul pentru unele algoritmi. Voi folosi 6x6.")
            size=6
        start_r = int(input("Start row (0-index): ") or "0")
        start_c = int(input("Start col (0-index): ") or "0")
        if not (0 <= start_r < size and 0 <= start_c < size):
            print("Poziție de start invalidă, folosesc (0,0).")
            start_r, start_c = 0, 0
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
    per_algo_timeout = 25.0  # seconds
    node_cap = 10000
    step_cap = 5000

    for name, func in ALGO_FUNCS.items():
        start_time = time.perf_counter()
        try:
            if func is None:
                results[name] = float('inf')
                continue

            sig = None
            try:
                sig = inspect.signature(func)
            except Exception:
                sig = None

            try:
                if sig and 'max_nodes' in sig.parameters:
                    func(problem, max_nodes=node_cap)
                elif sig and 'max_steps' in sig.parameters:
                    func(problem, max_steps=step_cap)
                else:
                    func(problem)

                elapsed = time.perf_counter() - start_time
                if elapsed > per_algo_timeout:
                    print(f"⏱️  {name} a depășit {per_algo_timeout}s — marchez ca N/A.")
                    results[name] = float('inf')
                else:
                    results[name] = round(elapsed, 3)

            except Exception as e:
                print(f"❌  Eroare în {name}: {e}")
                results[name] = float('inf')

        except Exception as outer:
            print(f"❌  Eroare externă la {name}: {outer}")
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
        # If the problem supports manual editing of the prefill preview, offer to let the user modify it.
        try:
            pre = getattr(problem, "prefilled", None)
            if pre is not None:
                print("Prefill aplicat (preview):", pre)
                edit = input("Dorești să editezi manual preview-ul? (y/N): ").strip().lower()
                if edit == 'y':
                    while True:
                        raw = input("Introdu pozițiile discurilor separate prin virgula (ex: 2,2,2,1,...). Poți da mai puține valori; restul vor fi completate cu 1: ").strip()
                        if not raw:
                            print("Input gol — renunț la edit.")
                            break
                        try:
                            parts = [int(x.strip()) for x in raw.split(',') if x.strip() != '']
                        except Exception:
                            print("Format invalid — încearcă din nou.")
                            continue
                        # attempt to apply prefill; prefill will validate ranges and pad if needed
                        try:
                            problem.prefill(parts)
                        except Exception as e:
                            print(f"Prefill invalid: {e}")
                            cont = input("Reîncerci? (y/N): ").strip().lower()
                            if cont == 'y':
                                continue
                            else:
                                break
                        # perform stacking check: build towers and ensure ordering
                        disks = getattr(problem, 'prefilled')
                        pegs_count = problem.num_towers
                        towers = {i: [] for i in range(1, pegs_count + 1)}
                        for disk_num, tower in enumerate(disks, start=1):
                            towers[tower].append(disk_num)
                        bad = False
                        for t, lst in towers.items():
                            if lst != sorted(lst):
                                print(f"Problema: pe peg {t} ordinea discurilor nu este validă: {lst}")
                                bad = True
                        if bad:
                            cont = input("Prefill generat nu e legal. Reîncerci editarea? (y/N): ").strip().lower()
                            if cont == 'y':
                                continue
                            else:
                                # revert to earlier preview
                                problem.prefill(pre)
                                break
                        # accepted
                        print("Prefill actualizat (preview):", problem.prefilled)
                        break
        except Exception:
            pass
    else:
        problem = choose_problem_and_instance(problem_name, prefill=False, prefill_level=0.0)
    # if no manual edit path above printed preview, attempt to show any prefill applied
    try:
        pre2 = getattr(problem, "prefilled", None)
        if pre2 is not None:
            print("Prefill aplicat (preview):", pre2)
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
