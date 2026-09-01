# Sales Intelligence

MVP de uma plataforma de inteligência e automação de processos comerciais, focado em um único
caso de uso: **qualificação de leads**.

O sistema recebe uma mensagem de um lead e produz uma análise comercial estruturada: score,
qualificação, motivos, dores identificadas, intenção de compra, próxima ação recomendada e uma
resposta comercial sugerida — sempre revisável por um humano antes de qualquer envio.

Este não é um CRM, nem um agente de IA genérico, nem um BPMS. É um experimento de negócio para
validar se essa análise é suficientemente útil para entrar no processo comercial de uma empresa.
Ver `CLAUDE.md`/`SPEC.md` (não versionados, ver seção [Documentação de contexto](#documentação-de-contexto-não-versionada)) para os princípios completos do projeto.

## Princípio central: IA sugere, o sistema decide

O LLM produz dados estruturados (score, qualificação, dores, etc.), validados por Pydantic. As
decisões que importam para o negócio — priorização e próxima ação — são recalculadas
deterministicamente pelo backend (`backend/app/services/classification_service.py`), nunca
aceitas cegamente do modelo. Nenhuma mensagem é enviada automaticamente: a resposta sugerida
sempre passa por um humano (`[Editar]` / `[Copiar]` na interface).

## Arquitetura

```text
Frontend (React + Vite)
   |
   v
FastAPI
   |
   +---- PostgreSQL (companies, leads, analyses, interactions)
   |
   +---- Regras determinísticas (prioridade, próxima ação)
   |
   +---- LangGraph (START -> analyze_lead -> generate_response -> END)
                |
                +---- LLM (via camada de abstração, hoje OpenAI)
```

## Stack

- **Backend**: Python 3.12, FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL
- **IA**: LangGraph + LangChain, saída estruturada validada por Pydantic
- **Frontend**: React + TypeScript + Vite (sem framework de UI)
- **Infra**: Docker + Docker Compose

## Pré-requisitos

- Docker e Docker Compose
- Uma chave de API da OpenAI (`OPENAI_API_KEY`)
- Node.js 20+ para rodar o frontend (recomendado via [nvm](https://github.com/nvm-sh/nvm))
- Python 3.12+ apenas se quiser rodar o backend fora do Docker

## Como rodar

### 1. Configurar variáveis de ambiente

Na raiz do projeto:

```bash
cp .env.example .env
```

Edite `.env` e preencha `LLM_API_KEY` com sua chave da OpenAI. **Nunca commite o `.env` real** —
ele já está no `.gitignore`.

### 2. Subir backend + banco de dados

```bash
docker compose up --build
```

Isso sobe o Postgres e o backend (a imagem do backend roda `alembic upgrade head`
automaticamente antes de iniciar o servidor). A API fica disponível em
`http://localhost:8000` (`GET /health` para verificar) e a documentação interativa em
`http://localhost:8000/docs`.

### 3. Popular dados de demonstração (opcional, recomendado)

Com os containers no ar, em outro terminal:

```bash
docker compose exec backend python -m app.seed
```

Cria a empresa fictícia "Acme Sales" e 10 leads cobrindo diferentes cenários (qualificado, fora
do ICP, sem informação suficiente, alta urgência, pergunta de preço, etc. — ver
`backend/app/seed.py`). O comando é idempotente: rodar de novo não duplica os dados.

### 4. Subir o frontend

```bash
cd frontend
nvm use --lts    # ou instale Node 20+ de outra forma
npm install
cp .env.example .env   # VITE_API_URL, default http://localhost:8000
npm run dev
```

Acesse `http://localhost:5173`.

### 5. Testar o fluxo completo

No frontend: Dashboard → "Cadastrar empresa" (copie o ID mostrado) → "Cadastrar lead" (cole o ID
da empresa) → abra o lead → "Executar análise" → veja score, motivos, dores, próxima ação e
resposta sugerida. Ou pule os cadastros e use os leads do seed em "Leads".

**Atenção**: "Executar análise" faz uma chamada real à API da OpenAI (custo e latência reais,
~5-10s por análise).

## Rodando o backend fora do Docker (desenvolvimento)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Banco local via Docker, API/testes localmente:
docker compose up -d postgres
export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/sales_intelligence"
alembic upgrade head
uvicorn app.main:app --reload
```

## Testes

```bash
cd backend
source .venv/bin/activate  # ou pip install -r requirements.txt num venv novo
python -m pytest
```

Os testes usam um Postgres embutido efêmero (`pgserver`) por sessão de teste — não precisam do
Docker Compose rodando. Chamadas ao LLM são sempre mockadas nos testes automatizados (ver skill
`testing`); a validação com a OpenAI real é manual, via `docker compose` + seed, como descrito
acima.

## API

```text
POST /companies                    cria empresa
GET  /companies/{company_id}       retorna empresa

POST /leads                        cria lead (status inicial "new")
GET  /leads                        lista leads, ordenados por score desc
GET  /leads/{lead_id}              retorna lead + análise mais recente

POST /leads/{lead_id}/analyze      executa a análise (LangGraph + regras determinísticas)
GET  /leads/{lead_id}/analysis     retorna a análise persistida
```

Falha do LLM (timeout, indisponibilidade, saída inválida) marca o lead como `error` e nunca
persiste uma análise inválida — a API responde com uma mensagem amigável, sem stack trace.

## Estrutura do backend

```text
backend/app/
├── api/            # rotas FastAPI (finas, delegam para services)
├── services/        # regras de negócio e orquestração
├── models/           # SQLAlchemy
├── schemas/         # Pydantic (entrada/saída, incl. validação da saída do LLM)
├── repositories/    # acesso a dados
├── agents/          # grafo LangGraph, prompts, abstração de LLM
└── core/            # config, db, enums
```

## O que este MVP não faz (por decisão de escopo)

Sem envio automático de mensagens, sem WhatsApp/email, sem CRM completo, sem múltiplos agentes,
sem RAG/vector database, sem workflow builder. Toda resposta comercial é apenas sugerida — um
humano decide se edita e envia. Ver a documentação de contexto do projeto para a lista completa
e o racional.

## Documentação de contexto (não versionada)

`CLAUDE.md`, `SPEC.md` e `TASKS.md`, na raiz do projeto, guardam a especificação completa, os
princípios de arquitetura e o plano de fases do MVP — ficam fora do Git por decisão do projeto
(ver `.gitignore` e a skill `git_workflow`), mas existem localmente no repositório de
desenvolvimento.
