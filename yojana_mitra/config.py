"""Runtime configuration (environment variables, paths)."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PDF_DIR = DATA_DIR / "pdfs"
CACHE_DIR = ROOT / ".cache"
WEB_DIR = ROOT / "web"


def _load_dotenv() -> None:
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        v = v.strip()
        if v.startswith("#"):
            v = ""
        elif " #" in v:  # inline comment: KEY=value   # note
            v = v.split(" #", 1)[0].strip()
        v = v.strip('"').strip("'")
        if v:
            os.environ.setdefault(k.strip(), v)


_load_dotenv()

# Graph backend: "auto" uses Neo4j when NEO4J_URI is set and reachable, else the in-memory graph.
GRAPH_BACKEND = os.getenv("YM_GRAPH_BACKEND", "auto")
NEO4J_URI = os.getenv("NEO4J_URI", "")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

# LLM: used when an API key exists; otherwise rule-based / template fallbacks run.
# Provider: "groq" (GROQ_API_KEY) or "anthropic" (ANTHROPIC_API_KEY); auto picks whichever key is set,
# preferring Groq.
LLM_MODE = os.getenv("YM_LLM", "auto")  # auto | on | off
LLM_PROVIDER = os.getenv("YM_LLM_PROVIDER", "auto")  # auto | groq | anthropic
GROQ_MODEL = os.getenv("YM_GROQ_MODEL", "openai/gpt-oss-120b")
GROQ_BASE_URL = os.getenv("YM_GROQ_BASE_URL", "https://api.groq.com/openai/v1")
CLAUDE_MODEL = os.getenv("YM_CLAUDE_MODEL", "claude-opus-5-5")

EMBED_MODEL = os.getenv("YM_EMBED_MODEL", "intfloat/multilingual-e5-small")
# off = keyword (TF-IDF) retrieval only, no PyTorch model: fits small hosts such as Render's free plan.
DENSE = os.getenv("YM_DENSE", "on").lower() not in ("off", "0", "false", "no")

# If the embedding model is already cached, don't make Hugging Face network calls at startup.
_hf_cache = Path(os.getenv("HF_HOME", Path.home() / ".cache" / "huggingface")) / "hub"
if (_hf_cache / ("models--" + EMBED_MODEL.replace("/", "--"))).exists():
    os.environ.setdefault("HF_HUB_OFFLINE", "1")


def llm_provider() -> str | None:
    """Which LLM provider to use, or None for the offline fallbacks.

    Only an explicit API key (e.g. in .env) turns AI mode on.
    """
    if LLM_MODE == "off":
        return None
    has_groq, has_claude = bool(os.getenv("GROQ_API_KEY")), bool(os.getenv("ANTHROPIC_API_KEY"))
    if LLM_PROVIDER == "groq":
        return "groq" if has_groq else None
    if LLM_PROVIDER == "anthropic":
        return "anthropic" if (has_claude or LLM_MODE == "on") else None
    if has_groq:
        return "groq"
    if has_claude:
        return "anthropic"
    return None


def llm_model() -> str | None:
    return {"groq": GROQ_MODEL, "anthropic": CLAUDE_MODEL}.get(llm_provider() or "")
