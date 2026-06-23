import galois
import random
from polynomials import build_field_tables, power_vector

def encrypt_debug(X, eta, mu, GF, lam1, lam2, degree):
    index1, coeff1 = build_field_tables(eta, GF, lam1)
    index2, coeff2 = build_field_tables(mu, GF, lam2)
    blocks = [X[i*eta:(i+1)*eta] for i in range(mu)]
    powered1 = [power_vector(b, degree, index1, coeff1, GF) for b in blocks]
    transposed = [[powered1[k][t] for k in range(mu)] for t in range(eta)]
    final = [power_vector(t, degree, index2, coeff2, GF) for t in transposed]
    return [coord for block in final for coord in block]

def decrypt_debug(Y, eta, mu, GF, lam1, lam2, degree):
    order = GF.order**eta - 1
    s = pow(degree, -1, order)
    print(f"order = {order}, degree = {degree}, s = {s}")
    
    index1, coeff1 = build_field_tables(eta, GF, lam1)
    index2, coeff2 = build_field_tables(mu, GF, lam2)
    
    # Второй слой
    blocks2 = [Y[i*mu:(i+1)*mu] for i in range(eta)]
    inv_blocks2 = [power_vector(b, s, index2, coeff2, GF) for b in blocks2]
    print("inv_blocks2:", [[int(x) for x in b] for b in inv_blocks2])
    
    # Транспонирование обратное
    transposed_inv = [[inv_blocks2[k][t] for k in range(eta)] for t in range(mu)]
    print("transposed_inv:", [[int(x) for x in b] for b in transposed_inv])
    
    # Первый слой
    dec_blocks = [power_vector(b, s, index1, coeff1, GF) for b in transposed_inv]
    print("dec_blocks:", [[int(x) for x in b] for b in dec_blocks])
    
    return [coord for block in dec_blocks for coord in block]

eta, mu = 2, 2
degree = 5
GF = galois.GF(2**3)
lam1, lam2 = 2, 3

X = [GF(6), GF(6), GF(1), GF(3)]
Y = encrypt_debug(X, eta, mu, GF, lam1, lam2, degree)
print("Y =", [int(y) for y in Y])

X_dec = decrypt_debug(Y, eta, mu, GF, lam1, lam2, degree)
print("X_dec =", [int(x) for x in X_dec])