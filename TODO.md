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

## Phase 12b : Tests & Couverture

- [ ] Tests pour `app/agent/nodes/grade.py` (grade node)
- [ ] Tests pour `app/agent/nodes/retrieve.py` (retrieve node)
- [ ] Tests pour `app/ingest/pipeline.py` (pipeline complet)
- [ ] Tests pour `app/vectorstore/store.py` (vector store CRUD)
- [ ] Tests pour `app/embeddings/provider.py` (embeddings)
- [ ] Tests pour `app/agent/graph.py` (creation et execution du graphe)
- [ ] Tests pour `app/utils/retry.py` (retry decorator)
- [ ] Objectif : couverture >= 80%

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
