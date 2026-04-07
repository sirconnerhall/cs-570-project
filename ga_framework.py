import copy
import random
from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, Tuple, TypeVar

T = TypeVar("T", bound="Individual")


class Individual(ABC):
    """
    Abstract base class for a Genetic Algorithm individual.
    Represents an input structure to an algorithm (the 'failure case').
    """

    def __init__(self, genotype: Any):
        self.genotype = genotype
        self.fitness: Optional[float] = None

    @abstractmethod
    def mutate(self, mutation_rate: float):
        """Mutate the individual's genotype in place."""
        pass

    @abstractmethod
    def crossover(self, other: Any) -> Tuple[Any, Any]:
        """Combine with another individual to produce two offspring."""
        pass


class Problem(ABC, Generic[T]):
    """
    Abstract base class for defining the problem-specific parts of the GA.
    You will subclass this for Quicksort, Dijkstra, Coin Change, etc.
    """

    @abstractmethod
    def generate_random_individual(self) -> T:
        """Create a random Individual for the initial population."""
        pass

    @abstractmethod
    def evaluate_fitness(self, individual: T) -> float:
        """
        Evaluate and return the fitness of the individual.
        In the context of this project, a HIGHER fitness means the algorithm
        performed WORSE (e.g., higher execution time, more comparisons).
        """
        pass


class GeneticAlgorithm(Generic[T]):
    """
    The main engine for the Genetic Algorithm.
    """

    def __init__(
        self,
        problem: Problem[T],
        pop_size: int = 50,
        generations: int = 100,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8,
        tournament_size: int = 3,
        elitism: bool = True,
    ):
        self.problem = problem
        self.pop_size = pop_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.tournament_size = tournament_size
        self.elitism = elitism
        self.population: List[T] = []

    def initialize_population(self):
        self.population = [
            self.problem.generate_random_individual() for _ in range(self.pop_size)
        ]

    def evaluate_population(self):
        for ind in self.population:
            if ind.fitness is None:
                ind.fitness = self.problem.evaluate_fitness(ind)

    def tournament_selection(self) -> T:
        """Select a parent using tournament selection."""
        tournament = random.sample(self.population, self.tournament_size)
        return max(tournament, key=lambda ind: ind.fitness or float("-inf"))

    def run(self, verbose: bool = True) -> Tuple[T, List[float]]:
        """
        Run the GA for the specified number of generations.
        Returns the best individual found and a history of best fitness per generation.
        """
        self.initialize_population()
        self.evaluate_population()

        best_individual = max(
            self.population, key=lambda ind: ind.fitness or float("-inf")
        )
        best_individual = copy.deepcopy(best_individual)
        history: List[float] = (
            [best_individual.fitness] if best_individual.fitness is not None else []
        )

        if verbose:
            print(f"Gen 0 (Initial) - Best Fitness: {best_individual.fitness}")

        for gen in range(self.generations):
            new_population = []

            while len(new_population) < self.pop_size:
                parent1 = self.tournament_selection()
                parent2 = self.tournament_selection()

                if random.random() < self.crossover_rate:
                    child1, child2 = parent1.crossover(parent2)
                else:
                    child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)

                child1.mutate(self.mutation_rate)
                child2.mutate(self.mutation_rate)

                # Reset fitness because genotypes have changed
                child1.fitness = None
                child2.fitness = None

                new_population.extend([child1, child2])

            # Ensure we don't exceed population size (if pop_size is odd)
            self.population = new_population[: self.pop_size]

            if self.elitism:
                # Replace the first individual with the best from the previous generation
                self.population[0] = copy.deepcopy(best_individual)

            self.evaluate_population()

            # Update best individual
            current_best = max(
                self.population, key=lambda ind: ind.fitness or float("-inf")
            )
            if (current_best.fitness or float("-inf")) > (
                best_individual.fitness or float("-inf")
            ):
                best_individual = copy.deepcopy(current_best)

            if best_individual.fitness is not None:
                history.append(best_individual.fitness)

            if verbose and (gen + 1) % max(1, (self.generations // 10)) == 0:
                print(
                    f"Gen {gen + 1}/{self.generations} - Best Fitness: {best_individual.fitness:.4f}"
                )

        return best_individual, history
