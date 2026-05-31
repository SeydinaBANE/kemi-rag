from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.agent.nodes.grade import grade_node
from app.agent.state import GraphState
from app.domain.schemas import GradingResult


def _make_state(question: str, contexts: list[str] | None = None) -> GraphState:
    return {
        "question": question,
        "rewritten_question": "",
        "context": contexts or [],
        "documents": [],
        "sources": [],
        "answer": "",
        "iterations": 1,
        "messages": [],
        "trace": [],
    }


class TestGradeNode:
    def test_grade_node_no_context(self) -> None:
        state = _make_state("What is Python?")
        result = grade_node(state)
        assert result == {"context": []}

    def test_grade_node_all_relevant(self) -> None:
        state = _make_state("What is Python?", ["Python is a language."])

        with patch("app.agent.nodes.grade.ChatOpenRouter") as mock_llm:
            mock_instance = mock_llm.return_value
            mock_structured = MagicMock(return_value=GradingResult(binary_score="yes"))
            mock_instance.with_structured_output.return_value = mock_structured

            result = grade_node(state)

            assert "context" in result
            assert result["context"] == ["Python is a language."]
            mock_structured.assert_called_once()

    def test_grade_node_none_relevant(self) -> None:
        state = _make_state("What is Python?", ["Java is a language."])

        with patch("app.agent.nodes.grade.ChatOpenRouter") as mock_llm:
            mock_instance = mock_llm.return_value
            mock_structured = MagicMock(return_value=GradingResult(binary_score="no"))
            mock_instance.with_structured_output.return_value = mock_structured

            result = grade_node(state)

            assert result["context"] == []

    def test_grade_node_mixed_relevance(self) -> None:
        state = _make_state(
            "What is Python?",
            ["Python is a language.", "Java is a language.", "Python is interpreted."],
        )

        with patch("app.agent.nodes.grade.ChatOpenRouter") as mock_llm:
            mock_instance = mock_llm.return_value
            scores = iter(["yes", "no", "yes"])

            def side_effect(*args: object, **kwargs: object) -> GradingResult:
                return GradingResult(binary_score=next(scores))

            mock_structured = MagicMock()
            mock_structured.side_effect = side_effect
            mock_instance.with_structured_output.return_value = mock_structured

            result = grade_node(state)

            assert result["context"] == ["Python is a language.", "Python is interpreted."]

    def test_grade_node_dict_result(self) -> None:
        state = _make_state("What is Python?", ["Python is a language."])

        with patch("app.agent.nodes.grade.ChatOpenRouter") as mock_llm:
            mock_instance = mock_llm.return_value
            mock_structured = MagicMock(return_value={"binary_score": "yes"})
            mock_instance.with_structured_output.return_value = mock_structured

            result = grade_node(state)

            assert result["context"] == ["Python is a language."]

    def test_grade_node_unknown_result_type(self) -> None:
        state = _make_state("What is Python?", ["Python is a language."])

        with patch("app.agent.nodes.grade.ChatOpenRouter") as mock_llm:
            mock_instance = mock_llm.return_value
            mock_structured = MagicMock(return_value="unexpected")
            mock_instance.with_structured_output.return_value = mock_structured

            result = grade_node(state)

            assert result["context"] == []
