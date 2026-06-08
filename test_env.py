from polynomials import build_field_tables
import galois

GF = galois.GF(13)
index, coeff = build_field_tables(3, GF, 2)
print("Таблица 3x3 создана")
print(index)
print("Всё работает!")