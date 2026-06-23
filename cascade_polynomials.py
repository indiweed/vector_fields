"""
Символьная генерация многочленов для двухслойной каскадной схемы.
Топология: X → разбиение на µ блоков длины η → N₁ → перестановка → N₂ → Z.
"""

import sympy as sp
import galois
import numpy as np
import random
import time
from itertools import combinations_with_replacement
from math import factorial
from polynomials import build_field_tables, multiply_vectors, multinomial_coeff, power_vector, power_vector_slow

# ===============================
# Генерация многочленов для одного слоя (символьная версия)
# ===============================

def poly_layer(vars_list, index_matrix, coeff_matrix, GF, degree=3):
    m = len(vars_list)
    p = GF.characteristic
    combos = list(combinations_with_replacement(range(m), degree))
    coeff_dicts = [{} for _ in range(m)]

    for combo in combos:
        mult = multinomial_coeff(combo)
        prod = [GF(0) for _ in range(m)]
        prod[combo[0]] = GF(1)
        for idx in combo[1:]:
            vec = [GF(0) for _ in range(m)]
            vec[idx] = GF(1)
            prod = multiply_vectors(prod, vec, index_matrix, coeff_matrix, GF)
        monomial = sp.prod([vars_list[i] for i in combo])
        for t in range(m):
            if prod[t] != 0:
                coeff_val = (mult * int(prod[t])) % p
                if monomial in coeff_dicts[t]:
                    coeff_dicts[t][monomial] = (coeff_dicts[t][monomial] + coeff_val) % p
                else:
                    coeff_dicts[t][monomial] = coeff_val

    polys = []
    for t in range(m):
        poly = sum(sp.Mul(coeff, monom) for monom, coeff in coeff_dicts[t].items())
        polys.append(sp.expand(poly))
    return polys

# ===============================
# Символьная каскадная схема (открытый ключ)
# ===============================

def cascade_polynomials(eta, mu, p, d, lam1, lam2, degree=3):
    n = eta * mu
    GF = galois.GF(p)
    x = sp.symbols(f'x0:{n}')
    
    blocks = [x[i*eta:(i+1)*eta] for i in range(mu)]
    index1, coeff1 = build_field_tables(eta, GF, lam1)
    first_layer = [poly_layer(block, index1, coeff1, GF, degree) for block in blocks]
    
    transposed = [[first_layer[k][t] for k in range(mu)] for t in range(eta)]
    index2, coeff2 = build_field_tables(mu, GF, lam2)
    
    y = sp.symbols(f'y0:{mu}')
    second_layer_templates = poly_layer(y, index2, coeff2, GF, degree)
    second_layer = []
    for block_expr in transposed:
        subs = {y[i]: block_expr[i] for i in range(mu)}
        block_polys = [sp.expand(poly.subs(subs)) for poly in second_layer_templates]
        second_layer.append(block_polys)
    
    result_polys = [poly for block in second_layer for poly in block]
    return result_polys

# ===============================
# Прямая и обратная топология (шифрование/расшифрование)
# ===============================

def encrypt(X, eta, mu, GF, lam1, lam2, degree, use_slow=False):
    n = len(X)
    assert n == eta * mu
    pow_func = power_vector_slow if use_slow else power_vector
    index1, coeff1 = build_field_tables(eta, GF, lam1)
    index2, coeff2 = build_field_tables(mu, GF, lam2)
    blocks = [X[i*eta:(i+1)*eta] for i in range(mu)]
    powered1 = [pow_func(b, degree, index1, coeff1, GF) for b in blocks]
    transposed = [[powered1[k][t] for k in range(mu)] for t in range(eta)]
    final = [pow_func(t, degree, index2, coeff2, GF) for t in transposed]
    return [coord for block in final for coord in block]

def decrypt(Y, eta, mu, GF, lam1, lam2, degree, use_slow=False):
    n = len(Y)
    assert n == eta * mu
    pow_func = power_vector_slow if use_slow else power_vector
    order1 = GF.order**eta - 1
    order2 = GF.order**mu - 1
    s1 = pow(degree, -1, order1)
    s2 = pow(degree, -1, order2)
    index1, coeff1 = build_field_tables(eta, GF, lam1)
    index2, coeff2 = build_field_tables(mu, GF, lam2)
    blocks2 = [Y[i*mu:(i+1)*mu] for i in range(eta)]
    inv_blocks2 = [pow_func(b, s2, index2, coeff2, GF) for b in blocks2]
    transposed_inv = [[inv_blocks2[k][t] for k in range(eta)] for t in range(mu)]
    dec_blocks = [pow_func(b, s1, index1, coeff1, GF) for b in transposed_inv]
    return [coord for block in dec_blocks for coord in block]

# ===============================
# Тестирование
# ===============================

def test_cascade():
    print("=== Тест символьной каскадной схемы (GF(p)) ===")
    eta, mu = 2, 2
    p = 13
    lam1, lam2 = 2, 3
    degree = 3
    GF = galois.GF(p)
    polys = cascade_polynomials(eta, mu, p, 0, lam1, lam2, degree)
    x = sp.symbols(f'x0:{eta*mu}')
    X_num = [GF(random.randint(0, p-1)) for _ in range(eta*mu)]
    Y_num = encrypt(X_num, eta, mu, GF, lam1, lam2, degree)
    subs = {x[i]: int(X_num[i]) for i in range(eta*mu)}
    Y_poly = [int(poly.subs(subs) % p) for poly in polys]
    if [int(y) for y in Y_num] == Y_poly:
        print("✅ Совпадает")
    else:
        print("❌ Расхождение")

def test_topology():
    print("\n=== Проверка обратимости топологии ===")
    eta, mu = 2, 2
    p = 13
    lam1, lam2 = 2, 3
    degree = 5  # gcd(5,13^2-1)=1
    GF = galois.GF(p)
    X = [GF(random.randint(1, p-1)) for _ in range(eta*mu)]
    Y = encrypt(X, eta, mu, GF, lam1, lam2, degree)
    X_dec = decrypt(Y, eta, mu, GF, lam1, lam2, degree)
    if [int(x) for x in X] == [int(x) for x in X_dec]:
        print("✅ X == decrypt(encrypt(X))")
    else:
        print("❌ Ошибка")

if __name__ == "__main__":
    test_cascade()
    test_topology()