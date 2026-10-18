
from random import Random

from kakaw.algorithms.base import LocalSearch
from kakaw.problems import Problem, State


class SteepestHillClimbing(LocalSearch):
    """
    Deskripsi:
      Kelas utama untuk algoritma Steepest Hill Climbing
      dengan pemilihan tetangga terbaik.
    """

    def __init__(
        self, problem: Problem, max_iterations: int = 200,
        neighbors_per_class: int = 5, seed: int = 42,
    ) -> None:
        super().__init__(problem)
        if type(max_iterations) is not int or max_iterations < 0:
            raise ValueError("max_iterations harus integer >= 0")
        if type(neighbors_per_class) is not int or neighbors_per_class < 1:
            raise ValueError("neighbors_per_class harus integer >= 1")
        self.max_iterations = max_iterations
        self.neighbors_per_class = neighbors_per_class
        self.seed = seed

    def search(self) -> State:
        objective = self.problem.objective
        objective.evaluations = 0
        rng = Random(self.seed)

        current = self.initial_state.copy()
        current_score = objective.evaluate(current)
        self.iteration = 0
        self.history = []

        for _ in range(self.max_iterations):
            best_neighbor = None
            best_score = current_score

            for class_id in current.assignments:
                for _ in range(self.neighbors_per_class):
                    neighbor = self.problem.random_relocate(
                        current.copy(), class_id, rng
                    )
                    score = objective.evaluate(neighbor)

                    if score < best_score:
                        best_neighbor = neighbor
                        best_score = score

            if best_neighbor is None:
                break

            current = best_neighbor
            current_score = best_score
            self.iteration += 1
            self.history.append(current_score)

        self.goal_state = current
        return self.goal_state
