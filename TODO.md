# TODO — Agent RAG Kemi

> Toutes les phases d'infrastructure et de developpement initial sont terminees.
> Ce fichier sert desormais de roadmap pour les ameliorations futures.

## Phase 11 : Observabilite

- [ ] Tracing LangSmith ou OpenTelemetry
- [ ] Metriques Prometheus (/metrics endpoint)
- [ ] Alerting sur les erreurs LLM / ingestion

## Phase 12 : Performance & Robustesse

- [ ] Indexation incrementale (watcher de fichiers)
- [ ] Cache de reponse identique (question deja posee)
- [ ] Timeout configurable par etape du graphe
- [ ] Fallback LLM si OpenRouter est indisponible

## Phase 12b : Tests & Couverture ✅

- [x] Tests pour `app/agent/nodes/grade.py` (grade node)
- [x] Tests pour `app/agent/nodes/retrieve.py` (retrieve node)
- [x] Tests pour `app/ingest/pipeline.py` (pipeline complet)
- [x] Tests pour `app/vectorstore/store.py` (vector store CRUD)
- [x] Tests pour `app/embeddings/provider.py` (embeddings)
- [x] Tests pour `app/agent/graph.py` (creation et execution du graphe)
- [x] Tests pour `app/utils/retry.py` (retry decorator)
- [x] Tests pour `app/ingest/loader.py` (_load_pdf, _load_text, load_document)
- [x] Tests pour `app/utils/hash.py` (sha256_hash, sha256_file)
- [x] Tests etendus pour `app/agent/router.py` (route_after_generate)
- [x] Tests etendus pour `app/api/routes.py` (health, query, ingest)
- [x] **Objectif : couverture >= 80%** → atteint **98.51%** (101 tests)

## Phase 13 : UX & Features

- [ ] Streaming de la reponse (SSE)
- [ ] Mode conversationnel (historique de session)
- [ ] Support de formats supplementaires (DOCX, HTML, images)
- [ ] Dashboard (stats, documents indexes, etat du vector store)

## Phase 14 : Securite & Conformite

- [ ] Rate limiting sur l'API
- [ ] Auth (API key) pour les endpoints sensibles
- [ ] Scan de vulnerabilite des dependances en CI (deja: safety)

---

**Legende :**
- `[ ]` = a faire
- `[x]` = fait
- Phases 1-10 : terminees (voire l'historique git pour le detail)
