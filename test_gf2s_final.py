import galois
import random
from math import gcd
from polynomials import build_field_tables, power_vector_slow

def test_gf2s(s, m, degree, verbose=True):
    print(f"\nТест: GF(2^{s}), m={m}, k={degree}")
    eta = mu = m
    GF = galois.GF(2**s)
    lam1, lam2 = GF(2), GF(3)
    
    if (2**s - 1) % m != 0:
        if verbose: print(f"  ❌ {m} не делит 2^{s}-1")
        return False
    order = 2**(s*m) - 1
    if gcd(degree, order) != 1:
        if verbose: print(f"  ❌ gcd({degree},{order}) ≠ 1")
        return False
    
    if verbose: print(f"  ✅ условия выполнены")
    
    index1, coeff1 = build_field_tables(eta, GF, lam1)
    index2, coeff2 = build_field_tables(mu, GF, lam2)
    
    X = [GF(random.randint(1, GF.order-1)) for _ in range(eta*mu)]
    
    def encrypt_slow(X):
        blocks = [X[i*eta:(i+1)*eta] for i in range(mu)]
        powered1 = [power_vector_slow(b, degree, index1, coeff1, GF) for b in blocks]
        transposed = [[powered1[k][t] for k in range(mu)] for t in range(eta)]
        final = [power_vector_slow(t, degree, index2, coeff2, GF) for t in transposed]
        return [coord for block in final for coord in block]
    
    Y = encrypt_slow(X)
    
    s1 = pow(degree, -1, GF.order**eta - 1)
    s2 = pow(degree, -1, GF.order**mu - 1)
    
    def decrypt_slow(Y):
        blocks2 = [Y[i*mu:(i+1)*mu] for i in range(eta)]
        inv_blocks2 = [power_vector_slow(b, s2, index2, coeff2, GF) for b in blocks2]
        transposed_inv = [[inv_blocks2[k][t] for k in range(eta)] for t in range(mu)]
        dec_blocks = [power_vector_slow(b, s1, index1, coeff1, GF) for b in transposed_inv]
        return [coord for block in dec_blocks for coord in block]
    
    X_dec = decrypt_slow(Y)
    
    if [int(x) for x in X] == [int(x) for x in X_dec]:
        if verbose: print("  ✅ обратимость работает")
        return True
    else:
        if verbose: print("  ❌ обратимость не работает")
        return False

if __name__ == "__main__":
    # Подходящие параметры (те, которые должны работать)
    params = [
        (4, 3, 11),   # ✅ уже проверено
        (4, 3, 2),    # gcd(2,4095)=1
        (4, 3, 4),    # gcd(4,4095)=1
        (6, 3, 5),    # gcd(5,262143)=1
        (6, 3, 11),   # gcd(11,262143)=1? 262143/11=23831.18 → 11*23831=262141, остаток 2 → да, взаимно просты
        (8, 3, 5),    # gcd(5,16777215)=1? 16777215/5=3355443 → да
        (8, 5, 7),    # gcd(7,2^40-1)=? 2^40-1 mod 7 =? скорее всего 1, т.к. 2^3=8≡1 mod7 → 2^39≡1, 2^40≡2, 2^40-1≡1 → gcd=1
        (8, 5, 9),    # 9=3^2, 2^40-1 mod3=0? 2 mod3=-1, (-1)^40=1, 1-1=0 → делится на 3 → не подходит
    ]
    
    for s, m, k in params:
        test_gf2s(s, m, k)