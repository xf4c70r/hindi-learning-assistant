"""Prompt Composer node for LangGraph.

This module defines a node that takes the current workflow state (containing
a query and retrieved context passages) and composes a well-structured prompt
for the LLM to generate a response.

The prompt follows best practices:
1. Clear system instructions
2. Explicit context boundary
3. Numbered passages for reference
4. Clear question/task marker
"""

from typing import Dict, Any, List, Optional

# Template for our system instructions
SYSTEM_TEMPLATE = """You are a Hindi language tutor helping a student learn.
Use the provided context passages to answer the student's question.
If you can't answer from the context alone, say so.
Always respond in a mix of Hindi and English to help the student learn."""

def compose_prompt(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node: enrich *state* with a composed `prompt`.
    
    Expected input state keys
    ------------------------
    query: str      – learner question / topic
    context: List[str] – relevant passages from FAISS
    
    Added output state keys
    ----------------------
    prompt: str     – fully composed prompt for LLM
    """
    query: Optional[str] = state.get("query")
    if not query:
        raise ValueError("State must contain 'query'")
        
    context: List[str] = state.get("context", [])
    
    # Build prompt components
    context_str = "\n".join(
        f"{i+1}. {p}" for i, p in enumerate(context)
    ) if context else "No relevant context found."
    
    prompt = f"""{SYSTEM_TEMPLATE}

Context:
{context_str}

Question: {query}"""
    
    # Add to state
    state["prompt"] = prompt
    return state