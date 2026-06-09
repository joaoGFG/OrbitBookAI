from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator
from decimal import Decimal


# ── Auth ──────────────────────────────────────────────────
class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    role: str = "VIAJANTE"

    @field_validator("role")
    @classmethod
    def validar_role(cls, v):
        if v not in ("VIAJANTE", "ADMIN"):
            raise ValueError("role inválido. Use: VIAJANTE ou ADMIN")
        return v


class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str


class UsuarioOut(BaseModel):
    id: int
    nome: str
    email: str
    role: Optional[str]
    criado_em: Optional[datetime]

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut


# ── Destinos ──────────────────────────────────────────────
class DestinoCreate(BaseModel):
    nome: str
    tipo: str
    descricao: str
    distance_km: Decimal
    preco_base: Decimal
    capacidade_max: int
    image_url: str


class DestinoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    preco_base: Optional[Decimal] = None
    image_url: Optional[str] = None


class AvaliacaoResumo(BaseModel):
    media: float
    total: int


class DestinoOut(BaseModel):
    id: int
    nome: str
    tipo: Optional[str]
    descricao: str
    capacidade_max: int
    preco_base: Decimal
    distance_km: Decimal
    image_url: str
    ativo: int
    avaliacao: Optional[AvaliacaoResumo] = None

    model_config = {"from_attributes": True}


# ── Reservas ──────────────────────────────────────────────
class ReservaCreate(BaseModel):
    destino_id: int
    departure_date: date
    return_date: date
    num_passageiros: int = 1


class ReservaStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validar_status(cls, v):
        validos = ("PENDENTE", "CONFIRMADO", "EM_MISSAO", "CONCLUIDO", "CANCELADO")
        if v not in validos:
            raise ValueError(f"status inválido. Use: {validos}")
        return v


class ReservaOut(BaseModel):
    id: int
    usuario_id: int
    destino_id: int
    departure_date: date
    return_date: date
    num_passageiros: int
    valor_total: Decimal
    status: Optional[str]
    criado_em: Optional[datetime]

    model_config = {"from_attributes": True}


class AvaliacaoComUsuario(BaseModel):
    id: int
    booking_id: int
    nota: float
    comentario: Optional[str]
    criado_em: Optional[datetime]
    usuario_nome: Optional[str] = None

    model_config = {"from_attributes": True}


class DestinoPageOut(BaseModel):
    items: List[DestinoOut]
    total: int
    page: int
    pages: int
    limit: int


# ── Avaliações ────────────────────────────────────────────
class AvaliacaoCreate(BaseModel):
    booking_id: int
    nota: float
    comentario: Optional[str] = None

    @field_validator("nota")
    @classmethod
    def validar_nota(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("nota deve ser entre 1 e 5")
        return v


class AvaliacaoOut(BaseModel):
    id: int
    booking_id: int
    usuario_id: Optional[int]
    destino_id: Optional[int]
    nota: float
    comentario: Optional[str]
    criado_em: Optional[datetime]

    model_config = {"from_attributes": True}
