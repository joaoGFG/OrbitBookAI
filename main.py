from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, destinos, reservas, avaliacoes, usuarios, ai

app = FastAPI(
    title="OrbitBook API",
    description="Plataforma de Reservas para Turismo Espacial — FIAP Global Solution 2026/1",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajuste para o domínio do front em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(destinos.router)
app.include_router(reservas.router)
app.include_router(avaliacoes.router)
app.include_router(usuarios.router)
app.include_router(ai.router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "app": "OrbitBook API", "version": "1.0.0"}


@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}
