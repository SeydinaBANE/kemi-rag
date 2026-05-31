from __future__ import annotations

from typing import Annotated, Any, TypedDict

from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    question: str
    rewritten_question: str
    context: list[str]
    documents: list[str]
    sources: list[dict[str, Any]]
    answer: str
    iterations: int
    messages: Annotated[list[Any], add_messages]
    trace: list[dict[str, Any]]
