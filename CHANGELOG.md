# Changelog

Toutes les modifications notables de ce projet sont documentees ici.

Format base sur [Keep a Changelog](https://keepachangelog.com/),
et ce projet adhere au [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-05-31

### Ajoute
- 83 nouveaux tests (101 total), couverture passee de 55% a 98.51%
- Tests pour `app/utils/retry.py` (retry + async_retry decorators)
- Tests pour `app/agent/nodes/grade.py` (grade node avec LLM judge)
- Tests pour `app/agent/nodes/retrieve.py` (retrieve node avec mocks)
- Tests pour `app/ingest/pipeline.py` (pipeline d'ingestion complet)
- Tests pour `app/ingest/loader.py` (_load_pdf, _load_text)
- Tests pour `app/embeddings/provider.py` (caching, batch, dimension)
- Tests pour `app/vectorstore/store.py` (CRUD, session, initialization)
- Tests pour `app/agent/graph.py` (creation et execution du graphe)
- Tests pour `app/utils/hash.py` (sha256_hash, sha256_file)
- Tests etendus pour `app/agent/router.py` (route_after_generate)
- Tests etendus pour `app/api/routes.py` (5 nouveaux cas)
- Seuil de couverture remonte a 80%

### Corrige
- Docker build : `COPY /root/.cache` supprime (n'existe pas avec --no-cache-dir)

## [0.1.1] - 2026-05-31

### Corrige
- Synchronisation automatique de `OPENROUTER_API_KEY` dans `os.environ`
  pour compatibilite avec `langchain_openrouter.ChatOpenRouter`
- Erreur `ValueError: I/O operation on closed file` dans le loader PDF
- Corrections lint (ruff), typage (mypy) et securite (bandit) pour
  passer la pre-commit pipeline
- Passage de `ignore_missing_imports` a des stubs types explicitement
  declares (`types-cachetools`, `pydantic-settings`)

## [0.1.0] - 2026-05-31

### Ajoute
- Initial release de l'agent RAG Kemi
- Ingestion de documents (PDF, Markdown, TXT) avec chunking et embeddings locaux
- Vector store PGVector (PostgreSQL + pgvector)
- Agent RAG agentique avec LangGraph :
  - Retrieval semantique
  - Relevance grading avec LLM judge
  - Query rewriting automatique
  - Generation avec citations
  - Boucle de correction (max 3 iterations)
- Serveur FastAPI (endpoints /query, /ingest, /health)
- CLI complete (ingest, query, stats)
- Docker Compose (PostgreSQL + app)
- CI/CD : ruff, mypy, pytest, bandit, safety, build Docker
- Pre-commit hooks (ruff, mypy, bandit, trailing-whitespace, end-of-file-fixer, check-yaml, check-added-large-files, check-merge-conflict, detect-private-key)
