import sympy as sp
from itertools import combinations_with_replacement
from math import factorial
import galois
import numpy as np

def build_field_tables(m, GF, lam):
    """Строит ТУБВ по формуле (6) с одной константой lam."""
    index_matrix = np.zeros((m, m), dtype=int)
    coeff_matrix = np.zeros((m, m), dtype=object)
    for i in range(m):
        for j in range(m):
            s = i + j
            index_matrix[i, j] = s % m
            if s < m:
                coeff_matrix[i, j] = GF(1)
            else:
                coeff_matrix[i, j] = lam
    return index_matrix, coeff_matrix

def multiply_vectors(a, b, index_matrix, coeff_matrix, GF):
    m = len(a)
    res = [GF(0) for _ in range(m)]
    for i in range(m):
        for j in range(m):
            idx = index_matrix[i, j]
            res[idx] += a[i] * b[j] * coeff_matrix[i, j]
    return res

def power_vector(v, exp, index_matrix, coeff_matrix, GF):
    """Быстрое возведение в степень (бинарный алгоритм)."""
    result = None
    base = v[:]
    n = exp
    while n > 0:
        if n & 1:
            result = base[:] if result is None else multiply_vectors(result, base, index_matrix, coeff_matrix, GF)
        base = multiply_vectors(base, base, index_matrix, coeff_matrix, GF)
        n >>= 1
    return result

def power_vector_slow(v, exp, index_matrix, coeff_matrix, GF):
    """Медленное возведение в степень (последовательное умножение) — для отладки GF(2^s)."""
    result = v[:]
    for _ in range(exp - 1):
        result = multiply_vectors(result, v, index_matrix, coeff_matrix, GF)
    return result

def multinomial_coeff(combo):
    counts = {}
    for x in combo:
        counts[x] = counts.get(x, 0) + 1
    denom = 1
    for c in counts.values():
        denom *= factorial(c)
    return factorial(len(combo)) // denom

def generate_polynomials(index_matrix, coeff_matrix, GF, k=3):
    m = index_matrix.shape[0]
    x = sp.symbols(f'x0:{m}')
    p = GF.characteristic
    combos = list(combinations_with_replacement(range(m), k))
    coeff_dicts = [{} for _ in range(m)]
    for combo in combos:
        mult = multinomial_coeff(combo)
        prod = [GF(0) for _ in range(m)]
        prod[combo[0]] = GF(1)
        for idx in combo[1:]:
            vec = [GF(0) for _ in range(m)]
            vec[idx] = GF(1)
            prod = multiply_vectors(prod, vec, index_matrix, coeff_matrix, GF)
        monomial = sp.prod([x[i] for i in combo])
        for t in range(m):
            if prod[t] != 0:
                coeff_int = (mult * int(prod[t])) % p
                coeff_dicts[t][monomial] = (coeff_dicts[t].get(monomial, 0) + coeff_int) % p
    polynomials = []
    for t in range(m):
        poly = sum(sp.Mul(coeff, monom) for monom, coeff in coeff_dicts[t].items())
        polynomials.append(sp.expand(poly))
    return polynomials