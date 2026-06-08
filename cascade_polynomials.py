"""
Символьная генерация многочленов для двухслойной каскадной схемы.
Топология: X → разбиение на µ блоков длины η → N₁ (X³) → перестановка → N₂ (X³) → Z.
"""

import sympy as sp
from itertools import combinations_with_replacement
from math import factorial
import galois
import numpy as np
import random
from polynomials import build_field_tables, multiply_vectors

# ===============================
# Мультиномиальный коэффициент
# ===============================

def multinomial(combo):
    counts = {}
    for x in combo:
        counts[x] = counts.get(x, 0) + 1
    denom = 1
    for c in counts.values():
        denom *= factorial(c)
    return factorial(len(combo)) // denom


# ===============================
# Генерация многочленов для одного слоя (через ТУБВ)
# ===============================

def poly_layer(vars_list, index_matrix, coeff_matrix, GF, degree):
    """
    vars_list: список символьных переменных (длина m)
    index_matrix, coeff_matrix: ТУБВ
    GF: поле
    degree: степень (2 или 3)
    Возвращает список многочленов длины m.
    """
    m = len(vars_list)
    p = GF.characteristic
    combos = list(combinations_with_replacement(range(m), degree))
    coeff_dicts = [{} for _ in range(m)]

    for combo in combos:
        mult = multinomial(combo)
        # Произведение базисных векторов e[combo[0]] * ... * e[combo[degree-1]]
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
# Символьная каскадная схема
# ===============================

def cascade_polynomials(eta, mu, p, d, lambdas1, lambdas1_prime, lambdas2, lambdas2_prime, degree=3):
    """
    Генерирует многочлены для двухслойной схемы.
    eta, mu: размерности блоков (n = eta * mu)
    p: простое число (характеристика поля)
    d: параметр сдвига (пока 0)
    lambdas1, lambdas1_prime: константы для первого слоя (длина eta-1)
    lambdas2, lambdas2_prime: константы для второго слоя (длина mu-1)
    degree: степень (2 или 3)
    """
    n = eta * mu
    GF = galois.GF(p)
    
    # Символьные переменные для всего вектора
    x = sp.symbols(f'x0:{n}')
    
    # 1. Разбиваем переменные на µ блоков длины η
    blocks = []
    for i in range(mu):
        start = i * eta
        blocks.append(x[start:start+eta])
    
    # 2. Строим ТУБВ для первого слоя (размерность η)
    index1, coeff1 = build_field_tables(eta, GF, lambdas1[0])  # упрощённо, используем одну константу
    # (здесь нужно использовать все lambdas1 и lambdas1_prime, но для краткости пока одна)
    
    # 3. Получаем многочлены первого слоя для каждого блока
    first_layer = []
    for block in blocks:
        first_layer.append(poly_layer(block, index1, coeff1, GF, degree))
    
    # 4. Перестановка: из µ векторов длины η формируем η векторов длины µ
    # После первого слоя: first_layer[i][j] — j-я координата i-го блока
    # Новые блоки: для каждого t = 0..η-1 собираем координаты t из всех блоков
    transposed = []
    for t in range(eta):
        new_block_vars = [first_layer[k][t] for k in range(mu)]  # это выражения, не переменные
        transposed.append(new_block_vars)
    
    # 5. Строим ТУБВ для второго слоя (размерность µ)
    index2, coeff2 = build_field_tables(mu, GF, lambdas2[0])  # упрощённо
    
    # 6. Применяем второй слой к каждому транспонированному блоку
    second_layer = []
    for block_expr in transposed:
        # У второго слоя переменные — это уже выражения, а не исходные x
        # Нужно создать временные символы, подставить выражения в конце
        # Проще: заменить generate_polynomials на функцию, работающую с выражениями
        # Здесь используем ту же poly_layer, но передаём список выражений
        # Однако poly_layer ожидает список символов, поэтому придётся подменять
        # Для простоты используем численную проверку, а символьную сделаем позже
        # Пока заглушка
        pass
    
    # Временно возвращаем пустой результат
    print("Символьная генерация второго слоя требует доработки.")
    return None


# ===============================
# Тест: сравниваем численную и символьную версии (пока только первый слой)
# ===============================

def test_first_layer():
    eta = 3
    mu = 3
    p = 5
    degree = 3
    GF = galois.GF(p)
    n = eta * mu
    x = sp.symbols(f'x0:{n}')
    blocks = [x[0:3], x[3:6], x[6:9]]
    
    index, coeff = build_field_tables(eta, GF, 2)  # λ=2 для примера
    poly_first = []
    for block in blocks:
        poly_first.append(poly_layer(block, index, coeff, GF, degree))
    
    print("Многочлены первого слоя для блока 0:")
    for i, poly in enumerate(poly_first[0]):
        print(f"y_{i} = {poly}")

if __name__ == "__main__":
    test_first_layer()