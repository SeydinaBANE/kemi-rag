# Changelog

Toutes les modifications notables de ce projet sont documentees ici.

Format base sur [Keep a Changelog](https://keepachangelog.com/),
et ce projet adhere au [Semantic Versioning](https://semver.org/).

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
- Pre-commit hooks
