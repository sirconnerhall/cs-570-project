import copy
import random
import sys
import time
from typing import Any

from ga_framework import GeneticAlgorithm, Individual, Problem
from quicksort import quick_sort

# Increase recursion depth just in case the worst-case quicksort goes deep
sys.setrecursionlimit(2000)


class QuicksortIndividual(Individual):
    """
    Represents an input array to the Quicksort algorithm.
    The genotype is a list of integers.
    """

    def __init__(self, genotype):
        super().__init__(genotype)

    def mutate(self, mutation_rate: float):
        """
        Mutates the array by swapping elements or replacing elements with random numbers.
        """
        for i in range(len(self.genotype)):
            if random.random() < mutation_rate:
                # 50% chance to swap with another element
                if random.random() < 0.5:
                    j = random.randint(0, len(self.genotype) - 1)
                    self.genotype[i], self.genotype[j] = (
                        self.genotype[j],
                        self.genotype[i],
                    )
                # 50% chance to replace with a new random number
                else:
                    self.genotype[i] = random.randint(0, len(self.genotype) * 2)

    def crossover(self, other: Any):
        """
        Performs single-point crossover to generate two new children.
        """
        point = random.randint(1, len(self.genotype) - 2)
        child1_genotype = self.genotype[:point] + other.genotype[point:]
        child2_genotype = other.genotype[:point] + self.genotype[point:]

        return QuicksortIndividual(child1_genotype), QuicksortIndividual(
            child2_genotype
        )


class QuicksortProblem(Problem[QuicksortIndividual]):
    """
    Defines the problem of finding the worst-case input for Quicksort.
    Fitness is defined as the time taken to sort the array.
    """

    def __init__(self, array_size: int = 500, trials: int = 5):
        self.array_size = array_size
        self.trials = trials

    def generate_random_individual(self) -> QuicksortIndividual:
        genotype = [
            random.randint(0, self.array_size * 2) for _ in range(self.array_size)
        ]
        return QuicksortIndividual(genotype)

    def evaluate_fitness(self, individual: QuicksortIndividual) -> float:
        """
        Evaluates how 'bad' the array is for quicksort.
        Higher time = worse performance = higher fitness.
        Since quicksort.py uses `randrange` for the pivot, the worst case is highly dependent on RNG.
        We run a few trials and take the average time to smooth out the randomness.
        """
        total_time = 0.0

        for _ in range(self.trials):
            # We must pass a copy because quick_sort modifies the array in-place via pops
            arr_copy = copy.deepcopy(individual.genotype)

            start_time = time.perf_counter()
            quick_sort(arr_copy)
            end_time = time.perf_counter()

            total_time += end_time - start_time

        return total_time / self.trials


def test_random_vs_ga():
    """
    Driver function to compare random array performance against GA-evolved worst-case arrays.
    """
    print("--- Quicksort Failure Finder ---")
    array_size = 200  # Using a smaller size to keep GA runtimes manageable
    trials = 10

    problem = QuicksortProblem(array_size=array_size, trials=trials)
    ga = GeneticAlgorithm(
        problem=problem,
        pop_size=30,
        generations=20,
        mutation_rate=0.15,
        crossover_rate=0.8,
        elitism=True,
    )

    print("Running Genetic Algorithm to find worst-case Quicksort arrays...")
    best_ind, history = ga.run(verbose=True)

    print("\n--- Results ---")
    print(
        f"Evolved worst-case fitness (avg execution time over {trials} trials): {(best_ind.fitness or 0.0):.6f} seconds"
    )

    # Generate random baseline
    random_times = []
    for _ in range(30):
        rand_ind = problem.generate_random_individual()
        random_times.append(problem.evaluate_fitness(rand_ind))

    avg_random_time = sum(random_times) / len(random_times)
    max_random_time = max(random_times)

    print(
        f"Average random array fitness (execution time): {avg_random_time:.6f} seconds"
    )
    print(f"Max random array fitness: {max_random_time:.6f} seconds")
    print(
        f"Improvement over average random: {((best_ind.fitness or 0.0) / avg_random_time):.2f}x slower"
    )

    # Analyze the found array
    is_sorted = best_ind.genotype == sorted(best_ind.genotype)
    is_reverse_sorted = best_ind.genotype == sorted(best_ind.genotype, reverse=True)

    print("\nArray Analysis:")
    print(f"Length: {len(best_ind.genotype)}")
    print(f"Is already sorted? {is_sorted}")
    print(f"Is reverse sorted? {is_reverse_sorted}")
    print(f"First 20 elements: {best_ind.genotype[:20]}")


if __name__ == "__main__":
    test_random_vs_ga()
