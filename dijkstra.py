# dijkstra.py
# Source: TheAlgorithms/Python
# https://github.com/TheAlgorithms/Python/blob/master/graphs/dijkstra.py

import heapq
import random


def dijkstra(graph, start, end):
    """Return the cost of the shortest path between vertices start and end.

    Graph format: {node: [[neighbor, cost], ...]}
    Returns -1 if no path exists.

    >>> dijkstra(G, "E", "C")
    6
    >>> dijkstra(G2, "E", "F")
    3
    >>> dijkstra(G3, "E", "F")
    3
    """
    heap = [(0, start)]  # (cost, node)
    visited = set()
    while heap:
        (cost, u) = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        if u == end:
            return cost
        for v, c in graph[u]:
            if v not in visited:
                heapq.heappush(heap, (cost + c, v))
    return -1


# Sample graphs for testing
G = {
    "A": [["B", 2], ["C", 5]],
    "B": [["A", 2], ["D", 3], ["E", 1], ["F", 1]],
    "C": [["A", 5], ["F", 3]],
    "D": [["B", 3]],
    "E": [["B", 4], ["F", 3]],
    "F": [["C", 3], ["E", 3]],
}

G2 = {
    "B": [["C", 1]],
    "C": [["D", 1]],
    "D": [["F", 1]],
    "E": [["B", 1], ["F", 3]],
    "F": [],
}

G3 = {
    "B": [["C", 1]],
    "C": [["D", 1]],
    "D": [["F", 1]],
    "E": [["B", 1], ["G", 2]],
    "F": [],
    "G": [["F", 1]],
}


if __name__ == "__main__":
    import doctest
    doctest.testmod()


# ---- instrumented version + ga stuff ----

# global heap op counter
# counting both pushes and pops as "work"
heap_ops = 0

# fixing number of nodes -- changing this breaks the chromosome encoding
N_NODES = 6


def dijkstra_instrumented(graph, start, end):
    # counts heap operations as a proxy for how hard the algorithm works
    global heap_ops
    heap_ops = 0

    heap = [(0, start)]
    visited = set()

    while heap:
        cost, u = heapq.heappop(heap)
        heap_ops += 1  # pop

        if u in visited:
            continue
        visited.add(u)

        if u == end:
            return cost

        for v, c in graph[u]:
            if v not in visited:
                heapq.heappush(heap, (cost + c, v))
                heap_ops += 1  # push

    return -1


def weights_to_graph(weights):
    # decode flat chromosome into adjacency dict
    # chromosome has N_NODES*(N_NODES-1) entries, one per directed edge i->j where i != j
    # weight of 0 means no edge
    # TODO: maybe make this undirected? not sure if it matters

    graph = {}
    for i in range(N_NODES):
        graph[i] = []

    idx = 0
    for i in range(N_NODES):
        for j in range(N_NODES):
            if i != j:
                w = weights[idx]
                if w > 0:
                    graph[i].append([j, w])
                idx += 1

    return graph


def fitness_func(chromosome):
    # run dijkstra from node 0 to node N_NODES-1 and return heap op count
    # if no path exists return 0 (not interesting)
    global heap_ops

    graph = weights_to_graph(chromosome)
    result = dijkstra_instrumented(graph, 0, N_NODES - 1)

    if result == -1:
        return 0

    return heap_ops


def generate_chromosome():
    # random edge weights for an N_NODES directed graph
    # 0 = no edge, otherwise weight 1-20
    chrom = []

    for i in range(N_NODES):
        for j in range(N_NODES):
            if i != j:
                # ~40% chance of an edge existing
                if random.random() < 0.4:
                    chrom.append(random.randint(1, 20))
                else:
                    chrom.append(0)

    return chrom


def mutate(chromosome, mutation_rate=0.2):
    # directional mutation -- denser graphs cause more heap ops so bias toward
    # adding edges rather than removing them
    result = []

    for i in range(len(chromosome)):
        if random.random() < mutation_rate:
            if chromosome[i] == 0:
                # no edge here -- strongly prefer adding one
                result.append(random.randint(1, 20))
            else:
                # edge exists -- usually just change the weight, rarely remove it
                if random.random() < 0.15:
                    result.append(0)
                else:
                    result.append(random.randint(1, 20))
        else:
            result.append(chromosome[i])

    return result
