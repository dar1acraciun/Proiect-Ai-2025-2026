from abc import ABC, abstractmethod
from typing import Any, Iterable, Tuple


class Problem(ABC):

    @abstractmethod
    def initial_state(self) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def is_goal(self, state: Any) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def successors(self, state: Any) -> Iterable[Tuple[Any, float]]:
        raise NotImplementedError()

    def distance(self, a: Any, b: Any) -> float:
        return 1.0

    def heuristic(self, state: Any) -> float:
        return 0.0


    def prefill(self, state_or_positions: Any) -> None:
        setattr(self, "prefilled", state_or_positions)

    def prefill_level(self, level: float) -> None:
        return None

    def is_prefilled(self) -> bool:
        return hasattr(self, "prefilled") and getattr(self, "prefilled") is not None

    def get_prefilled(self) -> Any:
        return getattr(self, "prefilled", None)

    def apply_prefill(self, state_or_positions: Any) -> None:
        setter = getattr(self, "set_state", None)
        if callable(setter):
            try:
                setter(state_or_positions)
                return
            except Exception:
                pass

        setattr(self, "prefilled", state_or_positions)

    def set_state(self, state: Any) -> None:
        setattr(self, "prefilled", state)

    def to_dict(self) -> dict:
        return {"params": {}, "state": getattr(self, "prefilled", None)}

    @classmethod
    def from_dict(cls, d: dict):
        raise NotImplementedError("from_dict not implemented for this Problem class")

    def validate_solution(self, solution: Any) -> tuple[bool, str]:
        return False, "validate_solution not implemented for this problem"