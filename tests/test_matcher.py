import os

import pytest
import yaml

from yojana_mitra import config
from yojana_mitra.graph import MemoryGraph, evaluate
from yojana_mitra.matcher import match_profile
from yojana_mitra.profile import Profile, derive
from yojana_mitra.schemes import Criterion, load_schemes, parse_kb


def ids(r, bucket="eligible"):
    return {m.scheme_id for m in getattr(r, bucket)}


def test_kb_loads_and_is_valid():
    schemes = load_schemes()
    assert len(schemes) >= 35
    for s in schemes:
        assert s.criteria or s.id, s.id
        assert s.how_to_apply and s.documents and s.sources, f"{s.id} is missing explanation data"


def test_tristate_evaluation():
    c = Criterion(field="age", op="gte", value=60, label="60+")
    assert evaluate(c, 65, False) == (1, False)
    assert evaluate(c, 50, False) == (-1, False)
    assert evaluate(c, None, False) == (0, False)
    assert evaluate(c, None, True) == (1, True)


def test_or_groups_are_disjunctive():
    kb = {"schemes": [{"id": "x", "name": "X", "level": "state", "category": "t",
                       "criteria": [{"any_of": [{"field": "gender", "op": "eq", "value": "female", "label": "f"},
                                                {"field": "age", "op": "gte", "value": 60, "label": "60+"}]}]}]}
    g = MemoryGraph()
    g.load(parse_kb(kb))
    assert g.match({"gender": "male", "age": 65})["x"][0] == 1
    assert g.match({"gender": "male", "age": 30})["x"][0] == -1
    assert g.match({"gender": "male", "age": None})["x"][0] == 0


def test_widow_pension_and_limits():
    p = Profile(age=64, gender="female", state="Andhra Pradesh", area="rural", marital_status="widowed",
                land_acres=0, annual_income=60000)
    r = match_profile(p)
    assert {"ntr_bharosa_old_age", "ntr_bharosa_widow", "stree_shakti"} <= ids(r)
    rich = p.model_copy(update={"annual_income": 600000})
    assert "ntr_bharosa_widow" in ids(match_profile(rich), "not_eligible")


def test_ap_income_limit_depends_on_area():
    base = dict(age=40, state="Andhra Pradesh", annual_income=130000, land_acres=0)
    assert derive(Profile(area="urban", **base))["income_within_ap_limit"] is True
    assert derive(Profile(area="rural", **base))["income_within_ap_limit"] is False
    assert derive(Profile(**base))["income_within_ap_limit"] is None


def test_unknown_facts_produce_followups():
    r = match_profile(Profile(age=50, gender="female", state="Andhra Pradesh"))
    fields = {f["field"] for f in r.followups}
    assert fields & {"marital_status", "annual_income", "area", "land_acres"}
    # situational schemes are not pushed as questions
    assert "pmmvy" not in ids(r, "need_info")


def test_fee_reimbursement_outside_ap_needs_confirmation():
    base = dict(age=22, state="Andhra Pradesh", occupations=["student"], is_student=True,
                education_level="professional", social_category="BC", annual_income=100000)
    in_ap = match_profile(Profile(**base))
    fee = next(m for m in in_ap.eligible if m.scheme_id == "ap_fee_reimbursement")
    assert not any("outside AP" in c for c in fee.to_confirm)
    away = match_profile(Profile(studies_outside_ap=True, **base))
    fee = next(m for m in away.eligible if m.scheme_id == "ap_fee_reimbursement")
    assert any("outside AP" in c for c in fee.to_confirm)
    private = match_profile(Profile(studies_outside_ap=True, outside_ap_admission_ok=False, **base))
    assert "ap_fee_reimbursement" in ids(private, "not_eligible")


def test_student_focus_puts_education_first():
    from yojana_mitra.intent import detect_focus

    p = Profile(age=22, gender="male", state="Andhra Pradesh", area="rural", social_category="EWS",
                occupations=["student"], is_student=True, education_level="professional", annual_income=99984,
                has_lpg_connection=True, has_rice_card=True, owns_pucca_house=True, studies_outside_ap=True)
    focus = detect_focus("I want scholarships and fee reimbursement", p)
    assert focus["topics"] == ["education"] and focus["reason"] == "asked"
    assert detect_focus("", p)["reason"] == "student"
    r = match_profile(p, focus_categories=focus["categories"])
    assert r.eligible[0].scheme_id == "ap_fee_reimbursement" and r.eligible[0].in_focus
    assert not any(m.in_focus for m in r.eligible if m.category in ("household", "retirement_savings"))
    need = [m.scheme_id for m in r.need_info if m.in_focus]
    assert {"csss_pm_usp", "csis_interest_subsidy"} <= set(need)
    assert r.followups[0]["field"] in ("class12_top20", "wants_education_loan", "in_quality_institution")


def test_rare_situations_do_not_become_questions():
    r = match_profile(Profile(age=22, state="Andhra Pradesh", occupations=["student"], is_student=True))
    assert {"ntr_bharosa_widow", "ntr_bharosa_transgender", "talliki_vandanam"} <= ids(r, "if_applicable")


@pytest.mark.skipif(not config.NEO4J_URI, reason="set NEO4J_URI to test Cypher parity with a live Neo4j")
def test_neo4j_parity_with_memory_graph():
    from yojana_mitra.extract_rules import extract_rules
    from yojana_mitra.graph import Neo4jGraph

    neo = Neo4jGraph(config.NEO4J_URI, config.NEO4J_USER, config.NEO4J_PASSWORD)
    neo.load(load_schemes())
    mem = MemoryGraph()
    mem.load(load_schemes())
    path = os.path.join(config.ROOT, "eval", "profiles.yaml")
    for case in yaml.safe_load(open(path, encoding="utf-8"))["profiles"]:
        prof, _ = extract_rules(case["text"])
        if prof.state is None:
            prof = prof.model_copy(update={"state": "Andhra Pradesh"})
        facts = derive(prof)
        a = {k: v[0] for k, v in mem.match(facts).items()}
        b = {k: v[0] for k, v in neo.match(facts).items()}
        assert a == b, case["id"]
