from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from routers.auth import hash_senha, verificar_senha, criar_token, get_usuario_atual
import models, schemas

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.TokenOut, status_code=201)
def register(payload: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    existente = db.query(models.UserOrbit).filter(models.UserOrbit.email == payload.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    role = db.query(models.Role).filter(models.Role.name_role == payload.role).first()
    if not role:
        raise HTTPException(status_code=400, detail=f"Role '{payload.role}' não encontrado no banco")

    usuario = models.UserOrbit(
        name=payload.nome,
        email=payload.email,
        password_hash=hash_senha(payload.senha),
        id_role=role.id_role,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    token = criar_token({"sub": str(usuario.id_users_orbit)})
    return schemas.TokenOut(
        access_token=token,
        usuario=schemas.UsuarioOut.model_validate(usuario),
    )


@router.post("/login", response_model=schemas.TokenOut)
def login(payload: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(models.UserOrbit).filter(models.UserOrbit.email == payload.email).first()
    if not usuario or not verificar_senha(payload.senha, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )
    token = criar_token({"sub": str(usuario.id_users_orbit)})
    return schemas.TokenOut(
        access_token=token,
        usuario=schemas.UsuarioOut.model_validate(usuario),
    )


@router.get("/me", response_model=schemas.UsuarioOut)
def me(usuario=Depends(get_usuario_atual)):
    return usuario
