import random
from typing import Tuple, Union

Node = Union[int, list]  


class MinimaxTreeProblem:
    def __init__(
        self,
        branching: int = 2,
        depth: int = 3,
        leaf_min: int = -10,
        leaf_max: int = 10,
    ):
        self.branching = max(1, int(branching))
        self.depth = max(1, int(depth))
        self.leaf_min = int(leaf_min)
        self.leaf_max = int(leaf_max)
        self.root = self._generate_node(self.depth)

    def _generate_node(self, depth: int) -> Node:
        if depth == 1:
            return random.randint(self.leaf_min, self.leaf_max)
        min_children = 2 if depth > 1 else 1
        num_children = random.randint(min_children, self.branching)
        return [self._generate_node(depth - 1) for _ in range(num_children)]

    def run_minimax_alphabeta(self) -> Tuple[int, int]:
        leaves_evaluated = [0]
        
        def evaluate(node):
            return node
        
        def is_terminal(node):
            return isinstance(node, int)
        
        def get_children(node):
            return node if isinstance(node, list) else []
        
        def alpha_beta_pruning(node, alpha, beta, maximizing_player):
            if is_terminal(node):
                leaves_evaluated[0] += 1
                return evaluate(node)
            
            if maximizing_player:
                max_eval = float('-inf')
                for child in get_children(node):
                    eval_val = alpha_beta_pruning(child, alpha, beta, False)
                    max_eval = max(max_eval, eval_val)
                    alpha = max(alpha, eval_val)
                    if beta <= alpha:
                        break  
                return max_eval
            else:
                min_eval = float('inf')
                for child in get_children(node):
                    eval_val = alpha_beta_pruning(child, alpha, beta, True)
                    min_eval = min(min_eval, eval_val)
                    beta = min(beta, eval_val)
                    if beta <= alpha:
                        break  
                return min_eval
        
        root_val = alpha_beta_pruning(self.root, float('-inf'), float('inf'), True)
        return root_val, leaves_evaluated[0]

    def total_leaves(self) -> int:
        def rec(node):
            if isinstance(node, int):
                return 1
            return sum(rec(c) for c in node)
        return rec(self.root)
