import streamlit as st
import algorithms.uninformed as uninformed
import algorithms.informed as informed
from utils.algorithm_runner import run_benchmark_all_algorithms
from problems.n_queens import NQueensProblem
from problems.hanoi import GeneralizedHanoi
from problems.graph_coloring import GraphColoringProblem
from problems.knights_tour import KnightsTourProblem
import random

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
    "A*": informed.a_star,
}

ALGO_LIST = list(ALGO_FUNCS.keys())


def build_graph(nodes: int, edges: int, colors: int):
    graph = {i: set() for i in range(nodes)}
    color_classes = [[] for _ in range(colors)]
    for node in range(nodes):
        color_classes[node % colors].append(node)
    attempts = 0
    max_attempts = max(1, edges * 10)
    while attempts < edges and attempts < max_attempts:
        c1, c2 = random.sample(range(colors), 2)
        if color_classes[c1] and color_classes[c2]:
            n1 = random.choice(color_classes[c1])
            n2 = random.choice(color_classes[c2])
            if n2 not in graph[n1]:
                graph[n1].add(n2)
                graph[n2].add(n1)
                attempts += 1
    return graph, attempts


def preview_problem(problem):
    pre = getattr(problem, "prefilled", None)
    if pre is None:
        st.info("Fără prefill aplicat.")
        return
    name = problem.__class__.__name__
    if name == "GeneralizedHanoi":
        positions = list(pre)
        towers = {i: [] for i in range(1, problem.num_towers + 1)}
        for disk_num, tower in enumerate(positions, start=1):
            towers[int(tower)].append(disk_num)
        for t in range(1, problem.num_towers + 1):
            st.write(f"Peg {t}: {towers[t]}")
    else:
        st.json(pre)


st.set_page_config(page_title="AI Problems Benchmark", page_icon="⚙️", layout="wide")
st.title("Generator întrebări & benchmark algoritmi — Web")

with st.sidebar:
    st.header("Mod")
    mode = st.selectbox("Alege modul", ["Probleme & Benchmark", "Quiz Minimax", "Quiz Nash"], index=0)
    st.divider()
    if mode == "Probleme & Benchmark":
        st.subheader("Problemă")
        problem_name = st.selectbox(
            "Alege tipul problemei",
            ["N-Queens", "Generalized Hanoi", "Graph Coloring", "Knight's Tour"],
            index=0,
        )
        st.divider()

        if problem_name == "N-Queens":
            n = st.number_input("Dimensiunea tablei (n)", min_value=4, max_value=50, value=8, step=1)
        elif problem_name == "Generalized Hanoi":
            pegs = st.number_input("Număr de tije", min_value=3, max_value=10, value=3, step=1)
            discs = st.number_input("Număr de discuri", min_value=1, max_value=20, value=5, step=1)
            target = st.number_input("Peg țintă", min_value=1, max_value=int(pegs), value=2, step=1)
        elif problem_name == "Graph Coloring":
            nodes = st.number_input("Număr de noduri", min_value=1, max_value=500, value=20, step=1)
            edges = st.number_input("Număr de muchii dorite", min_value=0, max_value=2000, value=40, step=1)
            colors = st.number_input("Număr de culori", min_value=2, max_value=20, value=3, step=1)
        elif problem_name == "Knight's Tour":
            size = st.number_input("Dimensiune tablă (n)", min_value=4, max_value=30, value=8, step=1)
            start_r = st.number_input("Start row (0-index)", min_value=0, max_value=int(size) - 1, value=0, step=1)
            start_c = st.number_input("Start col (0-index)", min_value=0, max_value=int(size) - 1, value=0, step=1)

        st.subheader("Prefill")
        prefill_pct = st.slider("Nivel prefill (%)", min_value=0, max_value=100, value=90, step=1)
        generate_btn = st.button("Generează instanța")
    elif mode == "Quiz Minimax":
        st.subheader("Parametri arbore Minimax")
        mm_branch = st.number_input("Max frunze pe nod", min_value=2, max_value=10, value=2, step=1)
        mm_depth = st.number_input("Adâncime", min_value=2, max_value=8, value=3, step=1)
        mm_low = st.number_input("Valoare frunză minimă", min_value=-100, max_value=0, value=-10, step=1)
        mm_high = st.number_input("Valoare frunză maximă", min_value=1, max_value=100, value=10, step=1)
        gen_mm_btn = st.button("Generează arbore")
    elif mode == "Quiz Nash":
        st.subheader("Parametri joc (Nash)")
        difficulty = st.selectbox("Dificultate", ["easy", "medium", "hard"], index=1)
        if difficulty == "easy":
            rows_n, cols_n = 2, 2
            payoff_min, payoff_max, prob_nash = -3, 3, 0.7
        elif difficulty == "medium":
            rows_n = st.number_input("Rânduri", min_value=2, max_value=3, value=2, step=1)
            cols_n = st.number_input("Coloane", min_value=2, max_value=3, value=2, step=1)
            payoff_min, payoff_max, prob_nash = -5, 5, 0.5
        else:
            rows_n = st.number_input("Rânduri", min_value=3, max_value=5, value=4, step=1)
            cols_n = st.number_input("Coloane", min_value=3, max_value=5, value=4, step=1)
            payoff_min, payoff_max, prob_nash = -10, 10, 0.3
        gen_nash_btn = st.button("Generează joc")

if "problem" not in st.session_state:
    st.session_state.problem = None
if "benchmark" not in st.session_state:
    st.session_state.benchmark = None
if "minimax" not in st.session_state:
    st.session_state.minimax = None
if "nash" not in st.session_state:
    st.session_state.nash = None

if mode == "Probleme & Benchmark" and generate_btn:
    try:
        if problem_name == "N-Queens":
            prob = NQueensProblem(int(n))
        elif problem_name == "Generalized Hanoi":
            prob = GeneralizedHanoi(int(pegs), int(discs), int(target))
        elif problem_name == "Graph Coloring":
            graph, built = build_graph(int(nodes), int(edges), int(colors))
            prob = GraphColoringProblem(graph, int(colors))
            st.caption(f"Generat {built} muchii (cerute {int(edges)}).")
        elif problem_name == "Knight's Tour":
            prob = KnightsTourProblem(int(size), start=(int(start_r), int(start_c)))
        else:
            st.error("Problemă necunoscută")
            prob = None
        if prob is not None and hasattr(prob, "prefill_level"):
            level = max(0.0, min(1.0, prefill_pct / 100.0))
            try:
                prob.prefill_level(level)
            except Exception as e:
                st.warning(f"Eroare la aplicare prefill: {e}")
        st.session_state.problem = prob
        st.session_state.benchmark = None
        st.success("Instanță generată.")
    except Exception as e:
        st.error(f"Eroare la generare: {e}")

if mode == "Probleme & Benchmark":
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Preview instanță")
        if st.session_state.problem is None:
            st.info("Generează mai întâi o instanță.")
        else:
            preview_problem(st.session_state.problem)

    with col2:
        st.subheader("Benchmark algoritmi")
        if st.session_state.problem is None:
            st.info("Generează instanța pentru a rula benchmark.")
        else:
            run_btn = st.button("Rulează benchmark")
            if run_btn:
                with st.spinner("Rulez algoritmii, poate dura…"):
                    times, validity = run_benchmark_all_algorithms(st.session_state.problem, ALGO_FUNCS)
                    st.session_state.benchmark = {"times": times, "validity": validity}
            if st.session_state.benchmark is not None:
                times = st.session_state.benchmark["times"]
                validity = st.session_state.benchmark["validity"]
                valid_times = {k: v for k, v in times.items() if v != float("inf") and validity.get(k, False)}
                if not valid_times:
                    st.warning("Niciun algoritm nu a găsit o soluție validă.")
                else:
                    best = min(valid_times, key=valid_times.get)
                    rows = []
                    for k, v in sorted(times.items(), key=lambda kv: (kv[1] == float("inf"), kv[1])):
                        is_valid = validity.get(k, False)
                        display_time = "N/A" if (v == float("inf") or not is_valid) else f"{v:.6f}"
                        rows.append({"Algoritm": k, "Timp (s)": display_time, "Valid": "✔" if is_valid else "✖"})
                    st.table(rows)
                    st.success(f"Cel mai rapid algoritm valid: {best} ({times[best]:.6f}s)")

if mode == "Probleme & Benchmark":
    st.subheader("Alegerea ta")
    choice = st.selectbox("Alege algoritmul considerat cel mai potrivit", ALGO_LIST)
    if st.session_state.get("benchmark") is None:
        st.info("Rulează benchmark pentru a calcula scorul.")
    else:
        times = st.session_state.benchmark["times"]
        validity = st.session_state.benchmark["validity"]
        user_time = times.get(choice, float("inf"))
        user_is_valid = validity.get(choice, False)
        valid_times = {k: v for k, v in times.items() if v != float("inf") and validity.get(k, False)}
        if not user_is_valid:
            st.error("Soluția algoritmului ales este invalidă sau nu a rulat.")
        elif valid_times:
            best_time = min(valid_times.values())
            worst_time = max(valid_times.values())
            if best_time == worst_time:
                score = 100.0
            else:
                score = 100.0 * (worst_time - user_time) / (worst_time - best_time)
                score = min(100.0, max(0.0, score))
            best = min(valid_times, key=valid_times.get)
            if choice == best:
                st.success("Corect! Ai ales cel mai rapid algoritm cu soluție validă.")
            else:
                st.warning(f"Mai rapid: {best} ({times[best]:.6f}s)")
            st.metric(label="Scorul tău", value=f"{score:.2f}%")
        else:
            st.warning("Nu există timpuri valide pentru calculul scorului.")

# -------- Quiz Minimax UI --------
def render_minimax_tree(problem):
    lines = []
    def rec(node, level=0, is_max=True, prefix=""):
        if isinstance(node, int):
            lines.append(f"{prefix}FRUNZĂ: {node}")
        else:
            node_type = "MAX" if is_max else "MIN"
            child_count = len(node)
            if level == 0:
                lines.append(f"RĂDĂCINĂ ({node_type})")
                new_prefix = ""
            else:
                lines.append(f"{prefix}{node_type} (cu {child_count} copii)")
                new_prefix = prefix
            next_is_max = not is_max
            for i, child in enumerate(node):
                is_last = (i == len(node) - 1)
                if level == 0:
                    connector = "└─ " if is_last else "├─ "
                    child_prefix = connector
                else:
                    indent = "   " if is_last else "│  "
                    connector = "└─ " if is_last else "├─ "
                    child_prefix = new_prefix + indent + connector
                rec(child, level + 1, next_is_max, child_prefix)
    rec(problem.root, 0, True, "")
    return "\n".join(lines)

from problems.minimax_tree import MinimaxTreeProblem
if mode == "Quiz Minimax":
    if gen_mm_btn:
        try:
            st.session_state.minimax = MinimaxTreeProblem(
                branching=int(mm_branch), depth=int(mm_depth), leaf_min=int(mm_low), leaf_max=int(mm_high)
            )
            st.success("Arbore generat.")
        except Exception as e:
            st.error(f"Eroare la generare: {e}")
    if st.session_state.minimax is None:
        st.info("Generează un arbore pentru quiz.")
    else:
        st.subheader("Arbore Minimax")
        st.code(render_minimax_tree(st.session_state.minimax))
        st.subheader("Răspunsul tău")
        user_root = st.number_input("Valoarea rădăcinii", value=0, step=1)
        user_leaves = st.number_input("Noduri frunză evaluate (Alpha-Beta)", value=0, step=1)
        check_btn = st.button("Verifică răspunsul")
        if check_btn:
            correct_root, correct_visited = st.session_state.minimax.run_minimax_alphabeta()
            total_leaves = st.session_state.minimax.total_leaves()
            # scoring
            if int(user_root) == correct_root and int(user_leaves) == correct_visited:
                score = 100.0
                reason = "Răspuns exact pentru ambele valori."
            else:
                score = 100.0
                reasons = []
                root_diff = abs(int(user_root) - correct_root)
                root_correct = root_diff == 0
                if root_correct:
                    reasons.append("Valoarea rădăcinii corectă.")
                else:
                    score -= root_diff * 25.0
                    reasons.append(f"Valoarea rădăcinii: așteptat {correct_root}, tu {int(user_root)} (dif {root_diff}).")
                leaves_diff = abs(int(user_leaves) - correct_visited)
                leaves_correct = leaves_diff == 0
                if leaves_correct:
                    reasons.append("Numărul de frunze vizitate corect.")
                else:
                    score -= leaves_diff * 25.0
                    reasons.append(f"Frunze vizitate: așteptat {correct_visited}, tu {int(user_leaves)} (dif {leaves_diff}).")
                if root_correct or leaves_correct:
                    score = max(50.0, score)
                else:
                    score = max(0.0, score)
                reason = " ".join(reasons)
            st.metric("Scorul tău", f"{score:.2f}%")
            st.info(f"Corect: rădăcină = {correct_root}, frunze evaluate = {correct_visited} (total frunze = {total_leaves})")

# -------- Quiz Nash UI --------
from problems.random_nash_generator import generate_balanced_nash_game
def names(prefix: str, count: int):
    return [f"{prefix}{i+1}" for i in range(count)]

if mode == "Quiz Nash":
    if gen_nash_btn:
        try:
            matrix, equilibria = generate_balanced_nash_game(
                rows=int(rows_n), cols=int(cols_n), payoff_min=int(payoff_min), payoff_max=int(payoff_max), prob_with_nash=float(prob_nash)
            )
            st.session_state.nash = {
                "matrix": matrix,
                "equilibria": equilibria,
                "rows": names("R", int(rows_n)),
                "cols": names("C", int(cols_n)),
            }
            st.success("Joc generat.")
        except Exception as e:
            st.error(f"Eroare la generare: {e}")
    if st.session_state.nash is None:
        st.info("Generează un joc pentru quiz.")
    else:
        rows = st.session_state.nash["rows"]
        cols = st.session_state.nash["cols"]
        matrix = st.session_state.nash["matrix"]
        equilibria = st.session_state.nash["equilibria"]
        st.subheader("Matricea de payoff-uri")
        display_rows = []
        for i, r in enumerate(rows):
            row_display = {"": r}
            for j, c in enumerate(cols):
                u1, u2 = matrix[i][j]
                row_display[c] = f"({u1},{u2})"
            display_rows.append(row_display)
        st.table(display_rows)

        st.subheader("Întrebări")
        exists_choice = st.radio("Există echilibru Nash pur?", ["da", "nu"], index=0, horizontal=True)
        score = None
        reason = ""
        if exists_choice == "da":
            r_sel = st.selectbox("Strategia Player 1 (rând)", rows)
            c_sel = st.selectbox("Strategia Player 2 (coloană)", cols)
        check_nash_btn = st.button("Verifică răspunsul")
        if check_nash_btn:
            exists = len(equilibria) > 0
            if (exists_choice == "da") == exists:
                score = 50.0
            else:
                score = 0.0
                reason = "Răspuns greșit privind existența echilibrului."
            if score == 50.0 and exists:
                try:
                    ri = rows.index(r_sel)
                    ci = cols.index(c_sel)
                    if (ri, ci) in equilibria:
                        score = 100.0
                        reason = "Răspuns complet corect."
                    else:
                        score = 50.0
                        reason = "Existența corectă, dar strategia aleasă nu este Nash."
                except Exception:
                    score = 50.0
                    reason = "Strategii selectate invalide."
            if score == 50.0 and not exists:
                score = 100.0
                reason = "Corect: jocul nu are echilibru Nash pur."
            st.metric("Scorul tău", f"{score:.2f}%")
            # Show equilibria
            if equilibria:
                st.success("Echilibre Nash pure:")
                st.write([f"({rows[i]}, {cols[j]})" for i, j in equilibria])
            else:
                st.info("Nu există echilibru Nash pur.")

