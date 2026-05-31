# Changelog

Toutes les modifications notables de ce projet sont documentees ici.

Format base sur [Keep a Changelog](https://keepachangelog.com/),
et ce projet adhere au [Semantic Versioning](https://semver.org/).

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
