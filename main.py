# main.py - Simplified main entry point
import time
from utils.io_utils import generate_question
from utils.timing import time_function
from utils.display import (
    print_header, print_question, print_hanoi_towers, print_benchmark_results,
    print_instance_generated, print_prefill_options, get_algorithm_choice
)
from problems.minimax_quiz import run_minimax_quiz
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
    "Bidirectional": uninformed.bidirectional,
    "Greedy": informed.greedy,
    "Hill Climbing": informed.hill_climbing,
    "Simulated Annealing": informed.simulated_annealing,
    "Beam Search": informed.beam_search,
    "A*": informed.a_star
}

ALGO_LIST = list(ALGO_FUNCS.keys())

def _choose_problem_and_instance(problem_name: str, prefill: bool = False, prefill_level: float = 0.0):
    """Construct problem object from user params."""
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
        graph = {i: set() for i in range(nodes)}
        color_classes = [[] for _ in range(colors)]
        for node in range(nodes):
            color_classes[node % colors].append(node)
        attempts = 0
        max_attempts = edges * 10
        while attempts < edges and attempts < max_attempts:
            c1, c2 = random.sample(range(colors), 2)
            if color_classes[c1] and color_classes[c2]:
                n1 = random.choice(color_classes[c1])
                n2 = random.choice(color_classes[c2])
                if n2 not in graph[n1]:
                    graph[n1].add(n2)
                    graph[n2].add(n1)
                    attempts += 1
        print(f"Generated {attempts} edges (requested {edges})")
        prob = GraphColoringProblem(graph, colors)
    elif problem_name == "Knight's Tour":
        size = int(input("Dimensiune tablă (n): "))
        start_r = int(input("Start row (0-index): ") or "0")
        start_c = int(input("Start col (0-index): ") or "0")
        prob = KnightsTourProblem(size, start=(start_r, start_c))
    else:
        raise ValueError("Problemă necunoscută")
    
    if prefill and hasattr(prob, "prefill_level"):
        try:
            prob.prefill_level(prefill_level)
        except Exception as e:
            print(f"Eroare la aplicare prefill: {e}")
    
    return prob


def _benchmark_all_algos(problem):
    """Run all algorithms against problem; return (times_dict, validity_dict)."""
    results = {}
    validity = {}
    
    per_algo_timeout = 30.0
    
    if hasattr(problem, '__class__'):
        problem_class = problem.__class__.__name__
        if problem_class == 'GraphColoringProblem':
            node_cap = 100000
            step_cap = 100000
        elif problem_class == 'KnightsTourProblem':
            node_cap = 5000000
            step_cap = 5000000
        else:
            node_cap = 10000
            step_cap = 5000
    else:
        node_cap = 10000
        step_cap = 5000
    
    import inspect
    
    local_search_algos = {"Hill Climbing", "Simulated Annealing", "Beam Search"}
    
    for name, func in ALGO_FUNCS.items():
        try:
            if func is None:
                results[name] = float('inf')
                validity[name] = False
                continue
            
            algo_problem = problem
            if hasattr(problem, '__class__') and problem.__class__.__name__ == 'GraphColoringProblem':
                if name in local_search_algos:
                    from problems.graph_coloring import GraphColoringProblem
                    algo_problem = GraphColoringProblem(problem.graph, problem.colors, mode='local')
                    if hasattr(problem, 'prefilled') and problem.prefilled is not None:
                        algo_problem.prefill(problem.prefilled)
                else:
                    if hasattr(problem, 'mode') and problem.mode != 'path':
                        from problems.graph_coloring import GraphColoringProblem
                        algo_problem = GraphColoringProblem(problem.graph, problem.colors, mode='path')
                        if hasattr(problem, 'prefilled') and problem.prefilled is not None:
                            algo_problem.prefill(problem.prefilled)
            
            sig = None
            try:
                sig = inspect.signature(func)
            except Exception:
                sig = None
            
            if sig and 'max_nodes' in sig.parameters:
                t0 = time.perf_counter()
                try:
                    res = func(algo_problem, max_nodes=node_cap)
                except TypeError:
                    res = func(algo_problem)
                elapsed = time.perf_counter() - t0
                results[name] = elapsed
                print(f"{name} returned {res} in {elapsed:.6f}s")
                try:
                    ok, reason = algo_problem.validate_solution(res)
                    validity[name] = ok
                except Exception as e:
                    print(f" Validation: error validating result: {e}")
                    validity[name] = False
                else:
                    print(f" Validation: {'OK' if ok else 'INVALID'}{': ' + reason if reason else ''}")
                    if ok and hasattr(algo_problem, 'num_towers'):
                        print_hanoi_towers(res, algo_problem)
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
                    print(f" Validation: error validating result: {e}")
                    validity[name] = False
                else:
                    print(f" Validation: {'OK' if ok else 'INVALID'}{': ' + reason if reason else ''}")
                    if ok and hasattr(algo_problem, 'num_towers'):
                        print_hanoi_towers(res, algo_problem)
                continue
            
            res, t = time_function(func, algo_problem, timeout=per_algo_timeout)
            results[name] = t
            if t == float('inf'):
                print(f"{name} timed out or errored: {res}")
                validity[name] = False
            else:
                print(f"{name} returned {res} in {t:.6f}s")
                try:
                    ok, reason = algo_problem.validate_solution(res)
                    validity[name] = ok
                except Exception as e:
                    print(f" Validation: error validating result: {e}")
                    validity[name] = False
                else:
                    print(f" Validation: {'OK' if ok else 'INVALID'}{': ' + reason if reason else ''}")
                    if ok and hasattr(algo_problem, 'num_towers'):
                        print_hanoi_towers(res, algo_problem)
        except Exception:
            results[name] = float('inf')
            validity[name] = False
    
    return results, validity

def main():
    """Main quiz and benchmark flow."""
    print_header("Generator întrebări & benchmark algoritmi")
    q, problem_name = generate_question()
    print_question(q)

    # Check if this is a Minimax problem
    if problem_name == "MinMax":
        run_minimax_quiz()
        return

    # Determine prefill level
    choice = input("Generare instanță: [1] goală  [2] aproape completă validă (1/2) [1]: ").strip() or "1"
    if choice == "2":
        lvl = print_prefill_options()
        print(f"Aplic prefill automat nivel {int(lvl*100)}%")
        problem = _choose_problem_and_instance(problem_name, prefill=True, prefill_level=lvl)
        _handle_prefill_editing(problem)
    else:
        problem = _choose_problem_and_instance(problem_name, prefill=False, prefill_level=0.0)
    
    # Show prefill preview if applicable
    _show_prefill_preview(problem)
    
    # Run benchmark
    print_instance_generated()
    times, validity = _benchmark_all_algos(problem)
    
    # Get user's algorithm choice
    user_choice = get_algorithm_choice(ALGO_LIST)
    
    if user_choice not in ALGO_FUNCS:
        print("Algoritm invalid. Terminat.")
        return
    
    # Calculate and display results
    user_time = times[user_choice]
    user_is_valid = validity.get(user_choice, False)
    
    print_benchmark_results(times, validity, user_choice, user_time, user_is_valid, ALGO_LIST)


def _handle_prefill_editing(problem):
    """Handle manual editing of prefill if applicable."""
    try:
        pre = getattr(problem, "prefilled", None)
        if pre is not None:
            print("Prefill aplicat (preview):", pre)
            edit = input("Dorești să editezi manual preview-ul? (y/N): ").strip().lower()
            if edit == 'y':
                _interactive_prefill_edit(problem, pre)
    except Exception:
        pass


def _interactive_prefill_edit(problem, original_prefill):
    """Allow user to interactively edit prefill."""
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
        
        try:
            problem.prefill(parts)
        except Exception as e:
            print(f"Prefill invalid: {e}")
            cont = input("Reîncerci? (y/N): ").strip().lower()
            if cont == 'y':
                continue
            else:
                break
        
        # Validate stacking order
        if _validate_tower_stacking(problem):
            print("Prefill actualizat (preview):", problem.prefilled)
            break
        else:
            cont = input("Prefill generat nu e legal. Reîncerci editarea? (y/N): ").strip().lower()
            if cont == 'y':
                continue
            else:
                problem.prefill(original_prefill)
                break


def _validate_tower_stacking(problem):
    """Validate that disks are stacked correctly on towers."""
    disks = getattr(problem, 'prefilled')
    pegs_count = problem.num_towers
    towers = {i: [] for i in range(1, pegs_count + 1)}
    for disk_num, tower in enumerate(disks, start=1):
        towers[tower].append(disk_num)
    
    for t, lst in towers.items():
        if lst != sorted(lst):
            print(f"Problema: pe peg {t} ordinea discurilor nu este validă: {lst}")
            return False
    return True


def _show_prefill_preview(problem):
    """Show prefill preview if applicable."""
    try:
        pre = getattr(problem, "prefilled", None)
        if pre is not None:
            print("Prefill aplicat (preview):", pre)
    except Exception:
        pass


if __name__ == "__main__":
    main()
