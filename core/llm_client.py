"""
LLM API Client for CarbonZero.
Handles calls to Gemini, Groq, and OpenAI using the user-provided API key.
All other agent tool logic remains unchanged in core/agent.py.
"""

import urllib.request
import urllib.error
import json
from typing import Tuple


def call_llm_api(
    provider: str,
    api_key: str,
    system_prompt: str,
    user_message: str,
    model_hint: str = ""
) -> Tuple[bool, str]:
    """
    Calls the chosen LLM provider with the given API key.

    Returns:
        (success: bool, response_text: str)
        If success is False, response_text contains the user-facing error message.
    """
    provider = provider.strip().lower()

    try:
        if provider == "gemini":
            return _call_gemini(api_key, system_prompt, user_message)
        elif provider == "groq":
            return _call_groq(api_key, system_prompt, user_message, model_hint)
        elif provider == "openai":
            return _call_openai(api_key, system_prompt, user_message, model_hint)
        else:
            return False, f"Unknown provider '{provider}'. Please select Gemini, Groq, or OpenAI."
    except urllib.error.HTTPError as e:
        code = e.code
        if code == 401:
            return False, (
                "❌ **Cannot reach your API key** — The key was rejected (HTTP 401 Unauthorized). "
                "Please double-check the key and make sure it matches the selected provider."
            )
        elif code == 403:
            return False, (
                "❌ **Cannot reach your API key** — Access denied (HTTP 403 Forbidden). "
                "Verify that your account has API access enabled for this model."
            )
        elif code == 429:
            return False, (
                "⚠️ **Rate limit reached** — Too many requests (HTTP 429). "
                "Please wait a moment and try again."
            )
        else:
            body = ""
            try:
                body = e.read().decode("utf-8", errors="ignore")[:300]
            except Exception:
                pass
            return False, (
                f"❌ **Cannot reach your API key** — {provider.title()} API returned HTTP {code}. "
                f"Details: {body}"
            )
    except urllib.error.URLError:
        return False, (
            "❌ **Cannot reach your API key** — Network error: could not connect to the API endpoint. "
            "Please check your internet connection and try again."
        )
    except Exception as e:
        return False, f"❌ **Cannot reach your API key** — Unexpected error: {str(e)}"


# ---------------------------------------------------------------------------
# Gemini (Google Generative Language API)
# ---------------------------------------------------------------------------
def _call_gemini(api_key: str, system_prompt: str, user_message: str) -> Tuple[bool, str]:
    model = "gemini-1.5-flash"
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{system_prompt}\n\nUser: {user_message}"}]
            }
        ],
        "generationConfig": {
            "temperature": 0.5,
            "maxOutputTokens": 1024
        }
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    candidates = result.get("candidates", [])
    if not candidates:
        return False, "❌ Gemini returned an empty response. Please try again."
    text = candidates[0]["content"]["parts"][0]["text"]
    return True, text.strip()


# ---------------------------------------------------------------------------
# Groq (OpenAI-compatible endpoint)
# ---------------------------------------------------------------------------
def _call_groq(api_key: str, system_prompt: str, user_message: str, model_hint: str) -> Tuple[bool, str]:
    model = model_hint if model_hint else "llama3-8b-8192"
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message}
        ],
        "temperature": 0.5,
        "max_tokens": 1024
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    text = result["choices"][0]["message"]["content"]
    return True, text.strip()


# ---------------------------------------------------------------------------
# OpenAI
# ---------------------------------------------------------------------------
def _call_openai(api_key: str, system_prompt: str, user_message: str, model_hint: str) -> Tuple[bool, str]:
    model = model_hint if model_hint else "gpt-3.5-turbo"
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message}
        ],
        "temperature": 0.5,
        "max_tokens": 1024
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    text = result["choices"][0]["message"]["content"]
    return True, text.strip()
