"""LLM access for extraction, explanations, Q&A and the faithfulness judge.

Providers:
  groq       Groq's OpenAI-compatible API (GROQ_API_KEY), via the `openai` SDK
  anthropic  Claude via the official `anthropic` SDK (ANTHROPIC_API_KEY)

Every caller has a non-LLM fallback, so the app works with no key at all.
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Optional

from . import config

log = logging.getLogger(__name__)
_clients: dict = {}


def available() -> bool:
    return config.llm_provider() is not None


def provider() -> Optional[str]:
    return config.llm_provider()


def model() -> Optional[str]:
    return config.llm_model()


def _groq():
    if "groq" not in _clients:
        from openai import OpenAI

        _clients["groq"] = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url=config.GROQ_BASE_URL,
                                  timeout=120, max_retries=8)  # free tier rate limits -> 429s, retried with backoff
    return _clients["groq"]


def _anthropic():
    if "anthropic" not in _clients:
        import anthropic

        _clients["anthropic"] = anthropic.Anthropic()
    return _clients["anthropic"]


def _complete_groq(system: str, user: str, max_tokens: int, json_mode: bool, schema: Optional[dict],
                   effort: str = "low") -> str:
    sys_msg = system
    if json_mode and schema:
        # JSON mode guarantees valid JSON; the schema in the prompt guides its shape and the
        # caller validates it.
        sys_msg += ("\n\nReply with ONLY a JSON object matching this JSON Schema (use null for unknown "
                    "values, include every property):\n" + json.dumps(schema))
    kwargs: dict = {
        "model": config.GROQ_MODEL,
        "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": user}],
        "max_completion_tokens": max_tokens,
        "temperature": 0,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    if "gpt-oss" in config.GROQ_MODEL:
        # Reasoning model: thinking tokens count against max_completion_tokens, so keep a floor
        # and choose how hard it thinks.
        kwargs["reasoning_effort"] = effort if effort in ("low", "medium", "high") else "medium"
        kwargs["max_completion_tokens"] = max(max_tokens, 2000)
    resp = _groq().chat.completions.create(**kwargs)
    return resp.choices[0].message.content or ""


def _complete_anthropic(system: str, user: str, max_tokens: int, effort: str, schema: Optional[dict]) -> str:
    kwargs: dict = {
        "model": config.CLAUDE_MODEL,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}],
        "output_config": {"effort": effort},
        "betas": ["server-side-fallback-2026-07-01"],
        "fallbacks": "default",
    }
    if schema:
        kwargs["output_config"]["format"] = {"type": "json_schema", "schema": schema}
    resp = _anthropic().beta.messages.create(**kwargs)
    if getattr(resp, "stop_reason", None) == "refusal":
        raise RuntimeError("model declined the request")
    return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")


def complete(system: str, user: str, *, max_tokens: int = 4000, effort: str = "low",
             schema: Optional[dict] = None) -> str:
    """One LLM call. `schema` asks for a JSON object of that shape."""
    p = provider()
    if p == "groq":
        return _complete_groq(system, user, max_tokens, schema is not None, schema, effort)
    if p == "anthropic":
        return _complete_anthropic(system, user, max_tokens, effort, schema)
    raise RuntimeError("no LLM configured (set GROQ_API_KEY or ANTHROPIC_API_KEY)")


def complete_json(system: str, user: str, schema: dict, **kw) -> dict:
    text = complete(system, user, schema=schema, **kw)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, re.S)  # tolerate stray text around the object
        if not m:
            raise
        return json.loads(m.group(0))
