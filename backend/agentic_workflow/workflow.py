from __future__ import annotations

"""Minimal LangGraph workflow skeleton.

This graph currently has a single node (Retriever) that enriches the
incoming state with contextual passages.  We'll extend it later with nodes
for PromptComposition, LLM generation, performance analysis, etc.
"""

from typing import Dict, Any

from langgraph.graph import StateGraph, END

from .retriever import retrieve_context
from .prompt_composer import compose_prompt
from .llm import generate_response
from .performance_analyzer import analyze_performance

# Alias for readability: a workflow state is just a dict for now.
State = Dict[str, Any]


def build_graph() -> StateGraph[State]:
    """Create and return a StateGraph with Retriever only."""
    sg: StateGraph[State] = StateGraph(State)

    # Register nodes
    sg.add_node("retriever", retrieve_context)
    sg.add_node("composer", compose_prompt)
    sg.add_node("llm", generate_response)
    sg.add_node("analyzer", analyze_performance)

    # Wire: Start → retriever → composer → llm → analyzer → End
    sg.set_entry_point("retriever")
    sg.add_edge("retriever", "composer")
    sg.add_edge("composer", "llm")
    sg.add_edge("llm", "analyzer")
    sg.add_edge("analyzer", END)

    return sg


def run_simple(query: str, top_k: int = 3) -> State:
    """Utility to run the minimal graph with a raw query."""
    graph = build_graph().compile()
    initial_state: State = {"query": query, "top_k": top_k}
    final_state = graph.invoke(initial_state)
    return final_state


if __name__ == "__main__":
    # Quick manual test
    test_query = "भारत की राजधानी"
    result = run_simple(test_query)
    print("Context Passages:\n", "\n---\n".join(result.get("context", [])))
