# Agent RAG Kemi

## Stack
- Python 3.11+, LangChain, LangGraph, OpenRouter
- PostgreSQL + pgvector (Docker)
- sentence-transformers (embeddings locaux)
- Ruff (lint), mypy (typecheck), pytest (tests)
- Pre-commit hooks, GitHub Actions (CI/CD)

## Commandes (Makefile)
- `make up` -> docker compose up -d
- `make lint` -> ruff check
- `make typecheck` -> mypy
- `make test` -> pytest
- `make coverage` -> pytest --cov --cov-fail-under=80
- `make security` -> bandit + safety
- `make ingest` -> python cli.py ingest --dir documents/
- `make query q="question"` -> interroger l'agent
- `make serve` -> uvicorn dev server
- `make precommit` -> pre-commit run --all-files

## Architecture
- `app/ingest/` : load -> chunk -> embed -> store (idempotent via SHA256)
- `app/vectorstore/` : PGVector (insert, similarity_search)
- `app/agent/` : LangGraph (retrieve -> grade -> rewrite -> generate)
- `app/api/` : FastAPI server (query, ingest, health)
- `cli.py` : point d'entree CLI

## Regles
- Toujours lancer `make lint` et `make typecheck` avant commit
- Les embeddings sont locaux (sentence-transformers) - pas de cle API necessaire
- Le LLM passe par OpenRouter - configurer OPENROUTER_API_KEY dans .env
- Le max d'iterations agentiques est 3 (configurable)
- L'ingestion est idempotente (hash SHA256)
- La couverture de tests doit rester au-dessus de 80%
