from __future__ import annotations

"""Retriever node for LangGraph.

This module defines a simple function that will be used as a LangGraph node.
The node takes the current workflow *state* (a Python dict), expects a key
``query`` containing the learner question / current topic, and injects a
``context`` key containing the top-k retrieved passages from our FAISS
knowledge base.

The function is intentionally lightweight; any heavy lifting (embeddings,
vector search) happens in ``knowledge_base``.
"""

from typing import Dict, Any, List, Optional

from . import knowledge_base

# Number of passages we feed into the prompt. Easy to tune.
_TOP_K = 3


def retrieve_context(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node: enrich *state* with `context` retrieved via FAISS.

    Expected input state keys
    ------------------------
    query: str   – learner question / topic

    Added output state keys
    ----------------------
    context: List[str] – list of retrieved passages
    """
    query: Optional[str] = state.get("query")
    if not query:
        raise ValueError("Retriever node requires 'query' in state")

    # Call vector store
    results = knowledge_base.similarity_search(query, top_k=_TOP_K)
    passages: List[str] = [doc for doc, _score in results]

    # Mutate + return new state copy (LangGraph encourages immutability)
    new_state = {**state, "context": passages}
    return new_state
