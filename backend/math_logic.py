"""Обёртка над каскадной символьной схемой для веб-API."""
import logging
import random
import time
from math import gcd

import galois
import sympy as sp

from polynomials import build_field_tables, power_vector, power_vector_slow
from cascade_polynomials import cascade_polynomials, encrypt, decrypt

logger = logging.getLogger(__name__)


def get_field(field_order: int) -> galois.FieldArray:
    """GF(q) для q — простой или степень простого (13, 16, 8, 25, …)."""
    try:
        return galois.GF(field_order)
    except Exception as e:
        raise ValueError(f"Невозможно создать поле GF({field_order}): {e}")


def validate_params(field_order: int, eta: int, mu: int, degree: int) -> dict:
    """Проверяет условия применимости схемы. Возвращает отчёт по пунктам."""
    checks = []

    try:
        GF = get_field(field_order)
        checks.append({
            "name": "Поле Галуа",
            "ok": True,
            "detail": f"GF({GF.order}), характеристика {GF.characteristic}",
        })
    except ValueError as e:
        return {"valid": False, "checks": [{"name": "Поле Галуа", "ok": False, "detail": str(e)}]}

    q = GF.order

    checks.append({
        "name": "Размерности η, μ",
        "ok": eta >= 1 and mu >= 1,
        "detail": f"n = η·μ = {eta * mu}",
    })
    checks.append({
        "name": "Степень k",
        "ok": degree >= 1,
        "detail": f"k = {degree}",
    })

    order1 = q ** eta - 1
    g1 = gcd(degree, order1)
    checks.append({
        "name": "gcd(k, |F|^η − 1) = 1",
        "ok": g1 == 1,
        "detail": f"gcd({degree}, {order1}) = {g1}",
    })

    order2 = q ** mu - 1
    g2 = gcd(degree, order2)
    checks.append({
        "name": "gcd(k, |F|^μ − 1) = 1",
        "ok": g2 == 1,
        "detail": f"gcd({degree}, {order2}) = {g2}",
    })

    # Для бинарных полей — мягкая рекомендация (см. ваши test_gf2s*.py)
    if GF.characteristic == 2:
        problems = []
        if (q - 1) % eta != 0:
            problems.append(f"η={eta} ∤ |F|−1={q-1}")
        if (q - 1) % mu != 0:
            problems.append(f"μ={mu} ∤ |F|−1={q-1}")
        if problems:
            checks.append({
                "name": "Условия для GF(2^s) (рекомендация)",
                "ok": False,
                "warning": True,
                "detail": "; ".join(problems) + ". Проверьте обратимость через round-trip тест.",
            })
        else:
            checks.append({
                "name": "Условия для GF(2^s)",
                "ok": True,
                "detail": "η, μ делят |F|−1",
            })

    valid = all(c["ok"] for c in checks if not c.get("warning"))
    return {"valid": valid, "checks": checks, "n": eta * mu, "field_order": q}


def _count_terms(poly: sp.Expr) -> int:
    if poly == 0:
        return 0
    try:
        return len(poly.as_ordered_terms())
    except Exception:
        return 1


def generate_key_polynomials(eta: int, mu: int, field_order: int, degree: int,
                              lam1: int, lam2: int) -> dict:
    """Символьная генерация многочленов открытого ключа (SymPy → LaTeX)."""
    start = time.time()
    polys = cascade_polynomials(eta, mu, field_order, 0, lam1, lam2, degree)
    elapsed = (time.time() - start) * 1000

    items = []
    for i, poly in enumerate(polys):
        items.append({
            "index": i,
            "latex": sp.latex(poly),
            "repr": str(poly),
            "num_terms": _count_terms(poly),
        })

    return {
        "polynomials": items,
        "generation_time_ms": round(elapsed, 2),
        "n": eta * mu,
        "field_order": field_order,
    }


def encrypt_vector(X_ints: list[int], eta: int, mu: int, field_order: int,
                   degree: int, lam1: int, lam2: int) -> dict:
    GF = get_field(field_order)
    X = [GF(int(v)) for v in X_ints]

    start = time.time()
    Y = encrypt(X, eta, mu, GF, GF(lam1), GF(lam2), degree)
    elapsed = (time.time() - start) * 1000

    return {"Y": [int(y) for y in Y], "execution_time_ms": round(elapsed, 3)}


def decrypt_vector(Y_ints: list[int], eta: int, mu: int, field_order: int,
                   degree: int, lam1: int, lam2: int) -> dict:
    GF = get_field(field_order)
    Y = [GF(int(v)) for v in Y_ints]

    start = time.time()
    X = decrypt(Y, eta, mu, GF, GF(lam1), GF(lam2), degree)
    elapsed = (time.time() - start) * 1000

    return {"X": [int(x) for x in X], "execution_time_ms": round(elapsed, 3)}


def run_round_trip_test(eta: int, mu: int, field_order: int,
                        degree: int, lam1: int, lam2: int) -> dict:
    GF = get_field(field_order)
    n = eta * mu
    X = [GF(random.randint(0, GF.order - 1)) for _ in range(n)]
    if all(int(x) == 0 for x in X):
        X[0] = GF(1)

    t0 = time.time()
    Y = encrypt(X, eta, mu, GF, GF(lam1), GF(lam2), degree)
    enc_ms = (time.time() - t0) * 1000

    t0 = time.time()
    X_dec = decrypt(Y, eta, mu, GF, GF(lam1), GF(lam2), degree)
    dec_ms = (time.time() - t0) * 1000

    return {
        "success": [int(x) for x in X] == [int(x) for x in X_dec],
        "X": [int(x) for x in X],
        "Y": [int(y) for y in Y],
        "X_decrypted": [int(x) for x in X_dec],
        "encrypt_time_ms": round(enc_ms, 3),
        "decrypt_time_ms": round(dec_ms, 3),
    }