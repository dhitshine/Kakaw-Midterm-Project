import matplotlib.pyplot as plt

from kakaw.algorithms.base import LocalSearch
from kakaw.problems import Problem, State


class SteepestHillClimbing(LocalSearch):
    """
    Deskripsi:
      Kelas utama untuk algoritma Steepest Hill Climbing
      dengan pemilihan tetangga terbaik.
    """

    def __init__(
        self, problem: Problem, max_iterations: int = 1000,
    ) -> None:
        super().__init__(problem)
        if type(max_iterations) is not int or max_iterations < 0:
            raise ValueError("max_iterations harus integer >= 0")
        self.max_iterations = max_iterations

    def search(self) -> State:
        objective = self.problem.objective
        objective.evaluations = 0

        current = self.initial_state.copy()
        current_score = objective.evaluate(current)
        self.iteration = 0
        self.history = [current_score]

        for _ in range(self.max_iterations):
            best_neighbor = None
            best_score = current_score

            neighbors = self.problem.get_all_successors(current)

            for neighbor in neighbors:
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

    def plot(self, path: str | None = None) -> None:
        objectives: list[float] = self.history
        if not objectives:
            print("No data to plot")
            return
        plt.figure(figsize=(10, 6))
        plt.plot(objectives, linewidth=2, color="blue")
        plt.xlabel("Iteration", fontsize=12)
        plt.ylabel("Objective Function", fontsize=12)
        plt.title("Steepest Ascent Hill Climbing Algorithm - Objective Function vs Iteration", fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        if path is None:
            plt.show()
        else:
            plt.savefig(path)
        plt.close()

