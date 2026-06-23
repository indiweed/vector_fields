import galois
import random
from math import gcd
from polynomials import build_field_tables, power_vector_slow

def test_gf2s(s, m, degree):
    print(f"\n{'='*60}")
    print(f"Тест: GF(2^{s}), m={m}, степень k={degree}")
    print('='*60)
    
    eta = mu = m
    GF = galois.GF(2**s)
    lam1, lam2 = GF(2), GF(3)
    
    # Проверка условия делимости
    if (2**s - 1) % m != 0:
        print(f"❌ {m} не делит 2^{s}-1 = {2**s-1}")
        return False
    
    # Проверка взаимной простоты
    order = 2**(s*m) - 1
    if gcd(degree, order) != 1:
        print(f"❌ Степень {degree} не взаимно проста с порядком {order}")
        return False
    
    print(f"✅ Условия выполнены: {m} | {2**s-1}, gcd({degree},{order})=1")
    
    index1, coeff1 = build_field_tables(eta, GF, lam1)
    index2, coeff2 = build_field_tables(mu, GF, lam2)
    
    X = [GF(random.randint(1, GF.order-1)) for _ in range(eta*mu)]
    print(f"X = {[int(x) for x in X]}")
    
    def encrypt_slow(X):
        blocks = [X[i*eta:(i+1)*eta] for i in range(mu)]
        powered1 = [power_vector_slow(b, degree, index1, coeff1, GF) for b in blocks]
        transposed = [[powered1[k][t] for k in range(mu)] for t in range(eta)]
        final = [power_vector_slow(t, degree, index2, coeff2, GF) for t in transposed]
        return [coord for block in final for coord in block]
    
    Y = encrypt_slow(X)
    print(f"Y = {[int(y) for y in Y]}")
    
    s1 = pow(degree, -1, GF.order**eta - 1)
    s2 = pow(degree, -1, GF.order**mu - 1)
    
    def decrypt_slow(Y):
        blocks2 = [Y[i*mu:(i+1)*mu] for i in range(eta)]
        inv_blocks2 = [power_vector_slow(b, s2, index2, coeff2, GF) for b in blocks2]
        transposed_inv = [[inv_blocks2[k][t] for k in range(eta)] for t in range(mu)]
        dec_blocks = [power_vector_slow(b, s1, index1, coeff1, GF) for b in transposed_inv]
        return [coord for block in dec_blocks for coord in block]
    
    X_dec = decrypt_slow(Y)
    print(f"X_dec = {[int(x) for x in X_dec]}")
    
    if [int(x) for x in X] == [int(x) for x in X_dec]:
        print("✅ Обратимость работает")
        return True
    else:
        print("❌ Ошибка")
        return False

if __name__ == "__main__":
    # Список параметров: (s, m, degree)
    params = [
        (4, 3, 11),   # уже работает
        (4, 3, 13),   # тоже должно работать
        (4, 5, 11),   # s=4, m=5, k=11 (проверим)
        (6, 3, 5),    # s=6, m=3, k=5
        (6, 3, 11),   # s=6, m=3, k=11
        (8, 3, 5),    # s=8, m=3, k=5
        (8, 5, 3),    # s=8, m=5, k=3 (интересно)
        (8, 5, 7),    # s=8, m=5, k=7
    ]
    
    success_count = 0
    for s, m, degree in params:
        if test_gf2s(s, m, degree):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"ИТОГ: {success_count}/{len(params)} тестов успешны")