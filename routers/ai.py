import os
import re
import json
import httpx
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from auth import get_usuario_atual
import models

router = APIRouter(prefix="/ai", tags=["IA"])

GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash-lite"]
_GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

_SYSTEM_BASE = """Você é ARIA, assistente de viagens espaciais do OrbitBook.

ESTILO: Respostas curtas e diretas — 1 a 3 frases no máximo. Tom animado, próximo, sem enrolação. Sempre em português do Brasil.

REGRA DE RECOMENDAÇÃO:
Sempre que o usuário pedir uma viagem ou você sugerir um destino, use EXCLUSIVAMENTE os IDs dos destinos listados no catálogo.
Não invente destinos. Se não houver destino que caiba no orçamento, explique isso gentilmente.
"""

def _truncate_bytes(text: str, max_bytes: int) -> str:
    encoded = text.encode("utf-8")
    if len(encoded) <= max_bytes:
        return text
    return encoded[:max_bytes].decode("utf-8", errors="ignore")

def _build_system_prompt(destinos: list) -> str:
    regras = """
=== REGRAS DE CÁLCULO E CONTEÚDO ===
- O campo "content" NUNCA deve conter tags, IDs ou mencionar a palavra JSON.
- O campo "destino_ids" deve conter apenas os números inteiros. Deixe vazio [] se não recomendar nada.
- Quando o usuário informar quantidade de pessoas, calcule o custo aproximado como preco_base * pessoas.
- Para microgravidade e viagem curta, priorize destinos orbitais/LEO se couberem no orçamento.
"""
    linhas = [_SYSTEM_BASE, regras, "\n=== Destinos disponíveis ==="]
    for d in destinos:
        tipo = d.destination_type.name if d.destination_type else "N/A"
        linhas.append(
            f"ID={d.id_destinations} | {d.name} | Tipo: {tipo} | "
            f"Cap: {d.capacity}pax | Dist: {d.distance_km}km | "
            f"Preço: R${float(d.base_price):,.2f}"
        )
    return "\n".join(linhas)

def _extrair_json_ia(text: str) -> tuple[str, list[str], list[int]]:
    inicio = text.find('{')
    fim = text.rfind('}')
    
    if inicio != -1 and fim != -1:
        raw = text[inicio:fim+1]
    else:
        raw = text.strip()

    try:
        data = json.loads(raw, strict=False)
        content = str(data.get("content", "")).strip()
        suggestions = data.get("suggestions") or []
        destino_ids = data.get("destino_ids") or []
        
        suggestions = [str(s).strip() for s in suggestions if str(s).strip()][:3]
        destino_ids = [int(i) for i in destino_ids if str(i).isdigit() or isinstance(i, int)][:3]
        return content, suggestions, destino_ids
    except json.JSONDecodeError:
        print(f"\n[ERRO DE JSON] A IA respondeu com um formato inválido:\n{text}\n")
        return "Desculpe, tive um pequeno problema de comunicação espacial. Pode reformular a pergunta?", [], []

def _get_avaliacao(db: Session, dest_id: int) -> Optional[dict]:
    result = (
        db.query(
            func.avg(models.Review.rating).label("media"),
            func.count(models.Review.id_reviews).label("total"),
        )
        .join(models.Booking, models.Review.id_bookings == models.Booking.id_bookings)
        .filter(models.Booking.id_destinations == dest_id)
        .first()
    )
    if not result or not result.total or result.total == 0:
        return None
    return {"media": round(float(result.media), 1), "total": result.total}

def _sugestoes(user_msg: str, ai_resp: str) -> List[str]:
    msg = (user_msg + " " + ai_resp).lower()
    if any(w in msg for w in ("lua", "lunar")):
        return ["Quais são os requisitos?", "Como é o treinamento?", "Ver outras opções"]
    if any(w in msg for w in ("marte", "marciano")):
        return ["Quem pode se candidatar?", "Como funciona a seleção?", "Ver outros destinos"]
    if any(w in msg for w in ("suborbital", "orbital")):
        return ["Quanto tempo dura a missão?", "Como funciona o treinamento?", "Quero reservar"]
    if any(w in msg for w in ("preço", "custo", "valor", "quanto", "orçamento", "acessível")):
        return ["Como funciona o pagamento?", "Destino mais barato disponível?", "Simular valor total"]
    if any(w in msg for w in ("requisito", "físico", "saúde", "médico", "apto")):
        return ["Tenho problema cardíaco, posso ir?", "Como é o exame médico?", "Requisitos completos"]
    return ["Destinos mais acessíveis", "Missões com alta avaliação", "Opções para grupos grandes"]

# ── Schemas ──────────────────────────────────────────────────
class MensagemChat(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[MensagemChat]

class AvaliacaoResumo(BaseModel):
    media: float
    total: int

class DestinoRecomendado(BaseModel):
    id: int
    nome: str
    tipo: Optional[str]
    descricao: str
    preco_base: float
    distance_km: float
    image_url: str
    capacidade_max: int
    avaliacao: Optional[AvaliacaoResumo] = None
    ativo: int = 1

class ChatResponse(BaseModel):
    content: str
    suggestions: List[str]
    recomendacao_id: Optional[int] = None
    destinos_recomendados: List[DestinoRecomendado] = []

# ── Endpoint ─────────────────────────────────────────────────
@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual),
):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(500, "GEMINI_API_KEY não configurada")

    api_key_limpa = api_key.strip()
    destinos = db.query(models.Destination).join(models.DestinationType).all()
    system_prompt = _build_system_prompt(destinos)

    messages = [m for m in payload.messages if m.role in ("user", "assistant")]
    start = next((i for i, m in enumerate(messages) if m.role == "user"), None)
    if start is None:
        raise HTTPException(400, "Nenhuma mensagem de usuário encontrada")
    messages = messages[start:]

    contents = [
        {"role": "model" if m.role == "assistant" else "user", "parts": [{"text": m.content}]}
        for m in messages
    ]

    body = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": contents,
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "content": {"type": "STRING"},
                    "suggestions": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"}
                    },
                    "destino_ids": {
                        "type": "ARRAY",
                        "items": {"type": "INTEGER"}
                    }
                },
                "required": ["content", "suggestions", "destino_ids"]
            }
        },
    }

    resp = None
    used_model = GEMINI_MODELS[0]
    with httpx.Client(timeout=30) as client:
        for model in GEMINI_MODELS:
            url = _GEMINI_BASE.format(model=model) + f"?key={api_key_limpa}"
            r = client.post(url, json=body, headers={"Content-Type": "application/json"})
            if r.status_code not in (429, 503):
                resp = r
                used_model = model
                break
            print(f"[GEMINI] {model} → {r.status_code}, tentando próximo...")

    if resp is None or not resp.is_success:
        status_code = resp.status_code if resp else 502
        body_text = resp.text[:200] if resp else "sem resposta"
        print(f"[GEMINI ERROR] status={status_code} body={body_text}")
        raise HTTPException(502, f"Erro da API Gemini: {status_code} — {body_text}")

    data = resp.json()
    candidate = data.get("candidates", [{}])[0]
    finish_reason = candidate.get("finishReason", "")
    if finish_reason in ("SAFETY", "RECITATION", "OTHER"):
        raise HTTPException(502, f"Resposta bloqueada pelo modelo: {finish_reason}")
    raw_text = (
        candidate.get("content", {})
        .get("parts", [{}])[0]
        .get("text")
    )
    if not raw_text:
        raise HTTPException(502, "Resposta inválida da API Gemini")

    clean_text, ai_suggestions, dest_ids = _extrair_json_ia(raw_text)
    last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")

    destinos_recomendados: List[DestinoRecomendado] = []
    for did in dest_ids:
        d = db.query(models.Destination).filter(models.Destination.id_destinations == did).first()
        if d:
            av_dict = _get_avaliacao(db, did)
            av = AvaliacaoResumo(**av_dict) if av_dict else None
            destinos_recomendados.append(
                DestinoRecomendado(
                    id=d.id_destinations,
                    nome=d.name,
                    tipo=d.destination_type.name if d.destination_type else None,
                    descricao=d.description,
                    preco_base=float(d.base_price),
                    distance_km=float(d.distance_km),
                    image_url=d.image_url,
                    capacidade_max=d.capacity,
                    avaliacao=av,
                )
            )

    recomendacao_id = None
    try:
        rec = models.AIRecomendation(
            prompt_used=_truncate_bytes(last_user, 700),
            response_text=_truncate_bytes(clean_text, 490),
            model_used=used_model,
            id_users_orbit=usuario.id_users_orbit,
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        recomendacao_id = rec.id_ai_recomendation
    except Exception:
        db.rollback()

    return ChatResponse(
        content=clean_text,
        suggestions=ai_suggestions or _sugestoes(last_user, clean_text),
        recomendacao_id=recomendacao_id,
        destinos_recomendados=destinos_recomendados,
    )

@router.get("/historico", response_model=List[dict])
def historico(
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual),
):
    recs = (
        db.query(models.AIRecomendation)
        .filter(models.AIRecomendation.id_users_orbit == usuario.id_users_orbit)
        .order_by(models.AIRecomendation.created_at.desc())
        .limit(20)
        .all()
    )
    return [
        {
            "id": r.id_ai_recomendation,
            "prompt": r.prompt_used,
            "resposta": r.response_text,
            "modelo": r.model_used,
            "criado_em": r.created_at,
        }
        for r in recs
    ]