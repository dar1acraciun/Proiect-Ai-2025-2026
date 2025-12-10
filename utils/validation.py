
def validate_algo_result(problem, result):
    try:
        is_valid, reason = problem.validate_solution(result)
        return is_valid, reason
    except Exception as e:
        return False, f"Validation error: {e}"


def validate_tower_stacking(problem):
    try:
        disks = getattr(problem, 'prefilled', None)
        if disks is None:
            return True
        
        pegs_count = problem.num_towers
        towers = {i: [] for i in range(1, pegs_count + 1)}
        
        for disk_num, tower in enumerate(disks, start=1):
            towers[tower].append(disk_num)
        
        for t, lst in towers.items():
            if lst != sorted(lst):
                print(f"Problema: pe peg {t} ordinea discurilor nu este validă: {lst}")
                return False
        
        return True
    except Exception as e:
        print(f"Tower validation error: {e}")
        return False


def validate_prefill_input(raw_input: str):
    if not raw_input or not raw_input.strip():
        return None, "Input gol"
    
    try:
        parts = [int(x.strip()) for x in raw_input.split(',') if x.strip() != '']
        if not parts:
            return None, "Niciun număr valid găsit"
        return parts, None
    except ValueError:
        return None, "Format invalid - introduceti numere separate prin virgula"
