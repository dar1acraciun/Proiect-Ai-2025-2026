import time
import pickle
import subprocess
import sys
from typing import Callable, Any, Tuple, Optional

def time_function(func: Callable[[Any], Any], arg: Any, timeout: Optional[float] = None) -> Tuple[Any, float]:
    """Run func(arg) and return (result, elapsed_seconds).

    If timeout is provided (seconds) the call will be executed in a separate
    process and terminated if it exceeds the timeout. On timeout the function
    returns (None, float('inf')). If multiprocessing cannot be used (pickling
    errors) the call falls back to a direct invocation (no timeout).
    """
    if timeout is None:
        t0 = time.perf_counter()
        res = func(arg)
        t1 = time.perf_counter()
        return res, t1 - t0

    # Use multiprocessing to enforce timeout (works on Windows)
    try:
        # quick pre-check: ensure func and arg are picklable. If not, avoid spawning
        try:
            pickle.dumps(func)
            pickle.dumps(arg)
        except Exception:
            # Not picklable — caller may want to pass non-serializable objects (common).
            # Fall back to a direct call (no timeout) and surface a clear warning.
            # Returning direct timing here avoids creating a child process that would
            # otherwise emit noisy spawn-time tracebacks on Windows.
            print("[warning] multiprocessing-based timeout unavailable: function or argument not picklable; running without timeout")
            t0 = time.perf_counter()
            res = func(arg)
            t1 = time.perf_counter()
            return res, t1 - t0

        # Attempt to run the function in a subprocess to enforce timeout without
        # relying on multiprocessing handles (which can be fragile on Windows).
        mod = getattr(func, "__module__", None)
        name = getattr(func, "__name__", None)
        if mod and name and mod != "__main__":
            try:
                pickled = pickle.dumps(arg)
                # build a small runner that imports the function and executes it
                runner = (
                    f"import time, pickle, sys\n"
                    f"from {mod} import {name}\n"
                    f"arg = pickle.loads(sys.stdin.buffer.read())\n"
                    f"t0 = time.perf_counter()\n"
                    f"try:\n    {name}(arg)\nexcept SystemExit:\n    pass\n"
                    f"t1 = time.perf_counter()\n"
                    f"print(t1 - t0)\n"
                )
                proc = subprocess.run([sys.executable, "-c", runner], input=pickled, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
                if proc.returncode != 0:
                    # If the subprocess failed, surface stderr for debugging then fallback
                    # to direct call
                    # suppress noisy binary output
                    err = proc.stderr.decode(errors='replace')
                    print(f"[warning] subprocess runner failed: {err}")
                else:
                    out = proc.stdout.decode().strip()
                    try:
                        elapsed = float(out.splitlines()[-1].strip()) if out else float('inf')
                        return None, elapsed
                    except Exception:
                        # parsing failed, fallthrough to direct call
                        pass
            except subprocess.TimeoutExpired:
                return None, float('inf')
            except Exception as e:
                # any other problem with subprocess approach — fallback
                print(f"[warning] subprocess-based timeout unavailable: {e}")

        # If subprocess approach isn't possible, fall back to direct call (no enforced timeout)
        t0 = time.perf_counter()
        res = func(arg)
        t1 = time.perf_counter()
        return res, t1 - t0
    except Exception:
        # If multiprocessing fails for an unexpected reason, fallback to direct call
        t0 = time.perf_counter()
        res = func(arg)
        t1 = time.perf_counter()
        return res, t1 - t0
