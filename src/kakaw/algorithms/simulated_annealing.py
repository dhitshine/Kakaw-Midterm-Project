from __future__ import annotations

import math
from random import Random

import matplotlib.pyplot as plt

from kakaw.algorithms.base import LocalSearch
from kakaw.problems import Problem, State


class SimulatedAnnealing(LocalSearch):
    """
    Deskripsi:
      Kelas utama untuk algoritma Simulated Annealing
      sesuai spesifikasi §7.2 dan §5.4.
    """

    def __init__(
        self,
        problem: Problem,
        T0: float | None = None,
        rho: float = 0.995,
        max_iterations: int = 20000,
        seed: int = 42,
    ) -> None:
        super().__init__(problem)
        if T0 is not None and (not isinstance(T0, (int, float)) or T0 <= 0):
            raise ValueError("T0 harus berupa angka (int/float) > 0")
        if type(max_iterations) is not int or max_iterations < 0:
            raise ValueError("max_iterations harus integer >= 0")
        if not isinstance(rho, (int, float)) or not (0 < rho < 1):
            raise ValueError("rho harus berada pada rentang (0, 1)")

        self.T0 = (
            float(5.0 * self.problem.objective.weight)
            if T0 is None
            else float(T0)
        )
        self.rho = float(rho)
        self.max_iterations = max_iterations
        self.seed = seed
        self.accepted_moves: int = 0

    def search(self) -> State:
        objective = self.problem.objective
        objective.evaluations = 0
        rng = Random(self.seed)

        current = self.initial_state.copy()
        current_score = objective.evaluate(current)
        best = current.copy()
        best_score = current_score

        self.iteration = 0
        self.accepted_moves = 0
        self.history = []
        T = self.T0

        for _ in range(self.max_iterations):
            neighbor = self.problem.random_successor(current, rng)
            neighbor_score = objective.evaluate(neighbor)
            delta = neighbor_score - current_score

            accept = False
            if delta <= 0:
                accept = True
            else:
                exponent = -delta / T
                if exponent > -700:
                    try:
                        prob = math.exp(exponent)
                    except OverflowError:
                        prob = 0.0
                else:
                    prob = 0.0

                if rng.random() < prob:
                    accept = True

            if accept:
                current = neighbor
                current_score = neighbor_score
                self.accepted_moves += 1

            if current_score < best_score:
                best = current.copy()
                best_score = current_score

            self.iteration += 1
            self.history.append(current_score)
            T = max(self.rho * T, 1e-12)

        self.goal_state = best
        return self.goal_state

    def plot(self, path: str | None = None) -> None:
        iterations: list[float] = self.history_x or list(
            range(1, len(self.history) + 1)
        )
        if not iterations:
            print("No data to plot")
            return
        plt.figure(figsize=(10, 6))
        plt.plot(iterations, self.history, linewidth=2, color="blue")
        plt.xlabel("Iteration", fontsize=12)
        plt.ylabel("Objective Function Value", fontsize=12)
        plt.title("Simulated Annealing - Objective Function vs Iteration", fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        if path is None:
            plt.show()
        else:
            plt.savefig(path)
        plt.close()
