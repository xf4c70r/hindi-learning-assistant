"""Performance Analyzer node for LangGraph.

This node compares the learner's answer with the expected answer and updates
workflow state with a simple correctness score.  In later iterations we can
extend this with partial credit, difficulty adjustment, and spaced repetition
scheduling.
"""
from __future__ import annotations

from typing import Dict, Any


def analyze_performance(state: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate learner answer and update state.

    Expected keys in *state* before call:
      - user_answer: str  (learner's input)
      - expected_answer: str  (ground-truth from LLM / dataset)

    Keys added / updated:
      - is_correct: bool
      - score: int  (1 for correct, 0 for incorrect)
    """
    user_answer = (state.get("user_answer") or "").strip().lower()
    expected = (state.get("expected_answer") or "").strip().lower()

    is_correct = user_answer == expected if expected else False

    state["is_correct"] = is_correct
    state["score"] = 1 if is_correct else 0

    # TODO: append history list, tracking attempts, etc.
    return state