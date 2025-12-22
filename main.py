from utils.io_utils import generate_question
from utils.display import *
from utils.problem_factory import create_problem_instance
from utils.prefill import handle_prefill_editing, show_prefill_preview
from utils.algorithm_runner import run_benchmark_all_algorithms
from problems.minimax_quiz import run_minimax_quiz
import algorithms.uninformed as uninformed
import algorithms.informed as informed
from problems.nash_quiz import run_nash_quiz




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
