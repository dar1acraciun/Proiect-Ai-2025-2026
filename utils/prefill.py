from utils.validation import validate_prefill_input, validate_tower_stacking


def handle_prefill_editing(problem):
    try:
        pre = getattr(problem, "prefilled", None)
        if pre is not None:
            print("Prefill aplicat (preview):", pre)
            edit = input("Dorești să editezi manual preview-ul? (y/N): ").strip().lower()
            if edit == 'y':
                interactive_prefill_edit(problem, pre)
    except Exception:
        pass


def interactive_prefill_edit(problem, original_prefill):
    while True:
        raw = input("Introdu pozițiile discurilor separate prin virgula (ex: 2,2,2,1,...). Poți da mai puține valori; restul vor fi completate cu 1: ").strip()
        
        parts, error = validate_prefill_input(raw)
        if error:
            print(f"Eroare: {error}")
            cont = input("Reîncerci? (y/N): ").strip().lower()
            if cont != 'y':
                break
            continue
        
        try:
            problem.prefill(parts)
        except Exception as e:
            print(f"Prefill invalid: {e}")
            cont = input("Reîncerci? (y/N): ").strip().lower()
            if cont != 'y':
                break
            continue
        
        if validate_tower_stacking(problem):
            print("Prefill actualizat (preview):", problem.prefilled)
            break
        else:
            cont = input("Prefill generat nu e legal. Reîncerci editarea? (y/N): ").strip().lower()
            if cont != 'y':
                problem.prefill(original_prefill)
                break


def show_prefill_preview(problem):
    try:
        pre = getattr(problem, "prefilled", None)
        if pre is not None:
            print("Prefill aplicat (preview):", pre)
    except Exception:
        pass
