# Agent RAG Kemi

## Stack
- Python 3.11+, LangChain, LangGraph, OpenRouter
- PostgreSQL + pgvector (Docker)
- sentence-transformers (embeddings locaux)
- Ruff (lint), mypy (typecheck), pytest (tests)
- Pre-commit hooks, GitHub Actions (CI/CD)

## Commandes (Makefile)
- `make up` -> docker compose up -d
- `make lint` -> ruff check app/ tests/ cli.py
- `make typecheck` -> mypy app/ tests/ cli.py
- `make test` -> pytest
- `make coverage` -> pytest --cov --cov-fail-under=50
- `make security` -> bandit + safety
- `make ingest` -> python cli.py ingest --dir documents/
- `make query q="question"` -> interroger l'agent
- `make serve` -> uvicorn app.api.server:app --reload --host 0.0.0.0 --port 8000
- `make precommit` -> pre-commit run --all-files
- `make clean` -> nettoyer artefacts (cache, pyc, htmlcov)

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
- La cle est automatiquement synchronisee dans os.environ au demarrage
  (necessaire car langchain_openrouter.ChatOpenRouter lit la variable
  d'environnement directement)
- Le max d'iterations agentiques est 3 (configurable dans .env)
- L'ingestion est idempotente (hash SHA256)
- La couverture de tests doit rester au-dessus de 50% (objectif: 80% -- voir TODO Phase 12b)
- Les stubs de types sont installes dans pre-commit via additional_dependencies
  (pydantic-settings, types-cachetools, types-requests)
