import galois
import random
from polynomials import build_field_tables, multiply_vectors, power_vector

def cascade_transform(X, m1, lam1, m2, lam2, GF, k1=3, k2=3):
    n = len(X)
    assert n == m1 * m2
    index1, coeff1 = build_field_tables(m1, GF, lam1)
    index2, coeff2 = build_field_tables(m2, GF, lam2)
    # разбиение на блоки
    blocks = [X[i*m1:(i+1)*m1] for i in range(m2)]
    # первый слой
    powered = [power_vector(b, k1, index1, coeff1, GF) for b in blocks]
    # транспонирование
    transposed = [[powered[k][t] for k in range(m2)] for t in range(m1)]
    # второй слой
    final = [power_vector(t, k2, index2, coeff2, GF) for t in transposed]
    # сборка
    return [coord for block in final for coord in block]

if __name__ == "__main__":
    p = 13
    GF = galois.GF(p)
    m1, lam1 = 2, GF(2)
    m2, lam2 = 2, GF(3)
    X = [GF(random.randint(0, p-1)) for _ in range(m1*m2)]
    Y = cascade_transform(X, m1, lam1, m2, lam2, GF)
    print("X =", [int(x) for x in X])
    print("Y =", [int(y) for y in Y])