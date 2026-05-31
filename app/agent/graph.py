from __future__ import annotations

from typing import Any

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agent.nodes.generate import generate_node
from app.agent.nodes.grade import grade_node
from app.agent.nodes.retrieve import retrieve_node
from app.agent.nodes.rewrite import rewrite_node
from app.agent.router import route_after_generate, route_after_retrieval
from app.agent.state import GraphState


def create_rag_agent() -> CompiledStateGraph[GraphState, Any, Any, Any]:
    workflow = StateGraph(GraphState)

    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("grade", grade_node)
    workflow.add_node("rewrite", rewrite_node)
    workflow.add_node("generate", generate_node)

    workflow.set_entry_point("retrieve")

    workflow.add_edge("retrieve", "grade")

    workflow.add_conditional_edges(
        "grade",
        route_after_retrieval,
        {
            "generate": "generate",
            "rewrite": "rewrite",
            "max_iterations": "generate",
        },
    )

    workflow.add_edge("rewrite", "retrieve")

    workflow.add_conditional_edges(
        "generate",
        route_after_generate,
        {
            "retrieve": "retrieve",
            "end": END,
        },
    )

    return workflow.compile()


def run_agent(question: str) -> dict[str, Any]:
    app = create_rag_agent()
    result = app.invoke(
        {
            "question": question,
            "rewritten_question": "",
            "context": [],
            "documents": [],
            "sources": [],
            "answer": "",
            "iterations": 0,
            "messages": [],
            "trace": [],
        }
    )
    return result  # type: ignore[no-any-return]
