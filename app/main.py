from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.erros import erro_validacao
from app.models import Treino
from app.regras_client import avaliar_treino
from app.schemas import Resumo, StatusTreino, TipoTreino, TreinoCreate, TreinoOut, TreinoUpdate

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Planejador de treinos ao ar livre")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.add_exception_handler(RequestValidationError, erro_validacao)


def buscar_treino(db: Session, treino_id: int) -> Treino:
    treino = db.get(Treino, treino_id)
    if treino is None:
        raise HTTPException(404, "Treino não encontrado")
    return treino


@app.get("/", include_in_schema=False)
def pagina_inicial():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/treinos", response_model=list[TreinoOut])
def listar_treinos(
    tipo: TipoTreino | None = None,
    status: StatusTreino | None = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    query = db.query(Treino)
    if tipo:
        query = query.filter(Treino.tipo == tipo)
    if status:
        query = query.filter(Treino.status == status)
    return query.order_by(Treino.data_hora.desc()).offset(skip).limit(limit).all()


@app.post("/treinos", response_model=TreinoOut, status_code=201)
def criar_treino(dados: TreinoCreate, db: Session = Depends(get_db)):
    treino = Treino(**dados.model_dump())
    db.add(treino)
    db.commit()
    db.refresh(treino)
    return treino


@app.get("/treinos/{treino_id}", response_model=TreinoOut)
def obter_treino(treino_id: int, db: Session = Depends(get_db)):
    return buscar_treino(db, treino_id)


@app.put("/treinos/{treino_id}", response_model=TreinoOut)
def atualizar_treino(treino_id: int, dados: TreinoUpdate, db: Session = Depends(get_db)):
    treino = buscar_treino(db, treino_id)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(treino, campo, valor)
    db.commit()
    db.refresh(treino)
    return treino


@app.delete("/treinos/{treino_id}", status_code=204)
def remover_treino(treino_id: int, db: Session = Depends(get_db)):
    db.delete(buscar_treino(db, treino_id))
    db.commit()


@app.post("/treinos/{treino_id}/avaliar", response_model=TreinoOut)
def avaliar(treino_id: int, db: Session = Depends(get_db)):
    treino = buscar_treino(db, treino_id)
    resultado = avaliar_treino(treino.tipo, treino.cidade, treino.data_hora)

    treino.status = "cancelado" if resultado["status"] == "cancelar" else resultado["status"]
    treino.ultima_avaliacao = " | ".join(resultado["motivos"])
    treino.temperatura_c = resultado["clima"]["temperatura_c"]
    db.commit()
    db.refresh(treino)
    return treino


@app.get("/resumo", response_model=Resumo)
def resumo(db: Session = Depends(get_db)):
    por_status = db.query(Treino.status, func.count()).group_by(Treino.status).all()
    por_tipo = db.query(Treino.tipo, func.count()).group_by(Treino.tipo).all()
    return Resumo(
        total=db.query(Treino).count(),
        por_status=dict(por_status),
        por_tipo=dict(por_tipo),
    )
