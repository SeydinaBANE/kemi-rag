from __future__ import annotations

from unittest.mock import MagicMock, patch

from langgraph.graph.state import CompiledStateGraph

from app.agent.graph import create_rag_agent, run_agent


class TestCreateRagAgent:
    def test_create_rag_agent_returns_compiled_graph(self) -> None:
        agent = create_rag_agent()
        assert isinstance(agent, CompiledStateGraph)

    def test_rag_agent_has_expected_nodes(self) -> None:
        agent = create_rag_agent()
        nodes = agent.nodes
        assert "retrieve" in nodes
        assert "grade" in nodes
        assert "rewrite" in nodes
        assert "generate" in nodes


class TestRunAgent:
    def test_run_agent_invokes_graph(self) -> None:
        with patch("app.agent.graph.create_rag_agent") as mock_create:
            mock_app = MagicMock()
            mock_create.return_value = mock_app
            mock_app.invoke.return_value = {
                "answer": "Python is a language.",
                "sources": [],
                "iterations": 1,
                "context": [],
                "documents": [],
                "messages": [],
                "trace": [],
                "question": "What is Python?",
                "rewritten_question": "",
            }

            result = run_agent("What is Python?")

            assert result["answer"] == "Python is a language."
            assert result["iterations"] == 1

    def test_run_agent_passes_initial_state(self) -> None:
        with patch("app.agent.graph.create_rag_agent") as mock_create:
            mock_app = MagicMock()
            mock_create.return_value = mock_app
            mock_app.invoke.return_value = {"answer": "42"}

            run_agent("Ultimate Question?")

            call_kwargs = mock_app.invoke.call_args[0][0]
            assert call_kwargs["question"] == "Ultimate Question?"
            assert call_kwargs["iterations"] == 0
            assert call_kwargs["context"] == []
