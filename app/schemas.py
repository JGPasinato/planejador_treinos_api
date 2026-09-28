from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

TipoTreino = Literal["corrida", "caminhada", "ciclismo", "funcional"]
StatusTreino = Literal["planejado", "apto", "atencao", "cancelado", "realizado"]


class TreinoCreate(BaseModel):
    titulo: str = Field(min_length=3, max_length=120)
    tipo: TipoTreino
    cidade: str = Field(min_length=2)
    duracao_min: int = Field(ge=10, le=300)
    data_hora: datetime
    notas: str | None = None


class TreinoUpdate(BaseModel):
    titulo: str | None = Field(None, min_length=3, max_length=120)
    tipo: TipoTreino | None = None
    cidade: str | None = None
    duracao_min: int | None = Field(None, ge=10, le=300)
    data_hora: datetime | None = None
    status: StatusTreino | None = None
    notas: str | None = None


class TreinoOut(TreinoCreate):
    id: int
    status: str
    ultima_avaliacao: str | None = None
    temperatura_c: float | None = None

    model_config = {"from_attributes": True}


class Resumo(BaseModel):
    total: int
    por_status: dict[str, int]
    por_tipo: dict[str, int]
