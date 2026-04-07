import random
import time
from typing import Any

from coin_change import dp_count
from ga_framework import GeneticAlgorithm, Individual, Problem


class CoinChangeIndividual(Individual):
    """
    Represents an input to the Coin Change algorithm.
    The genotype is a list of integers representing coin denominations.
    """

    def __init__(self, genotype):
        super().__init__(genotype)

    def mutate(self, mutation_rate: float):
        """
        Mutates the coin denominations.
        Replaces coins with random new denominations.
        """
        mutated = False
        for i in range(len(self.genotype)):
            if random.random() < mutation_rate:
                # Replace with a new random coin value (avoiding 0)
                self.genotype[i] = random.randint(1, 100)
                mutated = True

        # Ensure we have a valid list of distinct, positive integers
        if mutated:
            self.genotype = sorted(list(set(self.genotype)))
            if not self.genotype:
                self.genotype = [1]

    def crossover(self, other: Any):
        """
        Performs single-point crossover to generate two new sets of coins.
        """
        if len(self.genotype) < 2 or len(other.genotype) < 2:
            return CoinChangeIndividual(self.genotype.copy()), CoinChangeIndividual(
                other.genotype.copy()
            )

        point1 = random.randint(1, len(self.genotype) - 1)
        point2 = random.randint(1, len(other.genotype) - 1)

        child1_genotype = sorted(
            list(set(self.genotype[:point1] + other.genotype[point2:]))
        )
        child2_genotype = sorted(
            list(set(other.genotype[:point2] + self.genotype[point1:]))
        )

        # Fallback if crossover creates empty sets
        if not child1_genotype:
            child1_genotype = [1]
        if not child2_genotype:
            child2_genotype = [1]

        return CoinChangeIndividual(child1_genotype), CoinChangeIndividual(
            child2_genotype
        )


class CoinChangeProblem(Problem[CoinChangeIndividual]):
    """
    Defines the problem of finding the coin denominations that result in the
    maximum number of ways to make change for a given target amount.
    This creates a combinatorial explosion (testing integer limits/memory in some languages).
    """

    def __init__(
        self, target_amount: int = 500, num_coins: int = 10, max_coin_val: int = 50
    ):
        self.target_amount = target_amount
        self.num_coins = num_coins
        self.max_coin_val = max_coin_val

    def generate_random_individual(self) -> CoinChangeIndividual:
        coins = set()
        while len(coins) < self.num_coins:
            coins.add(random.randint(1, self.max_coin_val))
        return CoinChangeIndividual(sorted(list(coins)))

    def evaluate_fitness(self, individual: CoinChangeIndividual) -> float:
        """
        Fitness is the total number of ways to make change for the target amount.
        Higher value means a more complex combinatorial output.
        """
        ways = dp_count(individual.genotype, self.target_amount)
        # Return as float since GA framework assumes float-compatible fitness
        return float(ways)


def test_random_vs_ga():
    """
    Driver function to compare random coin sets against GA-evolved worst-case sets.
    """
    print("--- Coin Change Failure Finder ---")
    target_amount = 1000
    num_coins = 8

    problem = CoinChangeProblem(
        target_amount=target_amount, num_coins=num_coins, max_coin_val=100
    )
    ga = GeneticAlgorithm(
        problem=problem,
        pop_size=40,
        generations=30,
        mutation_rate=0.2,
        crossover_rate=0.7,
        elitism=True,
    )

    print(
        f"Running Genetic Algorithm to find coin sets maximizing combinations for target {target_amount}..."
    )
    start_time = time.perf_counter()
    best_ind, history = ga.run(verbose=True)
    ga_time = time.perf_counter() - start_time

    print("\n--- Results ---")
    print(f"GA Execution Time: {ga_time:.2f} seconds")
    print(f"Evolved worst-case fitness (Combinations): {int(best_ind.fitness or 0)}")
    print(f"Evolved Coin Set: {best_ind.genotype}")

    # Generate random baseline
    random_fitnesses = []
    for _ in range(40):
        rand_ind = problem.generate_random_individual()
        random_fitnesses.append(problem.evaluate_fitness(rand_ind))

    avg_random_fitness = sum(random_fitnesses) / len(random_fitnesses)
    max_random_fitness = max(random_fitnesses)

    print(f"\nAverage random coin set combinations: {int(avg_random_fitness)}")
    print(f"Max random coin set combinations: {int(max_random_fitness)}")

    if avg_random_fitness > 0:
        print(
            f"Improvement over average random: {((best_ind.fitness or 0) / avg_random_fitness):.2f}x more combinations"
        )

    # The expected worst-case for maximizing combinations is usually small denominations like [1, 2, 3, ...]
    print("\nAnalysis:")
    print(
        "Notice how the GA naturally favors smaller coin denominations (often driving towards 1, 2, 3...)"
    )
    print(
        "because smaller coins can be combined in significantly more ways to reach the target amount."
    )


if __name__ == "__main__":
    test_random_vs_ga()
