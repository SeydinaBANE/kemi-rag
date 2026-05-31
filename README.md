# Kemi — Agent RAG

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/LangGraph-latest-purple?logo=langchain" alt="LangGraph">
  <img src="https://img.shields.io/badge/OpenRouter-LLM-orange" alt="OpenRouter">
  <img src="https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?logo=postgresql" alt="pgvector">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <br>
  <a href="https://github.com/SeydinaBANE/kemi-rag/actions/workflows/ci.yml"><img src="https://github.com/SeydinaBANE/kemi-rag/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/SeydinaBANE/kemi-rag/actions/workflows/cd.yml"><img src="https://github.com/SeydinaBANE/kemi-rag/actions/workflows/cd.yml/badge.svg" alt="CD"></a>
  <img src="https://img.shields.io/badge/version-0.1.1-blue" alt="Version">
</p>

Agent RAG agentique avec LangGraph, OpenRouter, et pgvector.

## Quick Start

```bash
cp .env.example .env          # editer OPENROUTER_API_KEY
make up                       # PostgreSQL + pgvector
pip install -r requirements.txt
pre-commit install
make ingest                   # indexer documents/
make query q="Ta question"
```

## Architecture

```
Question → retrieve → grade → [rewrite → retrieve] → generate → Reponse
```

- **retrieve** : recherche semantique dans PGVector (top-5 chunks)
- **grade** : LLM juge la pertinence des documents recuperes
- **rewrite** : reformulation de la question si tous les documents sont hors-sujet
- **generate** : contexte + question → reponse avec citations et sources

L'ingestion est idempotente (hash SHA256) — un document deja indexe est ignore.

## Commandes

| Commande                | Description                        |
|-------------------------|------------------------------------|
| `make up`               | Docker compose up -d               |
| `make down`             | Docker compose down                |
| `make serve`            | Lancer le serveur FastAPI en dev   |
| `make ingest`           | Ingerer les documents              |
| `make query q=...`      | Poser une question                 |
| `make lint`             | Ruff check                         |
| `make typecheck`        | Mypy check                         |
| `make test`             | Pytest                             |
| `make coverage`         | Pytest avec couverture (≥80%)      |
| `make security`         | Bandit + Safety                    |
| `make precommit`        | Pre-commit run --all-files         |
| `make docker-build`     | Docker compose build               |
| `make clean`            | Nettoyer les artefacts             |

## Configuration

Toutes les variables sont dans `.env` :

| Variable                  | Defaut                                      | Description                |
|---------------------------|---------------------------------------------|----------------------------|
| `OPENROUTER_API_KEY`      | —                                           | Cle API OpenRouter         |
| `DATABASE_URL`            | `postgresql://kemi:kemi@localhost:5432/kemi`| URL PostgreSQL             |
| `LLM_MODEL`               | `openai/gpt-4o-mini`                        | Modele LLM                 |
| `EMBEDDING_MODEL`         | `sentence-transformers/all-MiniLM-L6-v2`    | Modele d'embeddings local  |
| `MAX_ITERATIONS`          | `3`                                         | Maximum d'iterations agent |
| `RETRIEVAL_TOP_K`         | `5`                                         | Nombre de chunks retrieves |
| `CHUNK_SIZE`              | `512`                                       | Taille des chunks          |
| `API_PORT`                | `8000`                                      | Port du serveur FastAPI    |

> **Note** : `OPENROUTER_API_KEY` est automatiquement synchronisee dans les variables
> d'environnement pour `langchain_openrouter` au chargement de la configuration.

## API

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Que contient le document ?"}'

curl http://localhost:8000/health

curl -X POST http://localhost:8000/ingest \
  -F "file=@document.pdf"
```

## Tests

```bash
make test       # pytest
make coverage   # pytest --cov --cov-fail-under=80
make security   # bandit + safety
```

## Stack

- Python 3.11 / LangChain / LangGraph / OpenRouter
- PostgreSQL + pgvector (Docker)
- sentence-transformers (embeddings locaux)
- FastAPI / Uvicorn
- Ruff / Mypy / Bandit / Safety
- Pre-commit hooks / GitHub Actions (CI/CD)
