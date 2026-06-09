# 🚀 OrbitBook - Motor de IA Generativa (Concierge Espacial)
**Global Solution 2026/1 - FIAP**
**Disciplina:** Disruptive Architectures: IOT, IOB & Generative IA

Este repositório contém exclusivamente a arquitetura do **Motor de Inteligência Artificial** do OrbitBook, focado em resolver o problema de descentralização e falta de personalização no turismo espacial.

A nossa IA não atua como um simples chatbot isolado, mas como um **Concierge Espacial** integrado. Ele processa o perfil do viajante, cruza restrições de negócio (orçamento, capacidade e nível de risco) diretamente com o banco de dados e retorna sugestões justificadas em linguagem natural, prontas para reserva.

## 🎥 Pitch e Demonstração Funcional
* [Assista ao vídeo da IA em funcionamento no YouTube (Máx 3 min)]([#](https://youtu.be/NgRlAl6Zscc
))
* [Acesse o Front-end Completo do OrbitBook](https://github.com/caiolucasxz55/orbitbook-frontend)

---

## 🧠 Arquitetura e Integração

O motor de IA foi desenvolvido como um microserviço independente em FastAPI, responsável pela autenticação, integração com o Google Gemini e persistência dos dados no Oracle Database. A aplicação segue uma arquitetura desacoplada, permitindo que qualquer cliente (Web, Mobile ou Swagger) consuma os recursos por meio de APIs REST.

### ⚙️ Fluxo de Funcionamento

1. **Autenticação (JWT):** O usuário realiza login utilizando e-mail e senha. As credenciais são validadas e um token JWT é emitido para acesso aos endpoints protegidos.
2. **Consulta Inteligente:** O cliente envia uma mensagem para o endpoint `/ai/chat` juntamente com o token JWT.
3. **Construção de Contexto Dinâmico:** A API consulta o Oracle Database e monta dinamicamente um catálogo atualizado de destinos espaciais, incluindo preços, capacidade, distância e categoria.
4. **Inferência com IA Generativa:** O catálogo é enviado ao Google Gemini juntamente com o histórico da conversa. O modelo recebe instruções para atuar como concierge espacial e responder utilizando um esquema JSON rigidamente definido.
5. **Resposta Estruturada:** O Gemini retorna um JSON contendo:
   * Texto da recomendação (`content`)
   * Sugestões de próximas perguntas (`suggestions`)
   * IDs dos destinos recomendados (`destino_ids`)
6. **Enriquecimento dos Dados:** A API utiliza os IDs retornados para consultar novamente o banco de dados, recuperando informações completas dos destinos e suas avaliações médias em tempo real.
7. **Persistência e Histórico:** O prompt do usuário, a resposta gerada e o modelo utilizado são armazenados para auditoria e histórico de recomendações.
8. **Resposta ao Front-end:** O cliente recebe uma resposta estruturada contendo a mensagem da IA, sugestões de interação e os dados completos dos destinos recomendados.

### 🛠️ Tecnologias Utilizadas
* **Linguagem:** Python 3.12
* **Framework Web:** FastAPI + Uvicorn
* **IA Generativa:** Google Gemini API
* **Structured Output:** Gemini Response Schema (JSON estruturado)
* **Banco de Dados:** Oracle Database
* **ORM:** SQLAlchemy + oracledb
* **Autenticação:** JWT (JSON Web Token)
* **Segurança:** bcrypt (passlib)
* **HTTP Client:** httpx

---

## 🚀 Como Executar este Microserviço Localmente

Siga o exemplo do .env.example:
ORACLE_USER=user
ORACLE_PASSWORD=senha
ORACLE_DSN=oracle.fiap.com.br:1521/orcl
SECRET_KEY=orbitbook-secret-key-2026-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GEMINI_API_KEY=sua_chave

1. Clone o repositório
``` git clone https://github.com/SEU_USUARIO/orbitbook-ai-api.git ```
``` cd orbitbook-ai-api ```

2. Crie e ative o ambiente virtual (Windows PowerShell):
```py -3.12 -m venv .venv ``` depois
```.\.venv\Scripts\activate ```

4. Instale as dependências:
```pip install -r requirements.txt```

5. Configuração de Variáveis de Ambiente:
Crie um arquivo .env na raiz do projeto e cole o que está no .env.example mas com suas credenciais

6. Inicie o Servidor Local:
```uvicorn main:app --reload```

A API estará disponível em http://127.0.0.1:8000. Você pode testar os endpoints interativamente acessando http://127.0.0.1:8000/docs.

---

## 🧪 Exemplo de Uso do Endpoint /ai/chat

Requisição (POST):
```
{
  "messages": [
    {
      "role": "user",
      "content": "Tenho um orçamento de 80 milhões de dólares e procuro uma viagem curta para duas pessoas em microgravidade."
    }
  ]
}
```

Resposta do Motor: O sistema rejeita automaticamente pacotes acima do orçamento (ex: Lua) e cruza as variáveis para recomendar pacotes em Órbita LEO:
```
{
  "content": "Para o seu orçamento de 80 milhões e desejo de microgravidade contínua, a Órbita Baixa (LEO) é o ideal para o casal! A Estação Axiom oferece estadias incríveis e caberá perfeitamente na sua carteira.",
  "suggestions": [
    "Como funciona o treinamento?",
    "Quais são os requisitos físicos?"
  ],
  "recomendacao_id": 14,
  "destinos_recomendados": [
    {
      "id": 2,
      "nome": "Estação Orbital LEO",
      "preco_base": 35000000.0,
      "capacidade_max": 8
    }
  ]
}
```
## 🧠 Imagem da arquitetura

<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/6279d905-cf25-4190-90fe-6b96f886a2d7" />




