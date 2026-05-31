from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_openrouter import ChatOpenRouter

from app.agent.state import GraphState
from app.config import settings

REWRITE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a query rewriter for a RAG system. "
            "Given the original user question, rewrite it to be more specific and search-friendly. "
            "Fix vague wording, add missing context, and make it concise. "
            "Return only the rewritten question, nothing else.",
        ),
        ("human", "Original question: {question}\n\nRewritten question:"),
    ]
)


def rewrite_node(state: GraphState) -> dict[str, str]:
    question = state["question"]

    llm = ChatOpenRouter(
        model=settings.llm_model,
        temperature=0,
        max_tokens=256,
        max_retries=2,
    )
    chain = REWRITE_PROMPT | llm
    response = chain.invoke({"question": question})

    rewritten = response.content.strip()
    return {"rewritten_question": rewritten}
