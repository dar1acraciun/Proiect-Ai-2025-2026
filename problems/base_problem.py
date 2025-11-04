from abc import ABC, abstractmethod
from typing import Any, Iterable, Tuple


class Problem(ABC):

    @abstractmethod
    def initial_state(self) -> Any:
        """Return the initial state for the problem (may depend on prefilled state)."""
        raise NotImplementedError()

    @abstractmethod
    def is_goal(self, state: Any) -> bool:
        """Return True if `state` is a goal state."""
        raise NotImplementedError()

    @abstractmethod
    def successors(self, state: Any) -> Iterable[Tuple[Any, float]]:
        """
        Yield (next_state, cost) pairs for successor states.

        Implementations should be pure w.r.t. `state` (i.e., not mutate it in place).
        Cost should be a float (default 1.0 when transitions are uniform).
        """
        raise NotImplementedError()

    def distance(self, a: Any, b: Any) -> float:
        """Transition cost (used by UCS / A*). Default 1.0."""
        return 1.0

    def heuristic(self, state: Any) -> float:
        """Heuristic for informed search (A* / Greedy). Default 0.0."""
        return 0.0

    # ---- Optional instance / evaluation hooks (defaults) ----

    def prefill(self, state_or_positions: Any) -> None:
        """
        Apply a concrete prefilling state supplied by caller.
        Default behaviour: save as attribute .prefilled for subclasses to consult.
        """
        setattr(self, "prefilled", state_or_positions)

    def prefill_level(self, level: float) -> None:
        """
        Generate and apply a partial valid state according to `level` in [0.0, 1.0].
        Default: no-op. Subclasses should override to implement problem-specific prefill logic.
        """
        return None

    def is_prefilled(self) -> bool:
        """Return True if a prefilled state/value exists for this problem."""
        return hasattr(self, "prefilled") and getattr(self, "prefilled") is not None

    def get_prefilled(self) -> Any:
        """Return the stored prefilled value or None if missing."""
        return getattr(self, "prefilled", None)

    def apply_prefill(self, state_or_positions: Any) -> None:
        """
        Apply a prefill in a safe, generic way.

        Preferred behavior: call subclass `set_state` if implemented, otherwise store
        the value on `self.prefilled`. Exceptions from subclass `set_state` fall back
        to storing the raw value.
        """
        setter = getattr(self, "set_state", None)
        if callable(setter):
            try:
                setter(state_or_positions)
                return
            except Exception:
                # if subclass raises on set_state, fallback to storing value
                pass

        setattr(self, "prefilled", state_or_positions)

    def set_state(self, state: Any) -> None:
        """Explicitly set the problem's internal initial state (default stores .prefilled)."""
        setattr(self, "prefilled", state)

    def to_dict(self) -> dict:
        """
        Serialize the problem instance to a dict with keys:
          - 'params': problem parameters (subclass should include, e.g. {'n':8})
          - 'state': current prefilled state or None
        Subclasses should override to include full parameterization.
        """
        return {"params": {}, "state": getattr(self, "prefilled", None)}

    @classmethod
    def from_dict(cls, d: dict):
        """
        Reconstruct a problem instance from a dict produced by to_dict.
        Default: raise NotImplementedError (subclasses should implement).
        """
        raise NotImplementedError("from_dict not implemented for this Problem class")

    def validate_solution(self, solution: Any) -> tuple[bool, str]:
        """
        Validate a candidate solution.
        Return (True, "") if correct, otherwise (False, "reason").
        Default: not implemented — subclasses should override.
        """
        return False, "validate_solution not implemented for this problem"