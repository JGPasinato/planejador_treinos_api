import os

import httpx
from fastapi import HTTPException

REGRAS_API_URL = os.getenv("REGRAS_API_URL", "http://localhost:8001")


def avaliar_treino(tipo, cidade, data_hora):
    try:
        resp = httpx.post(
            f"{REGRAS_API_URL}/avaliar",
            json={"tipo_treino": tipo, "cidade": cidade, "data_hora": data_hora.isoformat()},
            timeout=20,
        )
    except httpx.RequestError:
        raise HTTPException(503, "API de regras indisponível")

    if resp.status_code != 200:
        try:
            detalhe = resp.json()["detail"]
        except Exception:
            detalhe = resp.text
        raise HTTPException(resp.status_code, detalhe)

    return resp.json()
