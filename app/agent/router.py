from __future__ import annotations

from typing import Literal

from app.agent.state import GraphState


def route_after_retrieval(state: GraphState) -> Literal["generate", "rewrite", "max_iterations"]:
    contexts = state.get("context", [])
    iterations = state.get("iterations", 0)

    if iterations >= 3:
        return "max_iterations"

    if contexts:
        return "generate"
    else:
        return "rewrite"


def route_after_generate(state: GraphState) -> Literal["retrieve", "end"]:
    contexts = state.get("context", [])
    if not contexts and state.get("iterations", 0) < 3:
        return "retrieve"
    return "end"
