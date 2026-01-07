import random
from collections import deque, defaultdict
import copy


def generate_csp_random(num_vars=4, min_val=1, max_val=10, max_domain_size=5, num_constraints=5):
    variables = [f'X{i}' for i in range(num_vars)]

    # Domenii diferite pentru fiecare variabilă
    domains = {}
    for var in variables:
        size = random.randint(2, max_domain_size)
        domains[var] = sorted(random.sample(range(min_val, max_val + 1), size))

    # Generare constrângeri binare cu operatori aleatori
    operators = ['!=', '=', '<', '>']
    constraints = defaultdict(list)
    constraint_types = {}
    for _ in range(num_constraints):
        x, y = random.sample(variables, 2)
        if y not in constraints[x]:
            constraints[x].append(y)
            constraints[y].append(x)
            op = random.choice(operators)
            constraint_types[(x, y)] = op
            if op == '<':
                constraint_types[(y, x)] = '>'
            elif op == '>':
                constraint_types[(y, x)] = '<'
            else:
                constraint_types[(y, x)] = op

    # Asignare parțială aleatoare
    partial_assignment = {}
    for var in random.sample(variables, random.randint(0, num_vars-1)):
        partial_assignment[var] = random.choice(domains[var])

    return variables, domains, constraints, constraint_types, partial_assignment


def map_operator(op):
    return '==' if op == '=' else op


def is_consistent(var, value, assignment, constraints, constraint_types):
    for neighbor in constraints[var]:
        if neighbor in assignment:
            op = map_operator(constraint_types[(var, neighbor)])
            neighbor_val = assignment[neighbor]
            if not eval(f"{value} {op} {neighbor_val}"):
                return False
    return True


def select_unassigned_variable(variables, assignment, domains, strategy=None):
    unassigned = [v for v in variables if v not in assignment]
    if not unassigned:
        return None
    if strategy == "MRV":
        return min(unassigned, key=lambda var: len(domains[var]))
    return unassigned[0]


def forward_checking(var, value, domains, constraints, constraint_types, assignment):
    temp_domains = copy.deepcopy(domains)
    for neighbor in constraints[var]:
        if neighbor not in assignment:
            op = map_operator(constraint_types[(var, neighbor)])
            temp_domains[neighbor] = [val for val in temp_domains[neighbor] if eval(f"{value} {op} {val}")]
            if not temp_domains[neighbor]:
                return None
    return temp_domains


def ac3(domains, constraints, constraint_types):
    queue = deque([(xi, xj) for xi in constraints for xj in constraints[xi]])

    def revise(xi, xj):
        revised = False
        op = map_operator(constraint_types[(xi, xj)])
        original_domain = domains[xi][:]
        domains[xi] = [x for x in domains[xi] if any(eval(f"{x} {op} {y}") for y in domains[xj])]
        if domains[xi] != original_domain:
            revised = True
        return revised

    while queue:
        xi, xj = queue.popleft()
        if revise(xi, xj):
            if not domains[xi]:
                return False
            for xk in constraints[xi]:
                if xk != xj:
                    queue.append((xk, xi))
    return True


def backtrack(assignment, variables, domains, constraints, constraint_types, mrv=None, use_fc=False, use_ac3=False):
    if len(assignment) == len(variables):
        return assignment

    var = select_unassigned_variable(variables, assignment, domains, mrv)
    if var is None:
        return assignment

    for value in domains[var]:
        if is_consistent(var, value, assignment, constraints, constraint_types):
            assignment[var] = value
            temp_domains = domains

            if use_fc:
                temp_domains = forward_checking(var, value, domains, constraints, constraint_types, assignment)
                if temp_domains is None:
                    del assignment[var]
                    continue
            elif use_ac3:
                temp_domains = copy.deepcopy(domains)
                temp_domains[var] = [value]
                if not ac3(temp_domains, constraints, constraint_types):
                    del assignment[var]
                    continue

            result = backtrack(assignment, variables, temp_domains, constraints, constraint_types, mrv, use_fc, use_ac3)
            if result:
                return result
            del assignment[var]
    return None


def backtrack_all_solutions(assignment, variables, domains, constraints, constraint_types, mrv=None, use_fc=False, use_ac3=False, solutions=None):
    """Găsește TOATE soluțiile pentru CSP-ul dat."""
    if solutions is None:
        solutions = []
    
    if len(assignment) == len(variables):
        solutions.append(copy.deepcopy(assignment))
        return solutions

    var = select_unassigned_variable(variables, assignment, domains, mrv)
    if var is None:
        solutions.append(copy.deepcopy(assignment))
        return solutions

    for value in domains[var]:
        if is_consistent(var, value, assignment, constraints, constraint_types):
            assignment[var] = value
            # Copiem domains pentru a evita modificări în-place
            temp_domains = copy.deepcopy(domains)

            if use_fc:
                temp_domains = forward_checking(var, value, domains, constraints, constraint_types, assignment)
                if temp_domains is None:
                    del assignment[var]
                    continue
            elif use_ac3:
                temp_domains = copy.deepcopy(domains)
                temp_domains[var] = [value]
                if not ac3(temp_domains, constraints, constraint_types):
                    del assignment[var]
                    continue

            backtrack_all_solutions(assignment, variables, temp_domains, constraints, constraint_types, mrv, use_fc, use_ac3, solutions)
            del assignment[var]
    
    return solutions


def print_constraints_readable(variables, domains, constraints, constraint_types, partial_assignment):
    print("Variabile:", variables)
    print("Domenii:", domains)
    seen = set()
    readable = []
    for var in constraints:
        for neighbor in constraints[var]:
            if (var, neighbor) not in seen and (neighbor, var) not in seen:
                op = constraint_types[(var, neighbor)]
                readable.append(f"{var} {op} {neighbor}")
                seen.add((var, neighbor))
    print("Constrangeri:", ",".join(readable))
    print("Asignare partiala:", partial_assignment)


def generate_solvable_csp_with_partial(num_vars=4, min_val=1, max_val=10, max_domain_size=5,
                                       num_constraints=5, max_attempts=100, max_partial_vars=None):
    """
    Generează un CSP aleator care are cel puțin o soluție și o asignare partială consistentă.
    Partial_assignment se alege dintr-o soluție completă.
    """
    for _ in range(max_attempts):
        variables, domains, constraints, constraint_types, _ = generate_csp_random(
            num_vars, min_val, max_val, max_domain_size, num_constraints
        )

        # Verificăm dacă există cel puțin o soluție completă
        solution = backtrack({}, variables, domains, constraints, constraint_types)
        if not solution:
            continue  # regenerează CSP dacă nu e solvabil

        # Generăm o partial_assignment din soluție
        partial_assignment = {}
        if max_partial_vars is None:
            max_partial_vars = num_vars - 1
        num_partial = random.randint(1, max_partial_vars)

        candidate_vars = random.sample(variables, num_partial)
        for var in candidate_vars:
            partial_assignment[var] = solution[var]

        return variables, domains, constraints, constraint_types, partial_assignment

    raise Exception("Nu am reușit să genereze un CSP solvabil cu partial_assignment după multe încercări.")


def read_user_assignment(input_str):
    """
    Parsează un string de forma 'X0=3,X1=4' într-un dict {X0:3, X1:4}.
    Returnează None dacă formatul e invalid.
    """
    assignment = {}
    try:
        parts = input_str.split(',')
        for p in parts:
            var_val = p.split('=')
            if len(var_val) != 2:
                return None  # format invalid
            var, val = var_val
            assignment[var.strip()] = int(val.strip())
        return assignment
    except (ValueError, AttributeError, IndexError):
        return None


def read_complete_user_assignment(vars_to_fill, partial_assignment, read_assignment):
    """
    Cere utilizatorului să introducă EXACT valorile pentru vars_to_fill.
    Blochează până când inputul este valid.
    """
    example = ",".join(f"{v}=1" for v in vars_to_fill)

    while True:
        user_input = input(
            f"Introdu valorile pentru {vars_to_fill} (ex: {example}): "
        )

        # ❌ variabilă duplicată (X1=2,X1=3)
        raw_vars = [p.split('=')[0].strip() for p in user_input.split(',')]
        if len(raw_vars) != len(set(raw_vars)):
            print("Aceeasi variabila nu poate fi asignata de doua ori.")
            continue

        user_assignment = read_assignment(user_input)
        if user_assignment is None:
            print("Format invalid.")
            continue

        # ❌ reasignare variabile cunoscute
        forbidden = set(user_assignment.keys()) & set(partial_assignment.keys())
        if forbidden:
            print("Nu poti reasigna variabile deja cunoscute:", list(forbidden))
            continue

        # ❌ nu sunt EXACT variabilele cerute
        if set(user_assignment.keys()) != set(vars_to_fill):
            print("Trebuie sa asignezi EXACT aceste variabile:", vars_to_fill)
            continue

        return user_assignment


def benchmark_csp(solution, vars_to_fill, user_assignment):
    print("=== Soluție finală ===")
    print(solution)
    correct = 0
    total = len(vars_to_fill)

    for var in vars_to_fill:
        if user_assignment[var] == solution[var]:
            correct += 1

    score = (correct / total) * 100 if total > 0 else 100.0

    print("\n=== Evaluare răspuns utilizator ===")
    print(f"Variabile corecte: {correct} / {total}")
    print(f"Scor: {score:.2f}%")
