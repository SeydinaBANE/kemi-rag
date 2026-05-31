from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_openrouter import ChatOpenRouter

from app.agent.state import GraphState
from app.config import settings

GENERATE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant for question-answering tasks.\n"
            "Use the following pieces of retrieved context to answer the question.\n"
            "If you don't know the answer, say that you don't know.\n"
            "Cite your sources by mentioning the document name for each piece of information.\n"
            "Keep the answer concise and well-structured.\n\n"
            "Context:\n{context}",
        ),
        ("human", "Question: {question}"),
    ]
)


def generate_node(state: GraphState) -> dict[str, str]:
    question = state["question"]
    context = state.get("context", [])

    context_text = (
        "\n\n".join(f"[{i + 1}] {doc}" for i, doc in enumerate(context))
        if context
        else "No relevant context found."
    )

    llm = ChatOpenRouter(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        max_retries=2,
    )
    chain = GENERATE_PROMPT | llm
    response = chain.invoke({"question": question, "context": context_text})

    return {"answer": response.content.strip()}
