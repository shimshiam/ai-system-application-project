"""Shared LLM client factory.

Checks for GROQ_API_KEY first, then OPENAI_API_KEY.
Returns an OpenAI-compatible client and the model name to use.
"""

import json
import os
from typing import Any, Dict, List, Optional


# Groq base URL for OpenAI-compatible API
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
DEFAULT_OPENAI_MODEL = "gpt-4o"


def get_llm_client():
    """Return (client, model_name) using Groq or OpenAI, whichever key is available."""
    from openai import OpenAI

    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("AI_MODEL")

    if groq_key:
        client = OpenAI(api_key=groq_key, base_url=GROQ_BASE_URL)
        model = model or DEFAULT_GROQ_MODEL
        return client, model

    if openai_key:
        client = OpenAI(api_key=openai_key)
        model = model or DEFAULT_OPENAI_MODEL
        return client, model

    raise RuntimeError("No LLM API key found. Set GROQ_API_KEY or OPENAI_API_KEY.")


def llm_is_available() -> bool:
    """Check if any LLM API key is configured."""
    return bool(os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY"))


def chat_json(
    system_prompt: str,
    user_content: str,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Send a chat completion request and return parsed JSON.

    Uses json_object response format which is compatible with both
    Groq and OpenAI providers.
    """
    client, default_model = get_llm_client()
    selected_model = model or default_model

    response = client.chat.completions.create(
        model=selected_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )
    return json.loads(response.choices[0].message.content)
