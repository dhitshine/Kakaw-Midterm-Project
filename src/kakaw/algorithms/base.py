from abc import ABC, abstractmethod

from kakaw.problems import Problem, State


class LocalSearch(ABC):
    """
    Deskripsi:
      Abstract class untuk algoritma local search.
    """

    def __init__(self, problem: Problem) -> None:
        self.problem: Problem = problem
        self.initial_state: State = problem.initial_state()
        self.goal_state: State | None = None
        self.iteration: int = 0
        self.history: list[float] = []
        self.history_x: list[float] = []

    @abstractmethod
    def search(self) -> State:
        """Method wajib untuk menjalankan algoritma."""

    def plot(self, path: str | None = None) -> None:
        """Plot objective per move diterima; simpan ke `path` bila diberi."""
