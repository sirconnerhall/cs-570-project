# coin_change.py
# Source: TheAlgorithms/Python
# https://github.com/TheAlgorithms/Python/blob/master/dynamic_programming/minimum_coin_change.py

import random

def greedy_min_coins(denominations, amount):
    # greedy approach: always grab the biggest coin that fits
    coins = []
    for c in denominations:
        coins.append(c)
    coins.sort(reverse=True)

    count = 0
    remaining = amount

    for i in range(len(coins)):
        while remaining >= coins[i]:
            remaining -= coins[i]
            count += 1

    if remaining != 0:
        return -1  # couldn't make exact change

    return count


def dp_min_coins(denominations, amount):
    # bottom up dp -- find the actual minimum number of coins
    # only used as a reference to measure how badly greedy does
    dp = []
    for i in range(amount + 1):
        dp.append(float('inf'))
    dp[0] = 0

    for i in range(1, amount + 1):
        for j in range(len(denominations)):
            coin = denominations[j]
            if coin <= i:
                if dp[i - coin] + 1 < dp[i]:
                    dp[i] = dp[i - coin] + 1

    if dp[amount] == float('inf'):
        return -1

    return dp[amount]


if __name__ == "__main__":
    import doctest
    doctest.testmod()


# ---- ga stuff ----

def fitness_func(chromosome):
    # chromosome = [denom1, denom2, ..., denomN, target_amount]
    # fitness = greedy_coins - dp_coins (how suboptimal greedy is)
    # classic failure: [1,3,4] target 6 -> greedy=3, dp=2, gap=1

    target = chromosome[-1]
    denoms = chromosome[:-1]

    if len(denoms) == 0:
        return 0

    optimal = dp_min_coins(denoms, target)

    if optimal == -1:
        # no solution exists, not interesting
        return 0

    greedy = greedy_min_coins(denoms, target)

    if greedy == -1:
        # greedy failed but dp found a solution -- worst case
        return target

    return greedy - optimal

def generate_chromosome(n_denoms=5, max_amount=1000):

    chromosome = [1]

    while len(chromosome) < n_denoms:
        val = random.randint(2,100)
        if val not in chromosome:
            chromosome.append(val)

    chromosome.sort()  
    chromosome.append(random.randint(15, max_amount)) # target amount
    return chromosome

def mutate(chromosome, mutation_rate=0.3):
    seen = {1}
    result = [1]

    for i in range(1, len(chromosome) - 1):
        if random.random() < mutation_rate:
            val = random.randint(2, 100)
        else:
            val = chromosome[i]
        if val not in seen:
            seen.add(val)
            result.append(val)
        else:
            # pick a fresh value that doesn't collide
            attempts = 0
            while attempts < 20:
                val = random.randint(2, 100)
                if val not in seen:
                    seen.add(val)
                    result.append(val)
                    break
                attempts += 1

    if random.random() < mutation_rate:
        result.append(random.randint(15, 1000))
    else:
        result.append(chromosome[-1])

    return result