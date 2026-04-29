"""Shared LLM client factory.

Checks for GEMINI_API_KEY, GROQ_API_KEY, or OPENAI_API_KEY (in that order).
Returns an OpenAI-compatible client and the model name to use.
"""

import json
import os
from typing import Any, Dict, List, Optional


# Provider base URLs
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

# Default models per provider
DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
DEFAULT_OPENAI_MODEL = "gpt-4o"


def get_llm_client():
    """Return (client, model_name) using Gemini, Groq, or OpenAI."""
    from openai import OpenAI

    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("AI_MODEL")

    if gemini_key:
        client = OpenAI(api_key=gemini_key, base_url=GEMINI_BASE_URL)
        model = model or DEFAULT_GEMINI_MODEL
        return client, model

    if groq_key:
        client = OpenAI(api_key=groq_key, base_url=GROQ_BASE_URL)
        model = model or DEFAULT_GROQ_MODEL
        return client, model

    if openai_key:
        client = OpenAI(api_key=openai_key)
        model = model or DEFAULT_OPENAI_MODEL
        return client, model

    raise RuntimeError("No LLM API key found. Set GEMINI_API_KEY, GROQ_API_KEY, or OPENAI_API_KEY.")


def llm_is_available() -> bool:
    """Check if any LLM API key is configured."""
    return bool(
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GROQ_API_KEY")
        or os.getenv("OPENAI_API_KEY")
    )


def chat_json(
    system_prompt: str,
    user_content: str,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """Send a chat completion request and return parsed JSON.

    Uses json_object response format which is compatible with
    Gemini, Groq, and OpenAI providers.
    Includes exponential backoff for handling RateLimitError.
    """
    import time
    import openai
    
    client, default_model = get_llm_client()
    selected_model = model or default_model

    max_retries = 3
    base_delay = 2.0

    for attempt in range(max_retries):
        try:
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
        except openai.RateLimitError as exc:
            if attempt == max_retries - 1:
                raise exc
            time.sleep(base_delay * (2 ** attempt))
