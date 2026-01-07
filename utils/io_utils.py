import json
import random
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parents[1] / "templates" / "question_templates.json"
PROBLEMS = ["N-Queens", "Generalized Hanoi", "Graph Coloring", "Knight's Tour"]
OPTIMIZATIONS = ["FC", "MRV", "AC-3"]


def load_templates():
    with open(TEMPLATES, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_question():
    templates = load_templates()
    template = random.choice(templates)
    
    if "Alpha-Beta" in template:
        return template.format(problem_name="MinMax"), "MinMax"
    
    if "Nash" in template:
        return template.format(problem_name="Nash"), "Nash"

    if "problem_name" in template:
        problem = random.choice(PROBLEMS)
        return template.format(problem_name=problem), problem

    opt = random.choice(OPTIMIZATIONS)
    return template.format(optimization=opt), opt
