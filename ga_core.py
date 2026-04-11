# ga_core.py
# Genetic algorithm core: selection, crossover, mutation, evolution loop
#
# Adapted from:
#   kiecodes/genetic-algorithms (https://github.com/kiecodes/genetic-algorithms/blob/master/algorithms/genetic.py)
#   helloevolve.py by Colin Drake via josephmisiti gist (https://gist.github.com/josephmisiti/940cee03c97f031188ba7eac74d03a4f)

import random
import copy


# selection functions
def tournament_selection(population, fitness_func, k=3):
    # Pick k individuals at random, return the best one.
    # Tournament selection is simpler than roulette when fitness values
    # aren't guaranteed to be positive (e.g. could be 0 or negative gaps).
    competitors = random.sample(population, k)
    return max(competitors, key=fitness_func)


def roulette_selection(population, fitness_func):
    # Fitness-proportional selection (roulette wheel).
    # Adapted from helloevolve.py -- manually compute weights then pick.
    # Requires all fitness values to be non-negative.
    fitnesses = [fitness_func(ind) for ind in population]
    total = sum(fitnesses)
    if total == 0:
        return random.choice(population)
    pick = random.uniform(0, total)
    current = 0
    for ind, f in zip(population, fitnesses):
        current += f
        if current >= pick:
            return ind
    return population[-1]


# crossover functions
def single_point_crossover(parent_a, parent_b):
    # Single-point crossover on two list chromosomes.
    # From kiecodes: pick a random cut point and swap tails.
    if len(parent_a) != len(parent_b):
        raise ValueError("Parents must be the same length for crossover")
    if len(parent_a) < 2:
        return copy.deepcopy(parent_a), copy.deepcopy(parent_b)
    point = random.randint(1, len(parent_a) - 1)
    child_a = parent_a[:point] + parent_b[point:]
    child_b = parent_b[:point] + parent_a[point:]
    return child_a, child_b


def two_point_crossover(parent_a, parent_b):
    # Two-point crossover: swap the segment between two random cut points.
    if len(parent_a) != len(parent_b):
        raise ValueError("Parents must be the same length for crossover")
    if len(parent_a) < 3:
        return copy.deepcopy(parent_a), copy.deepcopy(parent_b)
    p1 = random.randint(1, len(parent_a) - 2)
    p2 = random.randint(p1 + 1, len(parent_a) - 1)
    child_a = parent_a[:p1] + parent_b[p1:p2] + parent_a[p2:]
    child_b = parent_b[:p1] + parent_a[p1:p2] + parent_b[p2:]
    return child_a, child_b


# evoliution function

def evolve(
    population,
    fitness_func,
    mutate_func,
    crossover_func=single_point_crossover,
    selection_func=tournament_selection,
    generations=100,
    elitism=2,
    verbose=False
):
    """
    Run the genetic algorithm for a fixed number of generations.

    Args:
        population:     list of chromosomes (each chromosome is problem-specific)
        fitness_func:   callable(chromosome) -> float, higher = better/worse-case
        mutate_func:    callable(chromosome) -> chromosome, problem-specific mutation
        crossover_func: callable(parent_a, parent_b) -> (child_a, child_b)
        selection_func: callable(population, fitness_func) -> chromosome
        generations:    number of generations to run
        elitism:        number of top individuals carried over unchanged each generation
        verbose:        print progress every 10 generations

    Returns:
        best_individual: the highest-fitness chromosome found
        best_fitness:    its fitness score
        history:         list of (generation, best_fitness) tuples
    """
    history = []
    best_individual = None
    best_fitness = float('-inf')

    for gen in range(generations):
        # Sort by fitness descending
        population = sorted(population, key=fitness_func, reverse=True)

        gen_best_fitness = fitness_func(population[0])
        if gen_best_fitness > best_fitness:
            best_fitness = gen_best_fitness
            best_individual = copy.deepcopy(population[0])

        history.append((gen, gen_best_fitness))

        if verbose and gen % 10 == 0:
            print(f"Generation {gen}: best fitness = {gen_best_fitness:.4f}")

        # Elitism: carry the top individuals into the next generation unchanged
        next_gen = [copy.deepcopy(ind) for ind in population[:elitism]]

        # Fill the rest of the next generation via selection + crossover + mutation
        while len(next_gen) < len(population):
            parent_a = selection_func(population, fitness_func)
            parent_b = selection_func(population, fitness_func)
            child_a, child_b = crossover_func(parent_a, parent_b)
            child_a = mutate_func(child_a)
            child_b = mutate_func(child_b)
            next_gen.append(child_a)
            if len(next_gen) < len(population):
                next_gen.append(child_b)

        population = next_gen

    return best_individual, best_fitness, history


# random search
def random_search(generate_func, fitness_func, n_samples):
    """
    Random search baseline: evaluate n_samples random chromosomes and
    return the best one. Used to compare against the GA.

    Args:
        generate_func: callable() -> chromosome, generates a random chromosome
        fitness_func:  callable(chromosome) -> float
        n_samples:     total number of random chromosomes to evaluate

    Returns:
        best_individual, best_fitness, history (list of (sample_num, best_fitness))
    """
    best_individual = None
    best_fitness = float('-inf')
    history = []

    for i in range(n_samples):
        ind = generate_func()
        f = fitness_func(ind)
        if f > best_fitness:
            best_fitness = f
            best_individual = ind
        history.append((i, best_fitness))

    return best_individual, best_fitness, history
