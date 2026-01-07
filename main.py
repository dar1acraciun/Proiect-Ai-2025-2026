from utils.io_utils import generate_question
from utils.io_utils import OPTIMIZATIONS
from utils.display import *
from utils.problem_factory import create_problem_instance
from utils.prefill import handle_prefill_editing, show_prefill_preview
from utils.algorithm_runner import run_benchmark_all_algorithms
from problems.minimax_quiz import run_minimax_quiz
import algorithms.uninformed as uninformed
import algorithms.informed as informed
from problems.nash_quiz import run_nash_quiz
from problems.csp import *
import copy


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


def main():
   
    print_header("Generator întrebări & benchmark algoritmi")
    
    question, problem_name = generate_question()
    print_question(question)
    
    if problem_name == "MinMax":
        run_minimax_quiz()
        return
    
    if problem_name == "Nash":
        run_nash_quiz()
        return

    if problem_name in OPTIMIZATIONS:
        variables, domains, constraints, constraint_types, partial_assignment = generate_solvable_csp_with_partial()
        print_constraints_readable(variables, domains, constraints, constraint_types, partial_assignment)

        strategy = None
        use_fc = use_ac3 = False
        if problem_name == 'FC':
            use_fc = True
        elif problem_name == 'MRV':
            strategy = "MRV"
        elif problem_name == 'AC-3':
            use_ac3 = True

        vars_to_fill = [v for v in variables if v not in partial_assignment]
        user_assignment = read_complete_user_assignment(vars_to_fill, partial_assignment, read_user_assignment)
        solution = backtrack(copy.deepcopy(partial_assignment), variables, domains, constraints, constraint_types,
                             mrv=strategy, use_fc=use_fc, use_ac3=use_ac3)

        benchmark_csp(solution, vars_to_fill, user_assignment)
        return

    choice = input("Generare instanță: [1] goală  [2] aproape completă validă (1/2) [1]: ").strip() or "1"
    
    if choice == "2":
        prefill_level = print_prefill_options()
        print(f"Aplic prefill automat nivel {int(prefill_level*100)}%")
        problem = create_problem_instance(problem_name, prefill=True, prefill_level=prefill_level)
        handle_prefill_editing(problem)
    else:
        problem = create_problem_instance(problem_name, prefill=False, prefill_level=0.0)
    
    show_prefill_preview(problem)
    
    print_instance_generated()
    times, validity = run_benchmark_all_algorithms(problem, ALGO_FUNCS)
    
    user_choice = get_algorithm_choice(ALGO_LIST)
    
    if user_choice not in ALGO_FUNCS:
        print("Algoritm invalid.")
        return
    
    user_time = times[user_choice]
    user_is_valid = validity.get(user_choice, False)
    
    print_benchmark_results(times, validity, user_choice, user_time, user_is_valid, ALGO_LIST)


if __name__ == "__main__":
    main()
