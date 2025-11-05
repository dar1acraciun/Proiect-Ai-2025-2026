import time
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


def _pretty_print_hanoi(state, problem):
    """Print towers for a GeneralizedHanoi state in a readable way."""
    if state is None:
        print("   (no state to show)")
        return
    # accept tuple (n, p1, p2, ...) or plain positions list
    if isinstance(state, tuple) and len(state) == problem.num_disks + 1:
        positions = list(state[1:])
    elif isinstance(state, (list, tuple)) and len(state) == problem.num_disks:
        positions = list(state)
    else:
        print("   (cannot pretty-print: unsupported state format)")
        return

    towers = {i: [] for i in range(1, problem.num_towers + 1)}
    for disk_num, tower in enumerate(positions, start=1):
        towers[int(tower)].append(disk_num)

    for t in range(1, problem.num_towers + 1):
        print(f"   Peg {t}: {towers[t]}")


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
        colors = int(input("Număr de culori disponibile: "))
        
        # Generate a k-colorable graph by partitioning nodes into color classes
        # and adding edges only between different color classes
        graph = {i: set() for i in range(nodes)}
        
        # Partition nodes into color classes
        color_classes = [[] for _ in range(colors)]
        for node in range(nodes):
            color_classes[node % colors].append(node)
        
        # Add random edges between different color classes (guaranteed to be colorable)
        attempts = 0
        max_attempts = edges * 10  # avoid infinite loop if edge budget is unrealistic
        while attempts < edges and attempts < max_attempts:
            # Pick two different color classes
            c1, c2 = random.sample(range(colors), 2)
            if color_classes[c1] and color_classes[c2]:
                # Pick one node from each
                n1 = random.choice(color_classes[c1])
                n2 = random.choice(color_classes[c2])
                if n2 not in graph[n1]:
                    graph[n1].add(n2)
                    graph[n2].add(n1)
                    attempts += 1
        
        print(f"Generated {attempts} edges (requested {edges})")
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
    validity = {}  # track which solutions are valid
    # per-algorithm timeout (seconds) to avoid extremely long runs on hard instances
    # If an algorithm takes longer than this, record it as N/A and continue.
    per_algo_timeout = 30.0
    # per-algorithm node/step caps for algorithms that accept these parameters
    # Different caps for different problem types
    if hasattr(problem, '__class__'):
        problem_class = problem.__class__.__name__
        if problem_class == 'GraphColoringProblem':
            node_cap = 100000
            step_cap = 100000
        elif problem_class == 'KnightsTourProblem':
            # Knight's Tour needs a very high cap
            # Even with Warnsdorff ordering, backtracking explores many nodes
            node_cap = 5000000  # 5 million nodes
            step_cap = 5000000
        else:
            node_cap = 10000
            step_cap = 5000
    else:
        node_cap = 10000
        step_cap = 5000
    import inspect

    # Local search algorithms that need a complete initial state
    local_search_algos = {"Hill Climbing", "Simulated Annealing", "Beam Search"}

    for name, func in ALGO_FUNCS.items():
        try:
            if func is None:
                results[name] = float('inf')
                validity[name] = False
                continue

            # For Graph Coloring with local search, create a 'local' mode variant
            algo_problem = problem
            if hasattr(problem, '__class__') and problem.__class__.__name__ == 'GraphColoringProblem':
                if name in local_search_algos:
                    # Create a local-mode version
                    from problems.graph_coloring import GraphColoringProblem
                    algo_problem = GraphColoringProblem(problem.graph, problem.colors, mode='local')
                    if problem.prefilled is not None:
                        algo_problem.prefill(problem.prefilled)
                else:
                    # Ensure path-finding uses 'path' mode
                    if hasattr(problem, 'mode') and problem.mode != 'path':
                        from problems.graph_coloring import GraphColoringProblem
                        algo_problem = GraphColoringProblem(problem.graph, problem.colors, mode='path')
                        if problem.prefilled is not None:
                            algo_problem.prefill(problem.prefilled)

            sig = None
            try:
                sig = inspect.signature(func)
            except Exception:
                sig = None

            # If the function accepts a max_nodes or max_steps parameter, call it directly
            # with conservative caps (avoids pickling/trampoline issues and enforces limits at algorithm level).
            if sig and 'max_nodes' in sig.parameters:
                t0 = time.perf_counter()
                try:
                    res = func(algo_problem, max_nodes=node_cap)
                except TypeError:
                    # some implementations may have different argument order — fallback
                    res = func(algo_problem)
                elapsed = time.perf_counter() - t0
                results[name] = elapsed
                # print result for debugging
                print(f"{name} returned {res} in {elapsed:.6f}s")
                # validate and pretty-print when possible
                try:
                    ok, reason = algo_problem.validate_solution(res)
                    validity[name] = ok
                except Exception as e:
                    print(f"  Validation: error validating result: {e}")
                    validity[name] = False
                else:
                    print(f"  Validation: {'OK' if ok else 'INVALID'}{': ' + reason if reason else ''}")
                    if ok and hasattr(algo_problem, 'num_towers'):
                        _pretty_print_hanoi(res, algo_problem)
                continue
            if sig and 'max_steps' in sig.parameters:
                t0 = time.perf_counter()
                try:
                    res = func(algo_problem, max_steps=step_cap)
                except TypeError:
                    res = func(algo_problem)
                elapsed = time.perf_counter() - t0
                results[name] = elapsed
                print(f"{name} returned {res} in {elapsed:.6f}s")
                try:
                    ok, reason = algo_problem.validate_solution(res)
                    validity[name] = ok
                except Exception as e:
                    print(f"  Validation: error validating result: {e}")
                    validity[name] = False
                else:
                    print(f"  Validation: {'OK' if ok else 'INVALID'}{': ' + reason if reason else ''}")
                    if ok and hasattr(algo_problem, 'num_towers'):
                        _pretty_print_hanoi(res, algo_problem)
                continue

            # otherwise fallback to the timeout-based runner which uses a subprocess when possible
            res, t = time_function(func, algo_problem, timeout=per_algo_timeout)
            results[name] = t
            if t == float('inf'):
                print(f"{name} timed out or errored: {res}")
                validity[name] = False
                # don't attempt validation when res is an error string or None
            else:
                print(f"{name} returned {res} in {t:.6f}s")
                try:
                    ok, reason = algo_problem.validate_solution(res)
                    validity[name] = ok
                except Exception as e:
                    print(f"  Validation: error validating result: {e}")
                    validity[name] = False
                else:
                    print(f"  Validation: {'OK' if ok else 'INVALID'}{': ' + reason if reason else ''}")
                    if ok and hasattr(algo_problem, 'num_towers'):
                        _pretty_print_hanoi(res, algo_problem)
        except Exception:
            results[name] = float('inf')
            validity[name] = False
    
    # Return both times and validity info
    return results, validity

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

    times, validity = benchmark_all_algos(problem)
    # determină cel mai rapid algoritm cu soluție validă (ignora infinit și invalid)
    valid_times = {k:v for k,v in times.items() if v != float('inf') and validity.get(k, False)}
    best = min(valid_times, key=valid_times.get) if valid_times else None



    print("\nAlege algoritmul (scrie exact numele) pe care crezi că e cel mai potrivit:")
    for name in ALGO_LIST:
        print("  -", name)
    user_choice = input("Algoritm ales: ").strip()

    if user_choice not in ALGO_FUNCS:
        print("Algoritm invalid. Terminat.")
        return

    # Only consider valid solutions for scoring
    finite_valid_times = [v for k, v in times.items() if v != float('inf') and validity.get(k, False)]
    if not finite_valid_times:
        print("⚠️  Niciun algoritm nu a găsit o soluție validă.")
        return
    
    best_time = min(finite_valid_times)
    worst_time = max(finite_valid_times)

    # Check if user's solution is valid
    user_is_valid = validity.get(user_choice, False)
    user_time = times[user_choice]

    if not user_is_valid:
        # Invalid or empty solution = 0% score
        print(f"❌ Ai ales {user_choice}, dar soluția este invalidă sau goală. (Scorul tău: 0.00%)")
    elif user_choice == best:
        print("✅ Corect! Ai ales alg. cu cel mai mic timp și soluție validă. (Scorul tău: 100.00%)")
    else:
        if best_time == worst_time:
            # All valid times are the same
            user_score = "100.00%"
        else:
            # Score = 100 * (worst - user_time) / (worst - best)
            # Capped at 100% to avoid scores > 100%
            score_val = 100 * (worst_time - user_time) / (worst_time - best_time)
            user_score = f"{min(100.0, score_val):.2f}%"

        print(f"❌ Incorect. Ai ales {user_choice}, dar cel mai rapid cu soluție validă a fost {best} cu {times[best]:.10f}s. (Scorul tău: {user_score})")

    print("\nTimpuri de execuție (sec):")

    # inf last, and invalid solutions shown as N/A
    sorted_times = sorted(times.items(), key=lambda kv: (kv[1] == float('inf'), kv[1]))

    for k, v in sorted_times:
        is_valid = validity.get(k, False)
        if v == float('inf') or not is_valid:
            s = "N/A"
            score = "N/A"
        else:
            if best_time == worst_time:
                norm = 100.0
            else:
                norm = 100 * (worst_time - v) / (worst_time - best_time)
                # Cap at 100%
                norm = min(100.0, norm)
            s = f"{v:.10f}"
            score = f"{norm:6.2f}%"

        print(f" - {k:<25s}: {s:>15s} | Scor: {score:>7s}")


if __name__ == "__main__":
    main()
