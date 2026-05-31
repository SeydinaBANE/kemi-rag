from __future__ import annotations

from app.agent.state import GraphState
from app.embeddings.provider import EmbeddingProvider
from app.vectorstore.store import VectorStore


def retrieve_node(
    state: GraphState,
    vector_store: VectorStore | None = None,
    embedding_provider: EmbeddingProvider | None = None,
) -> dict:
    vector_store = vector_store or VectorStore()
    embedding_provider = embedding_provider or EmbeddingProvider()

    query = state.get("rewritten_question") or state["question"]
    query_embedding = embedding_provider.embed(query)
    top_k = 5

    results = vector_store.similarity_search(query_embedding, top_k=top_k)

    contexts: list[str] = []
    sources: list[dict] = []
    documents: list[str] = []

    for content, doc_name, score, chunk_idx in results:
        contexts.append(content)
        documents.append(doc_name)
        sources.append({
            "document": doc_name,
            "chunk_index": chunk_idx,
            "content": content[:200],
            "score": score,
        })

    return {
        "context": contexts,
        "sources": sources,
        "documents": documents,
    }
