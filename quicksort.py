# quicksort.py
# Source: TheAlgorithms/Python
# https://github.com/TheAlgorithms/Python/blob/master/sorts/quick_sort.py

from __future__ import annotations
from random import randrange
import random


def quick_sort(collection: list) -> list:
    """A pure Python implementation of quicksort algorithm.

    :param collection: a mutable collection of comparable items
    :return: the same collection ordered in ascending order

    Examples:
    >>> quick_sort([0, 5, 3, 2, 2])
    [0, 2, 2, 3, 5]
    >>> quick_sort([])
    []
    >>> quick_sort([-2, 5, 0, -45])
    [-45, -2, 0, 5]
    """
    if len(collection) < 2:
        return collection

    pivot_index = randrange(len(collection))
    pivot = collection.pop(pivot_index)

    lesser = [item for item in collection if item <= pivot]
    greater = [item for item in collection if item > pivot]

    return [*quick_sort(lesser), pivot, *quick_sort(greater)]


if __name__ == "__main__":
    user_input = input("Enter numbers separated by a comma:\n").strip()
    unsorted = [int(item) for item in user_input.split(",")]
    print(quick_sort(unsorted))


# ---- instrumented version + ga stuff below ----

# global counter (avoids recursion)
comparison_count = 0


def quick_sort_instrumented(collection):
    # same as quick_sort but counts every comparison
    # using first element as pivot so its deterministic -- random pivot made
    # the fitness noisy and the ga couldnt learn anything
    global comparison_count

    if len(collection) < 2:
        return collection

    pivot = collection.pop(0)

    lesser = []
    greater = []

    # doing this as a loop instead of list comprehension so i can count comparisons
    for i in range(len(collection)):
        comparison_count += 1
        if collection[i] <= pivot:
            lesser.append(collection[i])
        else:
            greater.append(collection[i])

    return [*quick_sort_instrumented(lesser), pivot, *quick_sort_instrumented(greater)]


def fitness_func(chromosome):
    # fitness = number of comparisons quicksort makes on this input
    # more comparisons = closer to worst case = higher fitness for the ga
    global comparison_count
    comparison_count = 0

    # copy so we dont destroy the chromosome
    arr = []
    for x in chromosome:
        arr.append(x)

    quick_sort_instrumented(arr)

    # print(f"comparisons: {comparison_count}")  # debug, commenting out for now

    final = comparison_count
    return final


def generate_chromosome(n=20):
    # just a random list of ints
    chromosome = []
    for i in range(n):
        chromosome.append(random.randint(0, 100))

    return chromosome


def mutate(chromosome, mutation_rate=0.2):
    # directional mutation -- push toward sorted order since thats worst case
    # for first-element pivot. if neighbors are out of order, swap them.
    # small chance of random replacement to keep some diversity
    result = list(chromosome)

    for i in range(len(result) - 1):
        if random.random() < mutation_rate:
            if random.random() < 0.75:
                # sorting nudge: fix out-of-order adjacent pair
                if result[i] > result[i + 1]:
                    result[i], result[i + 1] = result[i + 1], result[i]
            else:
                # random replacement so we dont just immediately sort everything
                result[i] = random.randint(0, 100)

    return result
