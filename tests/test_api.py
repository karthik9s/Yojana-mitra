from fastapi.testclient import TestClient

from yojana_mitra.api import app

client = TestClient(app)


def test_health_and_fields():
    h = client.get("/api/health").json()
    assert h["knowledge_base"]["schemes"] >= 30
    assert "age" in client.get("/api/fields").json()


def test_match_flow():
    r = client.post("/api/match", json={
        "text": "I'm a 45-year-old woman farmer in a village near Guntur with 2 acres. "
                "My two children go to school. We have a white ration card and a gas connection.",
        "use_llm": False,
    }).json()
    ids = {m["scheme_id"] for m in r["eligible"]}
    assert {"annadata_sukhibhava", "talliki_vandanam", "stree_shakti", "deepam_2", "pm_kisan"} <= ids
    assert r["profile"]["state"] == "Andhra Pradesh"
    assert r["extraction"]["method"] == "rules"


def test_followup_override_changes_result():
    base = {"text": "I am a 50 year old woman in a village in Prakasam district", "use_llm": False}
    r1 = client.post("/api/match", json=base).json()
    assert "ntr_bharosa_widow" not in {m["scheme_id"] for m in r1["eligible"]}
    assert any(f["field"] in ("marital_status", "annual_income") for f in r1["followups"])
    answers = {"marital_status": "widowed", "annual_income": 60000, "land_acres": 0}
    r2 = client.post("/api/match", json={**base, "profile": answers}).json()
    assert "ntr_bharosa_widow" in {m["scheme_id"] for m in r2["eligible"]}


def test_other_state_excludes_ap_schemes():
    r = client.post("/api/match", json={"text": "I am a 40 year old woman farmer in Telangana with 3 acres",
                                        "use_llm": False}).json()
    ids = {m["scheme_id"] for m in r["eligible"]}
    assert "annadata_sukhibhava" not in ids and "pm_kisan" in ids


def test_explain_and_ask_offline():
    e = client.post("/api/explain", json={"scheme_id": "talliki_vandanam", "profile": {}, "lang": "te"}).json()
    assert "15,000" in e["answer"] and e["contexts"]
    a = client.post("/api/ask", json={"question": "What documents are needed for widow pension?"}).json()
    assert a["contexts"][0]["scheme_id"] == "ntr_bharosa_widow"


def test_hindi_and_telugu_questions_retrieve_right_scheme():
    # Cross-language retrieval must work even right after startup (dense model still loading).
    a = client.post("/api/ask", json={"question": "मछुआरों को मछली पकड़ने पर रोक के दौरान कितनी मदद मिलती है?", "lang": "hi"}).json()
    assert a["contexts"] and a["contexts"][0]["scheme_id"] in ("matsyakara_sevalo", "ntr_bharosa_fishermen")
    t = client.post("/api/ask", json={"question": "తల్లికి వందనం కోసం ఏ పత్రాలు కావాలి?", "lang": "te"}).json()
    assert "talliki_vandanam" in [c["scheme_id"] for c in t["contexts"][:3]]
