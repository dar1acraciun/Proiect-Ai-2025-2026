import time
import inspect
from utils.timing import time_function
from utils.validation import validate_algo_result


def run_benchmark_all_algorithms(problem, algo_funcs: dict):
    results = {}
    validity = {}
    
    per_algo_timeout = 30.0
    
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
    
    local_search_algos = {"Hill Climbing", "Simulated Annealing", "Beam Search"}
    
    for name, func in algo_funcs.items():
        try:
            if func is None:
                results[name] = float('inf')
                validity[name] = False
                continue
            
            algo_problem = _prepare_problem_for_algo(problem, name, local_search_algos)
            result = _execute_algorithm(func, algo_problem, name, node_cap, step_cap, per_algo_timeout)
            
            results[name] = result['time']
            validity[name] = result['valid']
            
            if result['time'] == float('inf'):
                print(f"{name} timed out or errored: {result['result']}")
            else:
                print(f"{name} returned {result['result']} in {result['time']:.6f}s")
                is_valid, reason = validate_algo_result(algo_problem, result['result'])
                print(f" Validation: {'OK' if is_valid else 'INVALID'}{': ' + reason if reason else ''}")
                
                
                if is_valid and hasattr(algo_problem, 'num_towers'):
                    from utils.display import print_hanoi_towers
                    print_hanoi_towers(result['result'], algo_problem)
        
        except Exception:
            results[name] = float('inf')
            validity[name] = False
    
    return results, validity


def _prepare_problem_for_algo(problem, algo_name: str, local_search_algos: set):
    if problem.__class__.__name__ != 'GraphColoringProblem':
        return problem
    
    if algo_name in local_search_algos:
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
        else:
            algo_problem = problem
    
    return algo_problem


def _execute_algorithm(func, problem, algo_name: str, node_cap: int, step_cap: int, timeout: float):

    try:
        sig = inspect.signature(func)
    except Exception:
        sig = None
    
    
    if sig and 'max_nodes' in sig.parameters:
        t0 = time.perf_counter()
        try:
            res = func(problem, max_nodes=node_cap)
        except TypeError:
            res = func(problem)
        elapsed = time.perf_counter() - t0
        return {'time': elapsed, 'result': res, 'valid': True}
    
    if sig and 'max_steps' in sig.parameters:
        t0 = time.perf_counter()
        try:
            res = func(problem, max_steps=step_cap)
        except TypeError:
            res = func(problem)
        elapsed = time.perf_counter() - t0
        return {'time': elapsed, 'result': res, 'valid': True}
    
   
    res, t = time_function(func, problem, timeout=timeout)
    if t == float('inf'):
        return {'time': float('inf'), 'result': res, 'valid': False}
    else:
        is_valid, _ = validate_algo_result(problem, res)
        return {'time': t, 'result': res, 'valid': is_valid}
