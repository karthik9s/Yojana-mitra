"""FastAPI app: JSON API + the single-page web UI.

Run:  uvicorn yojana_mitra.api:app --reload --port 8000
"""
from __future__ import annotations

import logging
import threading
from contextlib import asynccontextmanager
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import config, llm
from .explain import answer_question, explain_scheme
from .extract import extract
from .graph import get_store
from .intent import detect_focus
from .matcher import match_profile
from .profile import FIELD_META, Profile
from .rag import get_retriever
from .schemes import kb_meta, load_schemes, scheme_index

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    get_store()
    # Build the retrieval index in the background so the first page load is fast.
    threading.Thread(target=get_retriever, daemon=True).start()
    yield


app = FastAPI(title="Yojana Mitra", version="1.0", lifespan=lifespan)


@app.middleware("http")
async def no_stale_assets(request, call_next):
    """Browsers must revalidate the page and its JS/CSS (cheap 304s via ETag), so a UI update is
    never shown with half-old files."""
    response = await call_next(request)
    if request.url.path == "/" or request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-cache"
    return response

Lang = Literal["en", "te", "hi"]


class MatchRequest(BaseModel):
    text: str = Field("", max_length=4000)
    profile: Optional[dict] = None  # corrections / answers from the UI
    lang: Lang = "en"
    use_llm: Optional[bool] = None


class ExplainRequest(BaseModel):
    scheme_id: str
    profile: dict = {}
    match: Optional[dict] = None
    lang: Lang = "en"


class AskRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000)
    scheme_ids: Optional[list[str]] = None
    profile: Optional[dict] = None
    lang: Lang = "en"


@app.get("/api/health")
def health() -> dict:
    from . import rag

    return {
        "graph": get_store().stats(),
        "llm": {"enabled": llm.available(), "provider": llm.provider(), "model": llm.model()},
        "retriever": rag._retriever.info() if rag._retriever else {"status": "building"},
        "knowledge_base": {**kb_meta(), "schemes": len(load_schemes())},
    }


@app.get("/api/schemes")
def schemes() -> list[dict]:
    return [s.model_dump(exclude={"criteria"}) | {"criteria": [c.label for c in s.criteria]} for s in load_schemes()]


@app.get("/api/schemes/{scheme_id}")
def scheme(scheme_id: str) -> dict:
    s = scheme_index().get(scheme_id)
    if not s:
        raise HTTPException(404, "unknown scheme")
    return s.model_dump()


@app.get("/api/fields")
def fields() -> dict:
    return FIELD_META


@app.post("/api/match")
def match(req: MatchRequest) -> dict:
    if req.text.strip():
        ex = extract(req.text, use_llm=req.use_llm)
        prof, method, assumptions, notes = ex.profile, ex.method, ex.assumptions, ex.notes
    else:
        prof, method, assumptions, notes = Profile(), "form", [], []
    if req.profile:
        try:
            prof = prof.merged(req.profile)
        except Exception as e:
            raise HTTPException(422, f"invalid profile value: {e}")
    if prof.state is None:
        prof = prof.model_copy(update={"state": "Andhra Pradesh"})
        assumptions.append("State not mentioned - assumed Andhra Pradesh.")
    focus = detect_focus(req.text, prof)
    res = match_profile(prof, lang=req.lang, focus_categories=focus["categories"])
    return {**res.model_dump(), "focus_info": focus,
            "extraction": {"method": method, "assumptions": assumptions, "notes": notes}}


@app.post("/api/explain")
def explain(req: ExplainRequest) -> dict:
    if req.scheme_id not in scheme_index():
        raise HTTPException(404, "unknown scheme")
    return explain_scheme(req.scheme_id, req.profile, req.match, lang=req.lang)


@app.post("/api/ask")
def ask(req: AskRequest) -> dict:
    return answer_question(req.question, req.scheme_ids, lang=req.lang, profile=req.profile)


@app.get("/api/graph")
def graph_view() -> dict:
    """Nodes/edges for the knowledge-graph visualisation."""
    nodes, edges, seen = [], [], set()
    for s in load_schemes():
        nodes.append({"id": s.id, "label": s.name, "kind": "Scheme", "category": s.category, "level": s.level})
        for c in s.criteria:
            if c.id not in seen:
                seen.add(c.id)
                nodes.append({"id": c.id, "label": c.label, "kind": "Criterion"})
            edges.append({"source": s.id, "target": c.id, "group": c.group, "assume": c.assume})
    return {"nodes": nodes, "edges": edges}


app.mount("/static", StaticFiles(directory=str(config.WEB_DIR)), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(config.WEB_DIR / "index.html", headers={"Cache-Control": "no-cache"})
