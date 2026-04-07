import copy
import random
import time
from typing import Any

from dijkstra import dijkstra
from ga_framework import GeneticAlgorithm, Individual, Problem


class DijkstraIndividual(Individual):
    """
    Represents an input graph to Dijkstra's algorithm.
    The genotype is an adjacency list: {node: [[neighbor, cost], ...]}
    Nodes are integers from 0 to V-1.
    """

    def __init__(self, genotype, num_nodes: int):
        super().__init__(genotype)
        self.num_nodes = num_nodes

    def mutate(self, mutation_rate: float):
        """
        Mutates the graph by adding, removing, or modifying edges.
        """
        for u in range(self.num_nodes):
            if random.random() < mutation_rate:
                mutation_type = random.choice(["add", "remove", "modify"])

                if mutation_type == "add":
                    # Add a random edge
                    v = random.randint(0, self.num_nodes - 1)
                    if u != v:
                        cost = random.randint(1, 100)
                        # Check if edge already exists to avoid duplicates
                        existing = [edge[0] for edge in self.genotype[u]]
                        if v not in existing:
                            self.genotype[u].append([v, cost])

                elif mutation_type == "remove" and len(self.genotype[u]) > 0:
                    # Remove a random edge
                    edge_idx = random.randint(0, len(self.genotype[u]) - 1)
                    self.genotype[u].pop(edge_idx)

                elif mutation_type == "modify" and len(self.genotype[u]) > 0:
                    # Modify an edge weight
                    edge_idx = random.randint(0, len(self.genotype[u]) - 1)
                    self.genotype[u][edge_idx][1] = random.randint(1, 100)

    def crossover(self, other: Any):
        """
        Crossover by mixing the adjacency lists of the two parents.
        For each node, we randomly inherit its outgoing edges from parent 1 or parent 2.
        """
        child1_genotype = {i: [] for i in range(self.num_nodes)}
        child2_genotype = {i: [] for i in range(self.num_nodes)}

        for i in range(self.num_nodes):
            if random.random() < 0.5:
                child1_genotype[i] = copy.deepcopy(self.genotype[i])
                child2_genotype[i] = copy.deepcopy(other.genotype[i])
            else:
                child1_genotype[i] = copy.deepcopy(other.genotype[i])
                child2_genotype[i] = copy.deepcopy(self.genotype[i])

        return DijkstraIndividual(child1_genotype, self.num_nodes), DijkstraIndividual(
            child2_genotype, self.num_nodes
        )


class DijkstraProblem(Problem[DijkstraIndividual]):
    """
    Defines the problem of finding a graph that causes worst-case performance
    (maximum execution time) for Dijkstra's Algorithm.
    """

    def __init__(
        self, num_nodes: int = 100, edge_density: float = 0.2, trials: int = 5
    ):
        self.num_nodes = num_nodes
        self.edge_density = edge_density
        self.trials = trials

    def generate_random_individual(self) -> DijkstraIndividual:
        genotype = {i: [] for i in range(self.num_nodes)}

        # Ensure it's at least weakly connected by creating a path 0 -> 1 -> ... -> V-1
        for i in range(self.num_nodes - 1):
            genotype[i].append([i + 1, random.randint(1, 100)])

        # Add random edges based on density
        for u in range(self.num_nodes):
            for v in range(self.num_nodes):
                if u != v and random.random() < self.edge_density:
                    # Avoid duplicates
                    if v not in [edge[0] for edge in genotype[u]]:
                        genotype[u].append([v, random.randint(1, 100)])

        return DijkstraIndividual(genotype, self.num_nodes)

    def evaluate_fitness(self, individual: DijkstraIndividual) -> float:
        """
        Fitness is the time it takes to find the shortest path from 0 to V-1.
        Higher time = higher fitness (worse case).
        """
        total_time = 0.0
        start_node = 0
        end_node = self.num_nodes - 1

        for _ in range(self.trials):
            # Graph isn't modified by dijkstra, but we pass it anyway
            start_time = time.perf_counter()
            dijkstra(individual.genotype, start_node, end_node)
            end_time = time.perf_counter()

            total_time += end_time - start_time

        return total_time / self.trials


def test_random_vs_ga():
    """
    Driver function to compare random graphs against GA-evolved worst-case graphs for Dijkstra.
    """
    print("--- Dijkstra Failure Finder ---")
    num_nodes = 200
    trials = 5

    problem = DijkstraProblem(num_nodes=num_nodes, edge_density=0.1, trials=trials)
    ga = GeneticAlgorithm(
        problem=problem,
        pop_size=30,
        generations=20,
        mutation_rate=0.2,
        crossover_rate=0.8,
        elitism=True,
    )

    print(f"Running Genetic Algorithm to find worst-case graphs (N={num_nodes})...")
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
        f"Average random graph fitness (execution time): {avg_random_time:.6f} seconds"
    )
    print(f"Max random graph fitness: {max_random_time:.6f} seconds")

    if avg_random_time > 0:
        print(
            f"Improvement over average random: {((best_ind.fitness or 0.0) / avg_random_time):.2f}x slower"
        )

    # Analyze the found graph
    total_edges = sum(len(edges) for edges in best_ind.genotype.values())
    max_edges_node = max(len(edges) for edges in best_ind.genotype.values())

    print("\nGraph Analysis:")
    print(f"Total Nodes: {num_nodes}")
    print(f"Total Edges: {total_edges}")
    print(f"Average Edges per Node: {total_edges / num_nodes:.2f}")
    print(f"Max Edges on a Single Node: {max_edges_node}")
    print(
        "Dijkstra's worst-case typically emerges in dense graphs where many suboptimal paths are explored before the destination is reached."
    )


if __name__ == "__main__":
    test_random_vs_ga()
