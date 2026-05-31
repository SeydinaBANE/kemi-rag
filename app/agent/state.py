from __future__ import annotations

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    question: str
    rewritten_question: str
    context: list[str]
    documents: list[str]
    sources: list[dict]
    answer: str
    iterations: int
    messages: Annotated[list, add_messages]
    trace: list[dict]
