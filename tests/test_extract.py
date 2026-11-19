from yojana_mitra.extract import extract
from yojana_mitra.extract_rules import extract_rules


def test_english_basic():
    p, _ = extract_rules("I'm a 45-year-old woman farmer in a village near Guntur with 2 acres.")
    assert (p.age, p.gender, p.state, p.area, p.land_acres) == (45, "female", "Andhra Pradesh", "rural", 2.0)
    assert "farmer" in p.occupations


def test_relatives_do_not_leak_into_speaker_profile():
    p, _ = extract_rules("I'm 16, a girl studying 10th class in Srikakulam town. My mother is a widow and works as a daily labourer.")
    assert p.marital_status is None
    assert "agricultural_labourer" not in p.occupations
    assert p.gender == "female" and p.is_student


def test_income_units():
    assert extract_rules("I earn 12,000 a month")[0].annual_income == 144000
    assert extract_rules("family income is 1.8 lakh per year")[0].annual_income == 180000
    assert extract_rules("నెలకు 5000 ఆదాయం")[0].annual_income == 60000


def test_telugu_and_hindi():
    p, _ = extract_rules("నా వయస్సు 52 సంవత్సరాలు. నేను చేనేత కార్మికుడిని, గ్రామంలో ఉంటాను.")
    assert p.age == 52 and "weaver" in p.occupations and p.gender == "male" and p.area == "rural"
    p, _ = extract_rules("मैं 32 साल की महिला हूँ, तिरुपति शहर में रहती हूँ")
    assert p.age == 32 and p.gender == "female" and p.state == "Andhra Pradesh"


def test_ap_student_studying_in_hyderabad():
    p, _ = extract_rules("im 22 years old ,family incme below 1lakh, studying btech final year in hyderabad "
                         "but im andhra pradesh citizen")
    assert (p.age, p.state, p.annual_income, p.education_level) == (22, "Andhra Pradesh", 100000, "professional")
    assert p.is_student and p.studies_outside_ap is True
    p, _ = extract_rules("I am a 29 year old man living in Hyderabad, originally from Guntur")
    assert p.state == "Telangana"


def test_default_state_is_flagged():
    ex = extract("I am a 30 year old man", use_llm=False)
    assert ex.profile.state == "Andhra Pradesh" and ex.assumptions
    ex = extract("I am a 30 year old man from Hyderabad", use_llm=False)
    assert ex.profile.state == "Telangana" and not ex.assumptions
