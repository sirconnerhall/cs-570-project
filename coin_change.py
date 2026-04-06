# coin_change.py
# Source: TheAlgorithms/Python
# https://github.com/TheAlgorithms/Python/blob/master/dynamic_programming/minimum_coin_change.py

def dp_count(s, n):
    """Count the number of ways to make change for n units using coin denominations s.

    >>> dp_count([1, 2, 3], 4)
    4
    >>> dp_count([1, 2, 3], 7)
    8
    >>> dp_count([2, 5, 3, 6], 10)
    5
    >>> dp_count([10], 99)
    0
    >>> dp_count([4, 5, 6], 0)
    1
    >>> dp_count([1, 2, 3], -5)
    0
    """
    if n < 0:
        return 0
    # table[i] = number of ways to make change for amount i
    table = [0] * (n + 1)
    table[0] = 1  # one way to make change for 0: use no coins

    for coin_val in s:
        for j in range(coin_val, n + 1):
            table[j] += table[j - coin_val]

    return table[n]


if __name__ == "__main__":
    import doctest
    doctest.testmod()
