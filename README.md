# Kemi — Agent RAG

Agent RAG agentique avec LangGraph, OpenRouter, et pgvector.

## Quick Start

```bash
cp .env.example .env     # editer OPENROUTER_API_KEY
make up                  # PostgreSQL + pgvector
pip install -r requirements.txt
pre-commit install
make ingest              # indexer documents/
make query q="Ta question"
```

## Architecture

```
Question → retrieve → grade → [rewrite → retrieve] → generate → Reponse
```

- **retrieve** : recherche semantique dans PGVector
- **grade** : LLM juge la pertinence des documents
- **rewrite** : reformulation de la question si hors-sujet
- **generate** : contexte + question → reponse avec citations

## Commandes

| Commande | Description |
|----------|-------------|
| `make up` | Docker compose up |
| `make ingest` | Indexer documents/ |
| `make query q=...` | Poser une question |
| `make serve` | Lancer le serveur FastAPI |
| `make test` | Lancer les tests |
| `make lint` | Ruff check |
| `make typecheck` | Mypy check |

## API

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Que contient le document ?"}'

curl http://localhost:8000/health
```

## CI/CD

- **CI** : ruff → mypy → pytest (cov 80%) → bandit → safety → Docker build
- **CD** : push main → build image → push GHCR → GitHub Release

## Stack

- Python 3.11 / LangChain / LangGraph / OpenRouter
- PostgreSQL + pgvector (Docker)
- sentence-transformers (embeddings locaux)
- FastAPI / Uvicorn
