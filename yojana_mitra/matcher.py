"""Turn graph match output into ranked, explained results and follow-up questions."""
from __future__ import annotations

from collections import Counter
from typing import Optional

from pydantic import BaseModel

from .graph import get_store
from .profile import DERIVED_SOURCES, FIELD_META, Profile, derive
from .schemes import scheme_index

STATUS = {1: "eligible", 0: "need_info", -1: "not_eligible"}

# Situational facts people mention when they apply to them. If a scheme is only blocked by one
# of these being unmentioned, it goes to "if_applicable" instead of prompting a question.
TRAIT_FIELDS = {"disability_percent", "health_conditions", "is_pregnant", "has_daughter_under_10",
                "wants_to_start_business", "gate_qualified"}
YOUTH_FIELDS = {"is_student", "education_level"}  # traits for people over 30


class SchemeMatch(BaseModel):
    scheme_id: str
    name: str
    name_local: str
    level: str
    category: str
    amount: str
    summary: str
    portal: str = ""
    status: str  # eligible | need_info | if_applicable | not_eligible
    met: list[str]
    to_confirm: list[str]  # assumed conditions the citizen should confirm
    unknown: list[str]
    not_met: list[str]
    missing_fields: list[str]
    score: float
    in_focus: bool = False  # matches what the citizen asked for


class MatchResult(BaseModel):
    profile: dict
    facts: dict
    eligible: list[SchemeMatch]
    need_info: list[SchemeMatch]
    if_applicable: list[SchemeMatch]
    not_eligible: list[SchemeMatch]
    followups: list[dict]
    backend: str
    focus: list[str] = []


def _raw_fields(field: str) -> list[str]:
    return DERIVED_SOURCES.get(field, [field])


def _is_situational(d: dict, profile: Profile) -> bool:
    """Unknown conditions that only rarely hold, so they shouldn't drive questions.

    E.g. a scheme blocked only because we don't know whether someone is a widow or transgender
    belongs under "if this applies to you", not "we need a few more details".
    """
    cid = d["id"]
    if d["field"] == "gender" and cid.endswith('"transgender"'):
        return True
    if d["field"] == "marital_status" and any(x in cid for x in ("widowed", "divorced", "separated")):
        return True
    if d["field"] == "children_in_school" and (profile.is_student or (profile.age or 99) < 21):
        return True
    return False


def match_profile(profile: Profile, lang: str = "en", store=None,
                  focus_categories: list[str] | None = None) -> MatchResult:
    store = store or get_store()
    facts = derive(profile)
    raw = store.match(facts)
    idx = scheme_index()
    buckets: dict[str, list[SchemeMatch]] = {"eligible": [], "need_info": [], "if_applicable": [],
                                             "not_eligible": []}
    traits = TRAIT_FIELDS | (YOUTH_FIELDS if (profile.age or 0) > 30 else set())
    missing_counter: Counter[str] = Counter()
    focus = set(focus_categories or [])

    for sid, (status, details) in raw.items():
        s = idx[sid]
        # Within an OR group, report the best branch only.
        met, confirm, unknown, not_met, missing = [], [], [], [], []
        best: dict[int, int] = {}
        for d in details:
            best[d["group"]] = max(best.get(d["group"], -1), d["status"])
        # One branch per OR group: prefer a fact that is actually met over an assumed one.
        chosen: dict[int, dict] = {}
        for d in details:
            g = d["group"]
            if d["status"] == best[g] and (g not in chosen or (chosen[g]["assumed"] and not d["assumed"])):
                chosen[g] = d
        situational = False
        for d in chosen.values():
            if d["status"] == 0 and _is_situational(d, profile):
                situational = True
            if d["status"] == 1:
                (confirm if d["assumed"] else met).append(d["label"])
            elif d["status"] == 0:
                unknown.append(d["label"])
                missing.extend(f for f in _raw_fields(d["field"]) if facts.get(f) in (None, []))
            else:
                not_met.append(d["label"])
        missing = list(dict.fromkeys(missing))
        st = STATUS[status]
        if st == "need_info" and (situational or any(f in traits for f in missing)):
            st = "if_applicable"
        if st == "need_info":
            missing_counter.update(missing)
        # Specific schemes (many satisfied conditions) rank above generic ones.
        score = len(met) + 0.3 * len(confirm) - 0.5 * len(unknown)
        buckets[st].append(SchemeMatch(
            scheme_id=sid, name=s.name, name_local=s.display_name(lang), level=s.level, category=s.category,
            amount=s.amount, summary=s.summary, portal=s.portal, status=st, met=met, to_confirm=confirm, unknown=unknown,
            not_met=not_met, missing_fields=missing, score=score, in_focus=s.category in focus,
        ))
    for b in buckets.values():
        b.sort(key=lambda m: (not m.in_focus, -m.score, m.level != "state", m.name))

    # Rank questions by how much they resolve: a field that is the ONLY missing fact of a scheme
    # counts 1, one of two missing facts counts 0.5, etc. Ties keep the order of the (already
    # ranked) need-info schemes, so questions for the most relevant schemes come first.
    weight: dict[str, float] = {}
    for m in buckets["need_info"]:
        for f in m.missing_fields:
            weight[f] = weight.get(f, 0.0) + (3.0 if m.in_focus else 1.0) / len(m.missing_fields)
    ranked = sorted(weight, key=lambda f: -weight[f])[:5]

    followups = []
    for field, n in ((f, missing_counter[f]) for f in ranked):
        meta = FIELD_META.get(field, {})
        followups.append({
            "field": field,
            "question": meta.get(f"q_{lang}") or meta.get("q_en") or field,
            "type": meta.get("type", "text"),
            "options": meta.get("options"),
            "unlocks": n,
        })
    return MatchResult(profile=profile.model_dump(), facts=facts, eligible=buckets["eligible"],
                       need_info=buckets["need_info"], if_applicable=buckets["if_applicable"],
                       not_eligible=buckets["not_eligible"],
                       followups=followups, backend=store.name, focus=sorted(focus))


def eligible_ids(profile: Profile, include_need_info: bool = False, store=None) -> set[str]:
    r = match_profile(profile, store=store)
    ids = {m.scheme_id for m in r.eligible}
    if include_need_info:
        ids |= {m.scheme_id for m in r.need_info}
    return ids


def scheme_lookup(scheme_id: str) -> Optional[dict]:
    s = scheme_index().get(scheme_id)
    return s.model_dump() if s else None
