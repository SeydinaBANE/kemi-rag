from __future__ import annotations

from unittest.mock import patch

from app.agent.nodes.generate import generate_node
from app.agent.nodes.rewrite import rewrite_node
from app.agent.state import GraphState


class TestGraphState:
    def test_state_defaults(self) -> None:
        state: GraphState = {
            "question": "What is kemi?",
            "rewritten_question": "",
            "context": [],
            "documents": [],
            "sources": [],
            "answer": "",
            "iterations": 0,
            "messages": [],
            "trace": [],
        }
        assert state["question"] == "What is kemi?"
        assert state["iterations"] == 0

    def test_state_iteration_increment(self) -> None:
        state: GraphState = {
            "question": "test",
            "rewritten_question": "",
            "context": [],
            "documents": [],
            "sources": [],
            "answer": "",
            "iterations": 2,
            "messages": [],
            "trace": [],
        }
        assert state["iterations"] == 2


class TestGenerateNode:
    def test_generate_no_context(self) -> None:
        state: GraphState = {
            "question": "What is Python?",
            "rewritten_question": "",
            "context": [],
            "documents": [],
            "sources": [],
            "answer": "",
            "iterations": 0,
            "messages": [],
            "trace": [],
        }

        with patch("app.agent.nodes.generate.ChatOpenRouter") as mock_llm:
            mock_instance = mock_llm.return_value
            mock_chain = mock_instance.__or__.return_value
            mock_response = mock_chain.invoke.return_value
            mock_response.content = "Python is a programming language."

            result = generate_node(state)

            assert "answer" in result
            assert result["answer"] == "Python is a programming language."

    def test_generate_with_context(self) -> None:
        state: GraphState = {
            "question": "What is Python?",
            "rewritten_question": "",
            "context": ["Python is a high-level programming language created by Guido van Rossum."],
            "documents": ["doc1.md"],
            "sources": [],
            "answer": "",
            "iterations": 0,
            "messages": [],
            "trace": [],
        }

        with patch("app.agent.nodes.generate.ChatOpenRouter") as mock_llm:
            mock_instance = mock_llm.return_value
            mock_chain = mock_instance.__or__.return_value
            mock_response = mock_chain.invoke.return_value
            mock_response.content = "Python is a high-level programming language."

            result = generate_node(state)

            assert "answer" in result
            assert len(result["answer"]) > 0


class TestRewriteNode:
    def test_rewrite_question(self) -> None:
        state: GraphState = {
            "question": "What is it?",
            "rewritten_question": "",
            "context": [],
            "documents": [],
            "sources": [],
            "answer": "",
            "iterations": 0,
            "messages": [],
            "trace": [],
        }

        with patch("app.agent.nodes.rewrite.ChatOpenRouter") as mock_llm:
            mock_instance = mock_llm.return_value
            mock_chain = mock_instance.__or__.return_value
            mock_response = mock_chain.invoke.return_value
            mock_response.content = "What is the RAG agent Kemi?"

            result = rewrite_node(state)

            assert "rewritten_question" in result
            assert len(result["rewritten_question"]) > 0


class TestRouter:
    def test_route_with_context(self) -> None:
        from app.agent.router import route_after_retrieval

        state: GraphState = {
            "question": "test",
            "rewritten_question": "",
            "context": ["some context"],
            "documents": [],
            "sources": [],
            "answer": "",
            "iterations": 0,
            "messages": [],
            "trace": [],
        }

        assert route_after_retrieval(state) == "generate"

    def test_route_without_context(self) -> None:
        from app.agent.router import route_after_retrieval

        state: GraphState = {
            "question": "test",
            "rewritten_question": "",
            "context": [],
            "documents": [],
            "sources": [],
            "answer": "",
            "iterations": 0,
            "messages": [],
            "trace": [],
        }

        assert route_after_retrieval(state) == "rewrite"

    def test_route_max_iterations(self) -> None:
        from app.agent.router import route_after_retrieval

        state: GraphState = {
            "question": "test",
            "rewritten_question": "",
            "context": [],
            "documents": [],
            "sources": [],
            "answer": "",
            "iterations": 3,
            "messages": [],
            "trace": [],
        }

        assert route_after_retrieval(state) == "max_iterations"
