from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func

from app.database import Base


class Treino(Base):
    __tablename__ = "treinos"

    id = Column(Integer, primary_key=True)
    titulo = Column(String(120), nullable=False)
    tipo = Column(String(40), nullable=False)
    cidade = Column(String(120), nullable=False)
    duracao_min = Column(Integer, nullable=False)
    data_hora = Column(DateTime, nullable=False)
    status = Column(String(20), default="planejado")
    notas = Column(Text)
    ultima_avaliacao = Column(Text)
    temperatura_c = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
