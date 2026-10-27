import logging
import time
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from math_logic import (
    validate_params, generate_key_polynomials,
    encrypt_vector, decrypt_vector, run_round_trip_test,
    get_field,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cascade Scheme API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-domain.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CascadeParams(BaseModel):
    field_order: int = Field(13, description="Порядок поля GF(q): 13, 16, 8, …")
    eta: int = Field(2, ge=1, description="Размер первого слоя")
    mu: int = Field(2, ge=1, description="Размер второго слоя")
    degree: int = Field(3, ge=1, description="Степень k")
    lam1: int = Field(2, ge=0)
    lam2: int = Field(3, ge=0)

class EncryptRequest(CascadeParams):
    X: List[int] = Field(..., description="Вектор X (целые 0..q-1)")

class DecryptRequest(CascadeParams):
    Y: List[int] = Field(..., description="Вектор Y (целые 0..q-1)")

def _check_size(params: CascadeParams, for_symbolic: bool = False):
    if params.eta * params.mu > 16:
        raise HTTPException(400, "η·μ > 16 — слишком большая размерность")
    if for_symbolic and (params.eta > 5 or params.mu > 5 or params.degree > 5):
        raise HTTPException(400, "Символьная генерация: ограничьте η, μ, k ≤ 5")

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/validate")
async def api_validate(p: CascadeParams):
    try:
        return validate_params(p.field_order, p.eta, p.mu, p.degree)
    except Exception as e:
        logger.error(f"validate: {e}", exc_info=True)
        raise HTTPException(500, str(e))


@app.post("/api/generate")
async def api_generate(p: CascadeParams):
    _check_size(p, for_symbolic=True)
    v = validate_params(p.field_order, p.eta, p.mu, p.degree)
    if not v["valid"]:
        raise HTTPException(400, {"message": "Параметры не прошли валидацию", "checks": v["checks"]})
    try:
        return generate_key_polynomials(p.eta, p.mu, p.field_order, p.degree, p.lam1, p.lam2)
    except Exception as e:
        logger.error(f"generate: {e}", exc_info=True)
        raise HTTPException(500, str(e))


@app.post("/api/encrypt")
async def api_encrypt(r: EncryptRequest):
    _check_size(r)
    GF = get_field(r.field_order)
    if len(r.X) != r.eta * r.mu:
        raise HTTPException(400, f"Длина X должна быть η·μ = {r.eta * r.mu}")
    if any(not (0 <= int(x) < GF.order) for x in r.X):
        raise HTTPException(400, f"Все элементы X должны быть в диапазоне [0, {GF.order - 1}]")
    try:
        return encrypt_vector(r.X, r.eta, r.mu, r.field_order, r.degree, r.lam1, r.lam2)
    except Exception as e:
        logger.error(f"encrypt: {e}", exc_info=True)
        raise HTTPException(500, str(e))


@app.post("/api/decrypt")
async def api_decrypt(r: DecryptRequest):
    _check_size(r)
    GF = get_field(r.field_order)
    if len(r.Y) != r.eta * r.mu:
        raise HTTPException(400, f"Длина Y должна быть η·μ = {r.eta * r.mu}")
    if any(not (0 <= int(y) < GF.order) for y in r.Y):
        raise HTTPException(400, f"Все элементы Y должны быть в диапазоне [0, {GF.order - 1}]")
    v = validate_params(r.field_order, r.eta, r.mu, r.degree)
    if not v["valid"]:
        raise HTTPException(
            status_code=400,
            detail="Расшифрование невозможно: степень k необратима для этих параметров. "
                   f"gcd({r.degree}, {GF.order**r.eta - 1}) ≠ 1. "
                   "Смените степень k или параметры поля."
        )
    try:
        return decrypt_vector(r.Y, r.eta, r.mu, r.field_order, r.degree, r.lam1, r.lam2)
    except Exception as e:
        logger.error(f"decrypt: {e}", exc_info=True)
        raise HTTPException(500, str(e))


@app.post("/api/test")
async def api_test(p: CascadeParams):
    _check_size(p)
    v = validate_params(p.field_order, p.eta, p.mu, p.degree)
    if not v["valid"]:
        raise HTTPException(
            status_code=400,
            detail="Тест обратимости невозможен: параметры не прошли валидацию "
                   "(степень k необратима для выбранного поля)."
        )
    try:
        return run_round_trip_test(p.eta, p.mu, p.field_order, p.degree, p.lam1, p.lam2)
    except Exception as e:
        logger.error(f"test: {e}", exc_info=True)
        raise HTTPException(500, str(e))