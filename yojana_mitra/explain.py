"""RAG generation: per-scheme explanations and free-form Q&A, grounded in retrieved chunks.

With an LLM (Groq or Claude): answers are generated only from the retrieved context, cite chunk numbers like
[1], and are written in the user's language (English / Telugu / Hindi).
Without an LLM: an extractive, template-based answer is assembled from the same chunks, so
the app still works offline (content stays in English; UI labels are localised).
"""
from __future__ import annotations

import logging
import re
from typing import Optional

from . import llm
from .rag import get_retriever
from .schemes import scheme_index

log = logging.getLogger(__name__)

LANG_NAME = {"en": "English", "te": "Telugu (తెలుగు)", "hi": "Hindi (हिन्दी)"}

HEAD = {
    "en": {"why": "Why you qualify", "confirm": "Please confirm", "benefits": "What you get",
           "docs": "Documents to keep ready", "steps": "How to apply", "note": "Note"},
    "te": {"why": "మీరు ఎందుకు అర్హులు", "confirm": "దయచేసి నిర్ధారించండి", "benefits": "మీకు లభించేది",
           "docs": "సిద్ధంగా ఉంచుకోవాల్సిన పత్రాలు", "steps": "దరఖాస్తు విధానం", "note": "గమనిక"},
    "hi": {"why": "आप पात्र क्यों हैं", "confirm": "कृपया पुष्टि करें", "benefits": "आपको क्या मिलेगा",
           "docs": "ज़रूरी दस्तावेज़", "steps": "आवेदन कैसे करें", "note": "ध्यान दें"},
}

EXPLAIN_SYSTEM = """You are Yojana Mitra, a friendly assistant that explains Indian government
welfare schemes to citizens of Andhra Pradesh in simple language.

You get three separate inputs. Keep them separate in your answer:
  A. CITIZEN FACTS - what the citizen told us about themselves.
  B. RULE CHECK - which scheme rules they meet, and which rules we ASSUMED and they must confirm.
  C. PASSAGES - numbered official scheme text. The ONLY source for rules, amounts, documents, steps.

Ground rules:
1. Scheme rules, amounts, dates, documents, portals and steps come ONLY from the PASSAGES. Never add
   a requirement, amount or step that is not written there. Copy numbers and limits exactly
   (e.g. if a passage says ₹13,000 goes to the mother, do not say ₹15,000).
2. Never turn a citizen fact into a rule. The citizen being 52 does NOT mean "eligibility requires
   age 52"; the rule is whatever the passage says (e.g. "50 years or above"). Being SC does NOT mean
   the scheme is only for SC.
3. "Why you qualify": one bullet per rule in RULE CHECK "met", written as
   "<the rule, as worded in RULE CHECK> - you told us: <the matching citizen fact>" (skip the
   "you told us" part if no single fact matches). No other bullets in this section.
4. "Please confirm": one bullet per rule in RULE CHECK "assumed". Phrase each as a question or
   "please confirm that …". NEVER state an assumed rule as a fact about the citizen.
   Omit this section if nothing is assumed.
5. "What you get", "Documents to keep ready", "How to apply": only from the passages, each bullet
   ending with its passage number in square brackets, e.g. [3].
6. If something is not in the passages, say it is best confirmed at the Village/Ward Secretariat.
7. Short sentences for someone with basic literacy, rupee amounts with ₹, no jargon.
8. Write the entire answer in {language}. Keep scheme names recognisable (you may add the English
   name in brackets). Use Markdown with these four or five headings, translated into the answer
   language: "Why you qualify", "Please confirm", "What you get", "Documents to keep ready",
   "How to apply"."""

QA_SYSTEM = """You are Yojana Mitra, an assistant answering questions about Indian government
welfare schemes for citizens of Andhra Pradesh.

- Answer ONLY from the numbered context passages; cite them like [1] after each fact.
- If the context does not contain the answer, say so plainly and suggest asking at the
  Village/Ward Secretariat or calling 1902 (AP grievance helpline). Do not guess.
- Keep it short (under 150 words), simple, and write the whole answer in {language}."""


def _context_block(chunks: list[dict]) -> str:
    return "\n\n".join(f"[{i}] ({c['title']} - {c['section']}) {c['text']}" for i, c in enumerate(chunks, 1))


def _profile_line(profile: dict) -> str:
    keep = {k: v for k, v in profile.items() if v not in (None, [], "")}
    return ", ".join(f"{k}={v}" for k, v in keep.items())


def citizen_facts(profile: dict) -> str:
    """The citizen's own statements, as readable lines (also given to the faithfulness judge)."""
    from .profile import FIELD_META

    lines = []
    for k, v in profile.items():
        if v in (None, [], ""):
            continue
        label = FIELD_META.get(k, {}).get("en", k.replace("_", " "))
        if isinstance(v, bool):
            v = "yes" if v else "no"
        elif isinstance(v, list):
            v = ", ".join(str(x).replace("_", " ") for x in v)
        elif k == "annual_income":
            v = f"₹{v:,} per year (₹{round(v / 12):,} per month)"
        lines.append(f"- {label}: {v}")
    return "\n".join(lines) or "- (nothing stated)"


def _template_explain(scheme_id: str, match: Optional[dict], lang: str) -> str:
    s = scheme_index()[scheme_id]
    h = HEAD.get(lang, HEAD["en"])
    lines = [f"### {s.display_name(lang)}", f"**{s.amount}**", ""]
    if match and match.get("met"):
        lines += [f"**{h['why']}**"] + [f"- ✅ {m}" for m in match["met"]] + [""]
    if match and match.get("to_confirm"):
        lines += [f"**{h['confirm']}**"] + [f"- ❔ {m}" for m in match["to_confirm"]] + [""]
    lines += [f"**{h['benefits']}** [3]"] + [f"- {b}" for b in s.benefits] + [""]
    lines += [f"**{h['docs']}** [4]"] + [f"- {d}" for d in s.documents] + [""]
    lines += [f"**{h['steps']}** [5]"] + [f"{i}. {x}" for i, x in enumerate(s.how_to_apply, 1)]
    if s.status_note:
        lines += ["", f"_{h['note']}: {s.status_note}_ [1]"]
    return "\n".join(lines)


def explain_scheme(scheme_id: str, profile: dict, match: Optional[dict] = None, lang: str = "en",
                   use_llm: Optional[bool] = None) -> dict:
    if scheme_id not in scheme_index():
        raise KeyError(scheme_id)
    s = scheme_index()[scheme_id]
    chunks = get_retriever().scheme_context(scheme_id, f"{s.name} eligibility benefits documents how to apply")
    use_llm = llm.available() if use_llm is None else use_llm
    method = "template"
    text = None
    facts = citizen_facts(profile)
    if use_llm:
        met = (match or {}).get("met", [])
        assumed = (match or {}).get("to_confirm", [])
        user = ("A. CITIZEN FACTS\n" + facts
                + "\n\nB. RULE CHECK\nmet:\n" + ("\n".join(f"- {m}" for m in met) or "- (none)")
                + "\nassumed (must be confirmed by the citizen):\n" + ("\n".join(f"- {m}" for m in assumed) or "- (none)")
                + f"\n\nC. PASSAGES\n{_context_block(chunks)}"
                + f"\n\nExplain the scheme '{s.name}' to this citizen.")
        try:
            text = llm.complete(EXPLAIN_SYSTEM.format(language=LANG_NAME.get(lang, "English")), user,
                                max_tokens=3000, effort="low")
            method = "llm"
        except Exception as e:
            log.warning("LLM explanation failed: %s", e)
    if text is None:
        text = _template_explain(scheme_id, match, lang)
    return {"scheme_id": scheme_id, "answer": text, "method": method, "contexts": chunks,
            "citizen_facts": facts, "sources": sorted(set(s.sources + ([s.portal] if s.portal else [])))}


def _sentences(text: str) -> list[str]:
    return [x.strip() for x in re.split(r"(?<=[.;:])\s+(?=[A-Z0-9₹])", text) if len(x.strip()) > 20]


_STOP = {"the", "and", "for", "what", "how", "does", "do", "did", "can", "will", "get", "give", "gives", "much",
          "many", "which", "who", "when", "where", "this", "that", "with", "from", "about", "are", "is", "my", "me"}
_AMOUNT_Q = re.compile(r"how much|amount|money|benefit|paid|pay|stipend|rupees|₹|ఎంత|డబ్బు|कितना|पैसा|राशि", re.I)


def _passage_body(c: dict) -> str:
    """Drop the 'Scheme name (Telugu name) - section:' prefix every chunk starts with."""
    text = c["text"]
    if text.startswith(c["title"]):
        head = text[:len(c["title"]) + 200]
        m = re.match(re.escape(c["title"]) + r"(?:\s*\([^)]*\))?(?:\s*-\s*[\w /]+:|\.)\s*", head)
        if m:
            text = text[m.end():]
    return text.strip()


def _extractive_answer(question: str, chunks: list[dict]) -> str:
    """Pick the passages' most question-relevant sentences (offline fallback)."""
    qwords = {w for w in re.findall(r"\w+", question.lower()) if len(w) > 2 and w not in _STOP}
    wants_amount = bool(_AMOUNT_Q.search(question))

    def score(s: str) -> float:
        words = set(re.findall(r"\w+", s.lower()))
        sc = len(qwords & words)
        if wants_amount:
            sc += 3 if "₹" in s else (1 if re.search(r"\d", s) else 0)
        return sc

    picked, seen = [], set()
    for i, c in enumerate(chunks[:3], 1):
        body = _passage_body(c)
        sents = [s for s in (_sentences(body) or [body]) if s and s not in seen]
        if not sents:
            continue
        best = max(sents, key=score)
        seen.add(best)
        picked.append(f"- **{c['title']}**: {best} [{i}]")
    if not picked:
        return "I could not find this in the scheme guidelines."
    return "Here is what the scheme guidelines say:\n\n" + "\n".join(picked)


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


_GENERIC_TAIL = re.compile(r"\s+(samman nidhi|yojana|scheme|abhiyan)$", re.I)


def schemes_named_in(question: str) -> list[str]:
    """Scheme ids whose short English name appears in the question ("PM-KISAN", "Talliki Vandanam")."""
    q = _norm(question)
    hits: dict[str, str] = {}
    for sid, s in scheme_index().items():
        short = re.split(r"\s*[(–]\s*|\s+-\s+", s.name)[0].strip()
        for alias in {short, _GENERIC_TAIL.sub("", short)}:
            a = _norm(alias)
            if len(a) >= 5 and a in q and len(a) > len(hits.get(sid, "")):
                hits[sid] = a
    # "pmkisan" is inside "pmkisanmaandhan": keep only the most specific names that matched.
    return [sid for sid, a in hits.items() if not any(a != b and a in b for b in hits.values())]


def answer_question(question: str, scheme_ids: Optional[list[str]] = None, lang: str = "en",
                    profile: Optional[dict] = None, use_llm: Optional[bool] = None, k: int = 6) -> dict:
    named = [] if scheme_ids else schemes_named_in(question)
    if named:
        first = get_retriever().search(question, k=4, scheme_ids=named)
        ids = {c["id"] for c in first}
        chunks = (first + [c for c in get_retriever().search(question, k=k) if c["id"] not in ids])[:k]
    else:
        chunks = get_retriever().search(question, k=k, scheme_ids=scheme_ids)
    if not chunks and scheme_ids:
        chunks = get_retriever().search(question, k=k)
    use_llm = llm.available() if use_llm is None else use_llm
    method, text = "extractive", None
    if use_llm and chunks:
        user = f"Context passages:\n{_context_block(chunks)}\n\n"
        if profile:
            user += f"Citizen profile: {_profile_line(profile)}\n\n"
        user += f"Question: {question}"
        try:
            text = llm.complete(QA_SYSTEM.format(language=LANG_NAME.get(lang, "English")), user,
                                max_tokens=1500, effort="low")
            method = "llm"
        except Exception as e:
            log.warning("LLM QA failed: %s", e)
    if text is None:
        text = _extractive_answer(question, chunks) if chunks else "I could not find this in the scheme guidelines."
    return {"question": question, "answer": text, "method": method, "contexts": chunks}
