# driver.py
# ties everything together -- runs ga and random search for each algorithm
# and prints out results for comparison

import random
import ga_core
import quicksort as qs
import dijkstra as dijk
import coin_change as cc

# tweak these if needed
POP_SIZE = 100
GENERATIONS = 300
MUTATION_RATE = 0.2
RANDOM_BUDGET = POP_SIZE * GENERATIONS
random.seed(42)

def run_experiment(name, fitness_func, generate_func, mutate_func):
    print(f"\nrunning {name}...")

    population = [generate_func() for _ in range(POP_SIZE)]

    # ga_core expects no mutation_rate arg so wrap it
    def mutate_wrapper(chrom):
        return mutate_func(chrom, MUTATION_RATE)

    ga_best, ga_fitness, ga_history = ga_core.evolve(
        population=population,
        fitness_func=fitness_func,
        mutate_func=mutate_wrapper,
        generations=GENERATIONS,
        elitism=2,
        verbose=False
    )

    rs_best, rs_fitness, rs_history = ga_core.random_search(
        generate_func=generate_func,
        fitness_func=fitness_func,
        n_samples=RANDOM_BUDGET
    )

    # same eval budget so the comparison is actually fair
    print(f"ga: {ga_fitness}  random: {rs_fitness}")
    print(f"ga best: {ga_best}")
    print(f"random best: {rs_best}")
    if ga_fitness > rs_fitness:
        print("ga won")
    elif rs_fitness > ga_fitness:
        print("random won (???)")
    else:
        print("tied")

    return {
        "ga_best": ga_best, "ga_fitness": ga_fitness, "ga_history": ga_history,
        "rs_best": rs_best, "rs_fitness": rs_fitness, "rs_history": rs_history,
    }


if __name__ == "__main__":
    results = {}

    results["quicksort"] = run_experiment(
        name="quicksort",
        fitness_func=qs.fitness_func,
        generate_func=lambda: qs.generate_chromosome(n=20),
        mutate_func=qs.mutate,
    )

    # dijkstra fitness = heap operations, higher = worse for the algorithm
    results["dijkstra"] = run_experiment(
        name="dijkstra",
        fitness_func=dijk.fitness_func,
        generate_func=dijk.generate_chromosome,
        mutate_func=dijk.mutate,
    )

    results["coin change"] = run_experiment(
        name="coin change (greedy vs dp gap)",
        fitness_func=cc.fitness_func,
        generate_func=cc.generate_chromosome,
        mutate_func=cc.mutate,
    )

    # just print everything, can clean up later
    print("\n--- results ---")
    for name, r in results.items():
        print(f"{name}: ga={r['ga_fitness']} random={r['rs_fitness']}")