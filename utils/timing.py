import time
from typing import Callable, Any, Tuple, Optional

def time_function(func: Callable[[Any], Any], arg: Any, timeout: Optional[float] = None) -> Tuple[Any, float]:
    t0 = time.perf_counter()
    res = func(arg)
    t1 = time.perf_counter()
    return res, t1 - t0
