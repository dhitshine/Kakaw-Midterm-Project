from random import Random

import matplotlib.pyplot as plt

from kakaw.algorithms.base import LocalSearch
from kakaw.problems import Problem, State


class GeneticAlgorithm(LocalSearch):
    """
    Deskripsi:
      Kelas utama untuk Genetic Algorithm
    """

    def __init__(
        self,
        problem: Problem,
        N: int = 50,
        G: int = 200,
        p_c: float = 0.8,
        p_m: float = 0.1,
        elit: int = 2,
        seed: int = 42,
    ) -> None:
        super().__init__(problem)
        if type(N) is not int or N < 3:
            raise ValueError("N harus integer >= 3 untuk tournament")
        if type(G) is not int or G < 0:
            raise ValueError("G harus integer >= 0")
        if type(elit) is not int or not 0 <= elit <= N:
            raise ValueError("elit harus integer antara 0 dan N")
        if not 0 <= p_c <= 1 or not 0 <= p_m <= 1:
            raise ValueError("p_c dan p_m harus berada pada [0, 1]")
        self.N = N
        self.G = G
        self.p_c = p_c
        self.p_m = p_m
        self.elit = elit
        self.seed = seed

    def search(self) -> State:
        objective = self.problem.objective
        objective.evaluations = 0
        rng = Random(self.seed)
        initial = self.initial_state.copy()
        initial_score = objective.evaluate(initial)
        population = [(initial_score, initial)]
        self.iteration = 0
        self.history = []
        self.history_x = []

        while len(population) < self.N:
            candidate = initial.copy()
            for class_id in candidate.allocations:
                candidate = self.problem.random_relocate(candidate, class_id, rng)
            score = objective.evaluate(candidate)
            population.append((score, candidate))

        for _ in range(self.G):
            population.sort(key=self._score)
            new_population = population[: self.elit]
            score = population[0][0] # Best score
            while len(new_population) < self.N:
                first = self._tournament(population, rng)
                second = self._tournament(population, rng)
                child = first.copy()
                if rng.random() < self.p_c:
                    child = self._crossover(first, second, rng)
                child = self._mutate(child, rng)
                score = objective.evaluate(child)
                new_population.append((score, child))

            population = new_population
            self.iteration += 1
            self.history.append(score)
            self.history_x.append(self.iteration)

        best = min(population, key=self._score)
        self.goal_state = best[1]
        return self.goal_state

    def _score(self, individual):
        return individual[0]

    def _tournament(self, population: list[tuple[float, State]], rng: Random) -> State:
        participants = rng.sample(population, 3)
        winner = participants[0]
        for individual in participants[1:]:
            if individual[0] < winner[0]:
                winner = individual
        return winner[1]

    def _crossover(self, first: State, second: State, rng: Random) -> State:
        allocations = {}
        for class_id in first.allocations:
            if rng.random() < 0.5:
                allocations[class_id] = first.allocations[class_id]
            else:
                allocations[class_id] = second.allocations[class_id]
        return State(allocations)

    def _mutate(self, state: State, rng: Random) -> State:
        for class_id in state.allocations:
            if rng.random() < self.p_m:
                state = self.problem.random_relocate(state, class_id, rng)
        return state

    def plot(self, path: str | None = None) -> None:
        generations: list[float] = self.history_x
        fitness: list[float] = [-value for value in self.history]
        if not generations:
            print("No data to plot")
            return
        plt.figure(figsize=(10, 6))
        plt.plot(generations, fitness, linewidth=2, color="blue")
        plt.xlabel("Generation", fontsize=12)
        plt.ylabel("Fitness", fontsize=12)
        plt.title("Genetic Algorithm - Fitness vs Generations", fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        if path is None:
            plt.show()
        else:
            plt.savefig(path)
        plt.close()
