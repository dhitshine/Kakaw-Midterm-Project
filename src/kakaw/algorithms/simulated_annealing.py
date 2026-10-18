from __future__ import annotations

import math
from random import Random

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
            neighbor = self._random_successor(current, rng)
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
            self.history.append(best_score)
            T = max(self.rho * T, 1e-12)

        self.goal_state = best
        return self.goal_state

    def _random_successor(self, state: State, rng: Random) -> State:
        """
        Membangkitkan satu tetangga acak dari N(x) sesuai §5.4:
        - Swap hanya dipilih jika kedua durasi masih muat setelah pertukaran;
          jika tidak, relocate yang dipakai.
        - Move relocate dapat mengganti hari/waktu/ruangan, atau ruangan saja.
        """
        class_ids = tuple(self.problem._classes.keys())
        if not class_ids:
            return state

        # Pilih swap dengan peluang 50% jika ada minimal 2 kelas
        if len(class_ids) >= 2 and rng.random() < 0.5:
            swapped = self.problem.random_swap(state, rng)
            if swapped is not None:
                return swapped

        # Relocate (dipakai jika swap tidak dipilih atau swap tidak valid, §5.4)
        class_id = rng.choice(class_ids)
        if len(self.problem._rooms) > 1 and rng.random() < 0.2:
            return self.problem.random_room_change(state, class_id, rng)
        return self.problem.random_relocate(state, class_id, rng)
