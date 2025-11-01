from abc import ABC, abstractmethod
from typing import Any, Iterable, Tuple


class Problem(ABC):

    @abstractmethod
    def initial_state(self) -> Any:
        """Returnează starea inițială a problemei."""
        raise NotImplementedError()

    @abstractmethod
    def is_goal(self, state: Any) -> bool:
        """Returnează True dacă state este stare finală."""
        raise NotImplementedError()

    @abstractmethod
    def successors(self, state: Any) -> Iterable[Tuple[Any, float]]:
        """
        Returnează iterator de (next_state, cost) pentru nodurile succesoare.
        Cost poate fi 1.0 dacă nu există costuri diferențiate.
        """
        raise NotImplementedError()

    def distance(self, a: Any, b: Any) -> float:
        """Distanța/transiția între două stări (folosită de UCS/A*). Implicit 1."""
        return 1.0

    def heuristic(self, state: Any) -> float:
        """Heuristică pentru A* / Greedy. Implicit 0."""
        return 0.0
