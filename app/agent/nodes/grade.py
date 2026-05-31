from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_openrouter import ChatOpenRouter

from app.agent.state import GraphState
from app.config import settings
from app.domain.schemas import GradingResult

GRADE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a grader assessing relevance of a retrieved document to a user question.\n"
            "If the document contains keyword(s) or semantic meaning related to the question, "
            "grade it as relevant.\n"
            "Give a binary score 'yes' or 'no' to indicate whether the document is relevant "
            "to the question.",
        ),
        (
            "human",
            "User question: {question}\n\n"
            "Retrieved document: {document}\n\n"
            "Is this document relevant?",
        ),
    ]
)


def grade_node(state: GraphState) -> dict[str, list[str]]:
    question = state["question"]
    contexts = state.get("context", [])

    if not contexts:
        return {"context": []}

    llm = ChatOpenRouter(
        model=settings.llm_model,
        temperature=0,
        max_tokens=128,
        max_retries=2,
    )
    grader = GRADE_PROMPT | llm.with_structured_output(GradingResult)

    relevant_contexts: list[str] = []
    for doc in contexts:
        result = grader.invoke({"question": question, "document": doc})
        if isinstance(result, GradingResult):
            binary_score = result.binary_score
        elif isinstance(result, dict):
            binary_score = result.get("binary_score", "no")
        else:
            binary_score = "no"
        if binary_score == "yes":
            relevant_contexts.append(doc)

    return {"context": relevant_contexts}
