def print_header(title: str):
    print("=" * 60)
    print(title.center(60))
    print("=" * 60)


def print_question(question: str):
    print("\nÎntrebare generată:")
    print(question)


def print_hanoi_towers(state, problem):
    if state is None:
        print(" (no state to show)")
        return
    if isinstance(state, tuple) and len(state) == problem.num_disks + 1:
        positions = list(state[1:])
    elif isinstance(state, (list, tuple)) and len(state) == problem.num_disks:
        positions = list(state)
    else:
        print(" (cannot pretty-print: unsupported state format)")
        return
    towers = {i: [] for i in range(1, problem.num_towers + 1)}
    for disk_num, tower in enumerate(positions, start=1):
        towers[int(tower)].append(disk_num)
    for t in range(1, problem.num_towers + 1):
        print(f" Peg {t}: {towers[t]}")


def print_benchmark_results(times: dict, validity: dict, user_choice: str, user_time: float, 
                           user_is_valid: bool, algo_list: list):

    valid_times = {k: v for k, v in times.items() if v != float('inf') and validity.get(k, False)}
    
    if not valid_times:
        print("⚠️  Niciun algoritm nu a găsit o soluție validă.")
        return
    
    best = min(valid_times, key=valid_times.get)
    best_time = min(valid_times.values())
    worst_time = max(valid_times.values())
    
   
    print("\n" + "-" * 60)
    if not user_is_valid:
        print(f"❌ Ai ales {user_choice}, dar soluția este invalidă sau goală. (Scorul tău: 0.00%)")
    elif user_choice == best:
        print("✅ Corect! Ai ales alg. cu cel mai mic timp și soluție validă. (Scorul tău: 100.00%)")
    else:
        if best_time == worst_time:
            user_score = "100.00%"
        else:
            score_val = 100 * (worst_time - user_time) / (worst_time - best_time)
            user_score = f"{min(100.0, score_val):.2f}%"
        print(f"❌ Incorect. Ai ales {user_choice}, dar cel mai rapid cu soluție validă a fost {best} cu {times[best]:.10f}s. (Scorul tău: {user_score})")
    
    print("\n" + "-" * 60)
    print("Timpuri de execuție (sec):")
    print("-" * 60)
    
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
                norm = min(100.0, norm)
            s = f"{v:.10f}"
            score = f"{norm:6.2f}%"
        
        print(f" - {k:<25s}: {s:>15s} | Scor: {score:>7s}")
    print("-" * 60)


def print_minimax_results(user_root: int, user_leaves: int, correct_root: int, 
                         correct_visited: int, total_leaves: int, score: float, reason: str):
    print("\nRăspuns corect:")
    print(f" - Valoarea rădăcinii = {correct_root}")
    print(f" - Noduri frunză vizitate (Alpha-Beta) = {correct_visited} (total frunze în arbore = {total_leaves})")
    print(f"\nScorul tău: {score:.2f}%")
    print("Motiv:", reason)


def print_prefill_options():
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
    return pct / 100.0


def get_algorithm_choice(algo_list: list) -> str:
    print("\nAlege algoritmul (scrie exact numele) pe care crezi că e cel mai potrivit:")
    for name in algo_list:
        print("  -", name)
    return input("Algoritm ales: ").strip()


def print_instance_generated():
    print("\nInstanță generată. Rulez benchmark pentru toți algoritmii (atenție: poate dura).")


def print_minimax_tree(tree):
    print("\n" + "=" * 70)
    print("ARBORELE MINIMAX - STRUCTURĂ PE NIVELURI")
    print("=" * 70 + "\n")
    
    def rec(node, level=0, is_max=True, prefix=""):
        if isinstance(node, int):
           
            print(f"{prefix}FRUNZĂ: {node}")
        else:
            node_type = "MAX" if is_max else "MIN"
            child_count = len(node)
            
            if level == 0:
                print(f"RĂDĂCINĂ ({node_type})")
                new_prefix = ""
            else:
                print(f"{prefix}{node_type} (cu {child_count} copii)")
                new_prefix = prefix
            
            next_is_max = not is_max
            for i, child in enumerate(node):
                is_last = (i == len(node) - 1)
               
                if level == 0:
                    connector = "└─ " if is_last else "├─ "
                    child_prefix = connector
                else:
                    indent = "   " if is_last else "│  "
                    connector = "└─ " if is_last else "├─ "
                    child_prefix = new_prefix + indent + connector
                
                rec(child, level + 1, next_is_max, child_prefix)
    
    rec(tree.root, 0, True, "")
    print("\n" + "=" * 70 + "\n")
