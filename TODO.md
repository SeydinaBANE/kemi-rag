# TODO — Agent RAG Kemi

## Phase 1 : Infrastructure (DevOps)

- [x] Creer `.editorconfig`
- [x] Creer `.gitignore`
- [x] Creer `.dockerignore`
- [x] Creer `.env.example`
- [x] Creer `VERSION`
- [x] Creer `CHANGELOG.md`
- [x] Creer `Makefile`
- [x] Creer `.pre-commit-config.yaml`
- [x] Creer `pyproject.toml`
- [x] Creer `requirements.txt`
- [x] Creer `Dockerfile`
- [x] Creer `docker-compose.yml`
- [x] Creer `.github/dependabot.yml`
- [x] Creer `.github/workflows/ci.yml`
- [x] Creer `.github/workflows/cd.yml`

## Phase 2 : Fondations du code

- [x] `app/__init__.py`
- [x] `app/config.py`
- [x] `app/logging.py`
- [x] `app/models.py`
- [x] `app/domain/__init__.py`
- [x] `app/domain/schemas.py`
- [x] `app/utils/__init__.py`
- [x] `app/utils/retry.py`
- [x] `app/utils/hash.py`

## Phase 3 : Embeddings

- [x] `app/embeddings/__init__.py`
- [x] `app/embeddings/provider.py`

## Phase 4 : Ingestion

- [x] `app/ingest/__init__.py`
- [x] `app/ingest/loader.py`
- [x] `app/ingest/chunker.py`
- [x] `app/ingest/pipeline.py`

## Phase 5 : Vector Store

- [x] `app/vectorstore/__init__.py`
- [x] `app/vectorstore/store.py`

## Phase 6 : Agent RAG (LangGraph)

- [x] `app/agent/__init__.py`
- [x] `app/agent/state.py`
- [x] `app/agent/nodes/__init__.py`
- [x] `app/agent/nodes/retrieve.py`
- [x] `app/agent/nodes/grade.py`
- [x] `app/agent/nodes/rewrite.py`
- [x] `app/agent/nodes/generate.py`
- [x] `app/agent/router.py`
- [x] `app/agent/graph.py`

## Phase 7 : API

- [x] `app/api/__init__.py`
- [x] `app/api/server.py`
- [x] `app/api/routes.py`

## Phase 8 : CLI

- [x] `cli.py`

## Phase 9 : Tests

- [x] `tests/__init__.py`
- [x] `tests/conftest.py`
- [x] `tests/test_ingest.py`
- [x] `tests/test_agent.py`
- [x] `tests/test_api.py`

## Phase 10 : Documentation

- [x] `README.md`
- [x] `AGENTS.md`

---

**Legende :**
- `[ ]` = a faire
- `[x]` = fait
