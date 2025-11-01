import json
import random
from typing import Tuple
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parents[1] / "templates" / "question_templates.json"
PROBLEMS = ["N-Queens", "Generalized Hanoi", "Graph Coloring", "Knight’s Tour"]

def load_templates():
    with open(TEMPLATES, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_question():
    templates = load_templates()
    template = random.choice(templates)
    problem = random.choice(PROBLEMS)
    return template.format(problem_name=problem), problem
