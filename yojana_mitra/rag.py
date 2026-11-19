"""Retrieval over scheme guidelines.

Corpus = one section-level chunk per scheme section (overview, eligibility, benefits, documents,
how to apply) generated from the curated knowledge base, plus any guideline PDFs dropped into
data/pdfs/ (file name prefix = scheme id, e.g. `talliki_vandanam_GO.pdf`).

Retrieval is hybrid:
  * dense  - multilingual-e5-small embeddings (handles Telugu/Hindi queries), stored in Chroma
  * sparse - TF-IDF over word + character n-grams (exact names, numbers, Telugu spellings)
fused with Reciprocal Rank Fusion. If the embedding model or Chroma is unavailable the index
degrades to sparse-only rather than failing.
"""
from __future__ import annotations

import hashlib
import logging
import re
import threading
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from . import config
from .schemes import Scheme, load_schemes

log = logging.getLogger(__name__)

CHUNK_CHARS = 900
OVERLAP = 150


@dataclass
class Chunk:
    id: str
    scheme_id: Optional[str]
    section: str
    title: str
    text: str
    source: str
    meta: dict = field(default_factory=dict)


def _scheme_chunks(s: Scheme) -> list[Chunk]:
    src = s.portal or (s.sources[0] if s.sources else "")
    head = f"{s.name} ({s.name_te})"
    sec = {
        "overview": f"{head}. {s.summary} Offered by {s.department}. Benefit: {s.amount}. {s.details} "
                    + (f"Status note: {s.status_note}" if s.status_note else ""),
        "eligibility": f"{head} - who is eligible: " + "; ".join(dict.fromkeys(c.label for c in s.criteria))
                       + f". {s.details}",
        "benefits": f"{head} - benefits: " + " ".join(s.benefits),
        "documents": f"{head} - documents required: " + "; ".join(s.documents) + ".",
        "how_to_apply": f"{head} - how to apply: " + " ".join(f"Step {i}: {x}" for i, x in enumerate(s.how_to_apply, 1))
                        + (f" Official portal: {s.portal}." if s.portal else ""),
    }
    return [Chunk(id=f"{s.id}#{k}", scheme_id=s.id, section=k, title=s.name, text=v.strip(), source=src)
            for k, v in sec.items()]


def _split(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    out, start = [], 0
    while start < len(text):
        end = min(len(text), start + CHUNK_CHARS)
        if end < len(text):  # break on a sentence boundary when possible
            cut = text.rfind(". ", start + CHUNK_CHARS // 2, end)
            end = cut + 1 if cut != -1 else end
        out.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - OVERLAP, start + 1)
    return [c for c in out if len(c) > 40]


def _pdf_chunks(ids: set[str]) -> list[Chunk]:
    out: list[Chunk] = []
    if not config.PDF_DIR.exists():
        return out
    try:
        from pypdf import PdfReader
    except ImportError:  # pragma: no cover
        return out
    for pdf in sorted(config.PDF_DIR.glob("*.pdf")):
        sid = next((i for i in sorted(ids, key=len, reverse=True) if pdf.stem.lower().startswith(i)), None)
        try:
            reader = PdfReader(str(pdf))
        except Exception as e:
            log.warning("cannot read %s: %s", pdf, e)
            continue
        for pno, page in enumerate(reader.pages, 1):
            for j, piece in enumerate(_split(page.extract_text() or "")):
                out.append(Chunk(id=f"pdf:{pdf.name}:p{pno}:{j}", scheme_id=sid, section="guideline",
                                 title=pdf.stem, text=piece, source=f"{pdf.name} (page {pno})",
                                 meta={"page": pno}))
    return out


def build_corpus() -> list[Chunk]:
    schemes = load_schemes()
    chunks = [c for s in schemes for c in _scheme_chunks(s)]
    chunks += _pdf_chunks({s.id for s in schemes})
    return chunks


class Retriever:
    def __init__(self, chunks: Optional[list[Chunk]] = None, dense: Optional[bool] = None,
                 background: bool = False) -> None:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from scipy.sparse import hstack

        self.chunks = chunks if chunks is not None else build_corpus()
        self.by_id = {c.id: c for c in self.chunks}
        texts = [c.text for c in self.chunks]
        self._word = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1)
        self._char = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, min_df=1)
        self._hstack = hstack
        self._sparse = hstack([self._word.fit_transform(texts), self._char.fit_transform(texts)]).tocsr()
        self.fingerprint = hashlib.sha1("\n".join(c.id + c.text for c in self.chunks).encode()).hexdigest()[:12]
        self.model = None
        self.collection = None
        self._dense_matrix: Optional[np.ndarray] = None
        self._dense_ready = False
        self._dense_done = threading.Event()  # set when dense loading finished (or failed)
        self.dense_backend = "none"
        if not (dense is None or dense):
            self._dense_done.set()
        else:
            # Sparse search works immediately; dense vectors join once the model has loaded.
            self.dense_backend = "loading"
            if background:
                threading.Thread(target=self._init_dense, daemon=True).start()
            else:
                self._init_dense()

    # -- dense ---------------------------------------------------------------------------
    def _init_dense(self) -> None:
        try:
            self._load_dense()
        finally:
            self._dense_done.set()

    def wait_until_ready(self, timeout: float = 180) -> bool:
        """Block until dense retrieval is loaded (or has failed). Returns True if dense is usable."""
        self._dense_done.wait(timeout)
        return self._dense_ready

    def _load_dense(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(config.EMBED_MODEL)
        except Exception as e:
            log.warning("embedding model unavailable (%s); using sparse retrieval only", e)
            self.dense_backend = "none"
            return
        try:
            import chromadb

            config.CACHE_DIR.mkdir(exist_ok=True)
            client = chromadb.PersistentClient(path=str(config.CACHE_DIR / "chroma"))
            name = f"schemes_{self.fingerprint}"
            col = client.get_or_create_collection(name, metadata={"hnsw:space": "cosine"})
            if col.count() != len(self.chunks):
                for old in client.list_collections():
                    oname = getattr(old, "name", old)
                    if oname.startswith("schemes_") and oname != name:
                        client.delete_collection(oname)
                emb = self._embed([c.text for c in self.chunks], "passage")
                col.upsert(ids=[c.id for c in self.chunks], embeddings=emb.tolist(),
                           documents=[c.text for c in self.chunks],
                           metadatas=[{"scheme_id": c.scheme_id or "", "section": c.section} for c in self.chunks])
            self.collection = col
            self.dense_backend = "chroma"
        except Exception as e:
            log.warning("Chroma unavailable (%s); using in-memory vectors", e)
            self._dense_matrix = self._embed([c.text for c in self.chunks], "passage")
            self.dense_backend = "numpy"
        self._dense_ready = True

    def _embed(self, texts: list[str], kind: str) -> np.ndarray:
        # e5 models expect "query: " / "passage: " prefixes.
        return np.asarray(self.model.encode([f"{kind}: {t}" for t in texts], normalize_embeddings=True,
                                            batch_size=32, show_progress_bar=False), dtype=np.float32)

    def _dense_rank(self, query: str, allowed: Optional[set[str]], n: int) -> list[str]:
        if not self._dense_ready:
            return []
        q = self._embed([query], "query")[0]
        if self.collection is not None:
            where = None
            if allowed is not None:
                ids = sorted(allowed)
                where = {"scheme_id": ids[0]} if len(ids) == 1 else {"scheme_id": {"$in": ids}}
            res = self.collection.query(query_embeddings=[q.tolist()], n_results=min(n, len(self.chunks)),
                                        where=where)
            return res["ids"][0]
        sims = self._dense_matrix @ q
        order = np.argsort(-sims)
        return [self.chunks[i].id for i in order if allowed is None or self.chunks[i].scheme_id in allowed][:n]

    # -- sparse --------------------------------------------------------------------------
    def _sparse_rank(self, query: str, allowed: Optional[set[str]], n: int) -> list[str]:
        qv = self._hstack([self._word.transform([query]), self._char.transform([query])]).tocsr()
        sims = (self._sparse @ qv.T).toarray().ravel()
        order = np.argsort(-sims)
        return [self.chunks[i].id for i in order
                if sims[i] > 0 and (allowed is None or self.chunks[i].scheme_id in allowed)][:n]

    # -- public --------------------------------------------------------------------------
    def search(self, query: str, k: int = 6, scheme_ids: Optional[list[str]] = None,
               sections: Optional[list[str]] = None) -> list[dict]:
        allowed = set(scheme_ids) if scheme_ids else None
        pool = max(30, k * 5)
        sparse = self._sparse_rank(query, allowed, pool)
        # Keyword search can't bridge languages (a Telugu/Hindi question vs English guidelines).
        # If it found nothing, or the query is in an Indic script, wait for the multilingual model
        # instead of answering "not found" during the first minute after startup.
        indic = len(re.findall(r"[ऀ-ॿఀ-౿]", query)) > len(query) * 0.3
        if not self._dense_ready and (indic or not sparse):
            self.wait_until_ready()
        rankings = [sparse, self._dense_rank(query, allowed, pool)]
        scores: dict[str, float] = {}
        for ranking in rankings:
            for rank, cid in enumerate(ranking):
                scores[cid] = scores.get(cid, 0.0) + 1.0 / (60 + rank)  # Reciprocal Rank Fusion
        out = []
        for cid, sc in sorted(scores.items(), key=lambda x: -x[1]):
            c = self.by_id[cid]
            if sections and c.section not in sections:
                continue
            out.append({"id": c.id, "scheme_id": c.scheme_id, "section": c.section, "title": c.title,
                        "text": c.text, "source": c.source, "score": round(sc, 5)})
            if len(out) >= k:
                break
        return out

    def scheme_context(self, scheme_id: str, query: str, k: int = 5) -> list[dict]:
        """All structured sections for a scheme first, then the best PDF passages."""
        base = [self.by_id[f"{scheme_id}#{s}"] for s in ("overview", "eligibility", "benefits", "documents",
                                                          "how_to_apply") if f"{scheme_id}#{s}" in self.by_id]
        out = [{"id": c.id, "scheme_id": c.scheme_id, "section": c.section, "title": c.title, "text": c.text,
                "source": c.source, "score": 1.0} for c in base]
        extra = [h for h in self.search(query, k=k + len(out), scheme_ids=[scheme_id]) if h["section"] == "guideline"]
        return out + extra[:2]

    def info(self) -> dict:
        return {"chunks": len(self.chunks), "dense": self.dense_backend,
                "pdf_chunks": sum(1 for c in self.chunks if c.section == "guideline")}


_retriever: Optional[Retriever] = None
_lock = threading.Lock()


def get_retriever() -> Retriever:
    """Build once; concurrent callers (startup warm-up + first request) wait for the same index."""
    global _retriever
    if _retriever is None:
        with _lock:
            if _retriever is None:
                _retriever = Retriever(background=True)
    return _retriever
