"""Profile extraction: LLM (Groq or Claude, JSON output) when available, rule-based otherwise."""
from __future__ import annotations

import logging

from pydantic import BaseModel, ValidationError

from . import llm
from .extract_rules import extract_rules
from .profile import HEALTH_CONDITIONS, OCCUPATIONS, Profile

log = logging.getLogger(__name__)


def _nullable(t: str, **extra) -> dict:
    return {"anyOf": [{"type": t, **extra}, {"type": "null"}]}


def _enum(values: list[str]) -> dict:
    return {"anyOf": [{"type": "string", "enum": values}, {"type": "null"}]}


PROFILE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "age": _nullable("integer"),
        "gender": _enum(["female", "male", "transgender"]),
        "state": _nullable("string"),
        "district": _nullable("string"),
        "area": _enum(["rural", "urban"]),
        "social_category": _enum(["SC", "ST", "BC", "EWS", "minority", "general"]),
        "marital_status": _enum(["married", "unmarried", "widowed", "divorced", "separated"]),
        "occupations": {"type": "array", "items": {"type": "string", "enum": OCCUPATIONS}},
        "land_acres": _nullable("number"),
        "land_type": _enum(["wet", "dry"]),
        "annual_income": _nullable("integer"),
        "disability_percent": _nullable("integer"),
        "health_conditions": {"type": "array", "items": {"type": "string", "enum": HEALTH_CONDITIONS}},
        "is_pregnant": _nullable("boolean"),
        "children_in_school": _nullable("integer"),
        "has_daughter_under_10": _nullable("boolean"),
        "has_lpg_connection": _nullable("boolean"),
        "has_rice_card": _nullable("boolean"),
        "owns_pucca_house": _nullable("boolean"),
        "is_student": _nullable("boolean"),
        "education_level": _enum(["none", "primary", "secondary", "intermediate", "iti", "polytechnic",
                                  "degree", "professional", "pg"]),
        "studies_outside_ap": _nullable("boolean"),
        "outside_ap_admission_ok": _nullable("boolean"),
        "class12_top20": _nullable("boolean"),
        "in_quality_institution": _nullable("boolean"),
        "wants_education_loan": _nullable("boolean"),
        "first_year_of_course": _nullable("boolean"),
        "gate_qualified": _nullable("boolean"),
        "other_scholarship": _nullable("boolean"),
        "govt_employee": _nullable("boolean"),
        "income_tax_payer": _nullable("boolean"),
        "owns_four_wheeler": _nullable("boolean"),
        "owns_commercial_vehicle": _nullable("boolean"),
        "wants_to_start_business": _nullable("boolean"),
    },
}
PROFILE_SCHEMA["required"] = list(PROFILE_SCHEMA["properties"])

SYSTEM = """You extract a citizen's profile for an Indian government-scheme eligibility checker
(focused on Andhra Pradesh). The description may be in English, Telugu, Hindi or a mix
(including romanised Telugu like "nenu raitu ni").

Rules:
- Only fill a field when the text states it or it follows unambiguously. Otherwise use null
  (or [] for lists). Never guess; unknown is handled downstream by asking follow-up questions.
- Facts are about the speaker, not relatives ("my mother is 70" does not set age=70).
  Household facts (income, land, rice card, LPG, house) apply to the speaker's household.
- annual_income is the household's income in rupees per YEAR. Convert monthly amounts (x12),
  "lakh" = 100000, "k" = 1000.
- land_acres in acres (1 hectare = 2.471 acres, 100 cents = 1 acre). "Landless" = 0.
- state: full state name, e.g. "Andhra Pradesh" when an AP district/city/village is named.
- area: "rural" for villages/mandals, "urban" for towns and cities.
- occupations: choose all that apply. tenant_farmer = cultivates leased land (koulu raitu);
  farmer = cultivates own land; agricultural_labourer = works on others' fields for wages;
  artisan = carpenter, potter, goldsmith, blacksmith, tailor, barber, washerman, mason etc.;
  auto_driver includes taxi / cab drivers.
- Text may have typos and missing spaces ("incme below 1lakh" = income below 100000). For "below /
  under / less than X" use X.
- education_level (current course if studying, else highest completed): primary = class 1-7,
  secondary = class 8-10 / SSC, intermediate = class 11-12 / Inter / junior college, iti = ITI,
  polytechnic = diploma, degree = B.A./B.Sc./B.Com./BBA/BCA, professional = B.Tech/B.E./MBBS/BDS/
  B.Pharm/LLB/nursing/B.Arch, pg = M.Tech/M.Sc./MBA/MCA/M.A./M.Com.
- children_in_school = number of the speaker's children studying in Class 1-12.
- has_rice_card = white ration card / rice card / BPL card.
- is_pregnant also true for women who delivered a baby in the last few months.
- state is where the person is domiciled / a citizen of ("I'm from AP but study in Hyderabad" -> state
  "Andhra Pradesh", studies_outside_ap=true). outside_ap_admission_ok = true only if they say they got
  the seat through an entrance test / convener counselling (EAPCET, EAMCET...), false if they say
  management quota or a private/deemed university.
- Student details: class12_top20 (top 20 percentile of the Class 12 board; true if they say e.g. 90%+ in
  Inter/12th), in_quality_institution (IIT/NIT/IIIT/IISER/central or state university/NIRF-ranked),
  wants_education_loan, first_year_of_course (true for 1st year, false for 2nd year or later unless
  lateral entry), gate_qualified, other_scholarship (already receiving a scholarship)."""


def extract_llm(text: str) -> Profile:
    data = llm.complete_json(SYSTEM, f"Citizen's description:\n<<<\n{text}\n>>>", PROFILE_SCHEMA,
                             max_tokens=2000, effort="low")
    data = {k: v for k, v in data.items() if k in Profile.model_fields}
    for key in ("occupations", "health_conditions"):
        allowed = OCCUPATIONS if key == "occupations" else HEALTH_CONDITIONS
        data[key] = [x for x in (data.get(key) or []) if x in allowed]
    # Drop any single field the model filled with an out-of-range value instead of failing the whole
    # extraction (JSON mode guarantees JSON, not schema conformance).
    for _ in range(len(data) + 1):
        try:
            return Profile.model_validate(data)
        except ValidationError as e:
            bad = {err["loc"][0] for err in e.errors() if err.get("loc")}
            if not bad:
                raise
            for k in bad:
                data.pop(k, None)
    return Profile()


class Extraction(BaseModel):
    profile: Profile
    method: str  # "llm" | "rules"
    assumptions: list[str] = []
    notes: list[str] = []


def extract(text: str, use_llm: bool | None = None, default_state: str | None = "Andhra Pradesh") -> Extraction:
    notes: list[str] = []
    method = "rules"
    prof: Profile | None = None
    if use_llm is None:
        use_llm = llm.available()
    if use_llm and text.strip():
        try:
            prof = extract_llm(text)
            method = "llm"
        except Exception as e:  # network, auth, refusal... fall back to rules
            log.warning("LLM extraction failed, using rules: %s", e)
            notes.append("AI extraction unavailable; used the offline rule-based extractor.")
    if prof is None:
        prof, rule_notes = extract_rules(text)
        notes.extend(rule_notes)

    assumptions = []
    if prof.state is None and default_state:
        prof = prof.model_copy(update={"state": default_state})
        assumptions.append(f"State not mentioned - assumed {default_state}.")
    return Extraction(profile=prof, method=method, assumptions=assumptions, notes=notes)
