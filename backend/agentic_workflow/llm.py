"""LLM Generation node for LangGraph.

This module defines a node that takes a composed prompt from the workflow state
and uses LangChain + DeepSeek to generate a response.

The node is configurable (temperature, max tokens) and handles common error cases
(missing API key, network issues, etc).
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# Load .env from backend directory
backend_dir = Path(__file__).resolve().parent.parent
env_path = backend_dir / '.env'
load_dotenv(env_path)

# Load API key from environment (fail fast if missing)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError(
        f"DEEPSEEK_API_KEY not found in environment or {env_path}. "
        "Get one from https://platform.deepseek.com"
    )

# Configure model (shared instance)
_model = ChatOpenAI(
    model="deepseek-chat",
    temperature=0.7,
    max_tokens=300,
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1",
    streaming=True,
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
    # Add retries and timeout
    max_retries=3,
    request_timeout=30
)

def generate_response(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node: enrich *state* with LLM `response`.
    
    Expected input state keys
    ------------------------
    prompt: str    – fully composed prompt from composer
    
    Added output state keys
    ----------------------
    response: str  – LLM generation result
    """
    prompt: Optional[str] = state.get("prompt")
    if not prompt:
        raise ValueError("State must contain 'prompt'")
        
    # Split into system/human messages
    parts = prompt.split("\n\nContext:")
    system_part = parts[0].strip()
    context_part = parts[1].strip() if len(parts) > 1 else ""
    
    messages = [
        SystemMessage(content=system_part),
        HumanMessage(content=f"Context and question:\n{context_part}")
    ]
    
    # Generate (this calls the DeepSeek API)
    response = _model.invoke(messages)
    
    # Add to state
    state["response"] = response.content
    return state