from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importamos APENAS os roteadores necessários para a IA e Autenticação
from routers import auth, ai

app = FastAPI(
    title="OrbitBook API - Motor de IA",
    description="Motor de Inteligência Artificial Generativa para Turismo Espacial — FIAP Global Solution 2026/1",
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

# Registramos apenas as rotas avaliadas na disciplina
app.include_router(auth.router)
app.include_router(ai.router)

@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "app": "OrbitBook AI API", "version": "1.0.0"}

@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy"}