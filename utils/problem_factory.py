import random
from problems.n_queens import NQueensProblem
from problems.hanoi import GeneralizedHanoi
from problems.graph_coloring import GraphColoringProblem
from problems.knights_tour import KnightsTourProblem


def create_problem_instance(problem_name: str, prefill: bool = False, prefill_level: float = 0.0):
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
