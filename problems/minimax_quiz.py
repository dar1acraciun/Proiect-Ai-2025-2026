from problems.minimax_tree import MinimaxTreeProblem
from utils.display import print_minimax_tree, print_minimax_results


def run_minimax_quiz():
    print("\n=== Exercițiu MinMax + Alpha-Beta pruning ===")
    
    prob = _generate_random_tree()

    print("\nArborele generat:")
    print_minimax_tree(prob)
    print("\nÎntrebare:")
    print("Pentru arborele dat, care este valoarea de la rădăcină și câte noduri frunză vor fi evaluate aplicând MinMax cu Alpha-Beta?")
    print("Introduceți răspunsul sub formă de două numere întregi.")

    user_root, user_leaves = _get_user_answers()
    
    if user_root is None or user_leaves is None:
        return

    correct_root, correct_visited = prob.run_minimax_alphabeta()
    total_leaves = prob.total_leaves()

    score, reason = _calculate_minimax_score(
        user_root, user_leaves, correct_root, correct_visited, 
        total_leaves, prob.leaf_min, prob.leaf_max
    )

    print_minimax_results(user_root, user_leaves, correct_root, correct_visited, total_leaves, score, reason)


def _generate_random_tree() -> MinimaxTreeProblem:
    max_leaves = int(input("Număr maxim de frunze per nod ( >=2 default 2): ") or "2")
    max_leaves = max(2, max_leaves)  
    depth = int(input("Adâncime/nivele (default 3): ") or "3")
    low = int(input("Valoare frunză minimă (default -10): ") or "-10")
    high = int(input("Valoare frunză maximă (default 10): ") or "10")

    return MinimaxTreeProblem(
        branching=max_leaves,
        depth=depth,
        leaf_min=low, leaf_max=high
    )


def _get_user_answers() -> tuple:
    try:
        parts = input("Valoarea rădăcinii și nodurile frunză vizitate (ex: '5 10'): ").strip().split()
        if len(parts) >= 2:
            user_root = int(parts[0])
            user_leaves = int(parts[1])
        else:
            user_root = int(parts[0])
            user_leaves = int(input("Numărul de noduri frunză vizitate: ").strip())
        return user_root, user_leaves
    except Exception as e:
        print(f"Nu pot analiza input-ul: {e}. Renunț la exercițiu.")
        return None, None


def _calculate_minimax_score(user_root: int, user_leaves: int, correct_root: int, 
                            correct_visited: int, total_leaves: int, 
                            leaf_min: int, leaf_max: int) -> tuple:
   
    if user_root == correct_root and user_leaves == correct_visited:
        score = 100.0
        reason = "Răspuns exact pentru ambele valori (rădăcină și frunze vizitate)."
    else:
        score = 100.0
        reasons = []
        
       
        root_diff = abs(user_root - correct_root)
        root_correct = root_diff == 0
        if root_correct:
            reasons.append("Valoarea rădăcinii corectă.")
        else:
            
            score -= root_diff * 25.0
            reasons.append(f"Valoarea rădăcinii: așteptat {correct_root}, tu ai răspuns {user_root} (diferență: {root_diff}).")
        
    
        leaves_diff = abs(user_leaves - correct_visited)
        leaves_correct = leaves_diff == 0
        if leaves_correct:
            reasons.append("Numărul de frunze vizitate corect.")
        else:
            score -= leaves_diff * 25.0
            reasons.append(f"Frunze vizitate: așteptat {correct_visited}, tu ai răspuns {user_leaves} (diferență: {leaves_diff}).")
        
    
        if root_correct or leaves_correct:
            score = max(50.0, score)
        else:
            score = max(0.0, score)
        
        reason = " ".join(reasons)
    
    return score, reason
