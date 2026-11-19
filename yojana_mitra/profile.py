"""Citizen profile: the structured facts extracted from a free-text description.

The profile is deliberately *partial*: every field is optional, because people only mention
some facts. The matcher treats a missing field as "unknown", not as "fails".
`derive()` adds computed facts (AP residency, AP income/land limits, unorganised worker...)
that the scheme criteria reference.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

Gender = Literal["female", "male", "transgender"]
Area = Literal["rural", "urban"]
Marital = Literal["married", "unmarried", "widowed", "divorced", "separated"]
SocialCategory = Literal["SC", "ST", "BC", "EWS", "minority", "general"]
LandType = Literal["wet", "dry"]
Education = Literal[
    "none", "primary", "secondary", "intermediate", "iti", "polytechnic", "degree", "professional", "pg"
]

OCCUPATIONS = [
    "farmer", "tenant_farmer", "agricultural_labourer", "dairy_farmer", "fisherman", "weaver",
    "toddy_tapper", "cobbler", "artisan", "street_vendor", "auto_driver", "construction_worker",
    "domestic_worker", "student", "unemployed", "homemaker", "salaried_private", "govt_employee",
    "self_employed", "retired",
]
HEALTH_CONDITIONS = ["kidney_dialysis", "thalassemia", "sickle_cell", "haemophilia", "bedridden"]
UNORGANISED = {
    "agricultural_labourer", "construction_worker", "street_vendor", "domestic_worker", "auto_driver",
    "weaver", "cobbler", "artisan", "toddy_tapper", "fisherman", "tenant_farmer", "dairy_farmer",
    "self_employed",
}
FORMAL_JOBS = {"salaried_private", "govt_employee"}

AP_NAMES = {"andhra pradesh", "ap", "andhra"}


class Profile(BaseModel):
    age: Optional[int] = Field(None, ge=0, le=120)
    gender: Optional[Gender] = None
    state: Optional[str] = None
    district: Optional[str] = None
    area: Optional[Area] = None
    social_category: Optional[SocialCategory] = None
    marital_status: Optional[Marital] = None
    occupations: list[str] = Field(default_factory=list)
    land_acres: Optional[float] = Field(None, ge=0)
    land_type: Optional[LandType] = None
    annual_income: Optional[int] = Field(None, ge=0, description="Household income in rupees per year")
    disability_percent: Optional[int] = Field(None, ge=0, le=100)
    health_conditions: list[str] = Field(default_factory=list)
    is_pregnant: Optional[bool] = None
    children_in_school: Optional[int] = Field(None, ge=0)
    has_daughter_under_10: Optional[bool] = None
    has_lpg_connection: Optional[bool] = None
    has_rice_card: Optional[bool] = None
    owns_pucca_house: Optional[bool] = None
    is_student: Optional[bool] = None
    education_level: Optional[Education] = None
    studies_outside_ap: Optional[bool] = None  # AP resident whose college is in another state
    outside_ap_admission_ok: Optional[bool] = None  # admitted via entrance-test/convener route, not private/deemed
    class12_top20: Optional[bool] = None  # top 20 percentile of Class 12 board (CSSS)
    in_quality_institution: Optional[bool] = None  # NIRF-ranked / government institute (PM Vidyalaxmi)
    wants_education_loan: Optional[bool] = None
    first_year_of_course: Optional[bool] = None
    gate_qualified: Optional[bool] = None
    other_scholarship: Optional[bool] = None
    govt_employee: Optional[bool] = None
    income_tax_payer: Optional[bool] = None
    owns_four_wheeler: Optional[bool] = None
    owns_commercial_vehicle: Optional[bool] = None
    wants_to_start_business: Optional[bool] = None

    def merged(self, overrides: dict) -> "Profile":
        """Apply user corrections from the UI (None/'' values are ignored)."""
        data = self.model_dump()
        for k, v in (overrides or {}).items():
            if k in data and v not in (None, ""):
                data[k] = v
        return Profile.model_validate(data)


def _known_lists(p: Profile) -> bool:
    return bool(p.occupations)


def derive(p: Profile) -> dict:
    """Return the profile as a flat dict plus derived facts used by scheme criteria.

    Derived booleans are None when the inputs needed to decide them are missing.
    """
    d = p.model_dump()
    occ = set(p.occupations)

    # Residency: the app is AP-focused, but we never silently assume a state.
    if p.state:
        d["ap_resident"] = p.state.strip().lower() in AP_NAMES
    else:
        d["ap_resident"] = None

    # AP welfare income limit: ₹10,000/month rural, ₹12,000/month urban.
    inc = p.annual_income
    if inc is None:
        d["income_within_ap_limit"] = True if p.has_rice_card else None
    elif inc <= 120_000:
        d["income_within_ap_limit"] = True
    elif inc > 144_000:
        d["income_within_ap_limit"] = False
    else:  # between the rural and urban limits
        d["income_within_ap_limit"] = {"rural": False, "urban": True}.get(p.area or "", None)

    # AP land limit: < 3 acres wet or < 10 acres dry.
    la = p.land_acres
    if la is None:
        # Non-farm households usually hold no land; only farmers need to state it.
        if _known_lists(p) and not (occ & {"farmer", "tenant_farmer", "dairy_farmer"}):
            d["land_within_ap_limit"] = True
        elif p.has_rice_card:
            d["land_within_ap_limit"] = True
        else:
            d["land_within_ap_limit"] = None
    elif la <= 3:
        d["land_within_ap_limit"] = True
    elif la > 10:
        d["land_within_ap_limit"] = False
    else:
        d["land_within_ap_limit"] = {"dry": True, "wet": False}.get(p.land_type or "", None)

    # Employment-derived facts.
    # (Otherwise govt_employee stays unknown for the household; schemes mark it `assume`.)
    if p.govt_employee is None and "govt_employee" in occ:
        d["govt_employee"] = True
    d["is_unorganised_worker"] = (bool(occ & UNORGANISED) and not (occ & FORMAL_JOBS)) if occ else None
    d["employed_full_time"] = bool(occ & FORMAL_JOBS) if occ else None
    if p.is_student is None and "student" in occ:
        d["is_student"] = True
    # Most AP students study in AP; only an explicit other-state college changes the rule.
    if p.studies_outside_ap is None:
        d["studies_outside_ap"] = False
    return d


# Metadata used by the UI (labels, follow-up questions, input widgets).
FIELD_META: dict[str, dict] = {
    "age": {"type": "int", "en": "Age", "te": "వయస్సు", "hi": "आयु",
            "q_en": "How old are you?", "q_te": "మీ వయస్సు ఎంత?", "q_hi": "आपकी उम्र कितनी है?"},
    "gender": {"type": "enum", "options": ["female", "male", "transgender"], "en": "Gender", "te": "లింగం", "hi": "लिंग",
               "q_en": "What is your gender?", "q_te": "మీ లింగం ఏమిటి?", "q_hi": "आपका लिंग क्या है?"},
    "state": {"type": "text", "en": "State", "te": "రాష్ట్రం", "hi": "राज्य",
              "q_en": "Which state do you live in?", "q_te": "మీరు ఏ రాష్ట్రంలో నివసిస్తున్నారు?", "q_hi": "आप किस राज्य में रहते हैं?"},
    "district": {"type": "text", "en": "District", "te": "జిల్లా", "hi": "जिला"},
    "area": {"type": "enum", "options": ["rural", "urban"], "en": "Area", "te": "ప్రాంతం", "hi": "क्षेत्र",
             "q_en": "Do you live in a village (rural) or a town/city (urban)?", "q_te": "మీరు గ్రామంలో ఉంటారా లేక పట్టణంలోనా?", "q_hi": "आप गाँव में रहते हैं या शहर में?"},
    "social_category": {"type": "enum", "options": ["SC", "ST", "BC", "EWS", "minority", "general"], "en": "Social category", "te": "సామాజిక వర్గం", "hi": "सामाजिक वर्ग",
                        "q_en": "Which social category do you belong to (SC/ST/BC/EWS/minority/general)?", "q_te": "మీ సామాజిక వర్గం ఏమిటి (SC/ST/BC/EWS/మైనారిటీ/జనరల్)?", "q_hi": "आप किस सामाजिक वर्ग से हैं (SC/ST/BC/EWS/अल्पसंख्यक/सामान्य)?"},
    "marital_status": {"type": "enum", "options": ["married", "unmarried", "widowed", "divorced", "separated"], "en": "Marital status", "te": "వైవాహిక స్థితి", "hi": "वैवाहिक स्थिति",
                       "q_en": "What is your marital status?", "q_te": "మీ వైవాహిక స్థితి ఏమిటి?", "q_hi": "आपकी वैवाहिक स्थिति क्या है?"},
    "occupations": {"type": "multi", "options": OCCUPATIONS, "en": "Occupation", "te": "వృత్తి", "hi": "व्यवसाय",
                    "q_en": "What work do you do?", "q_te": "మీరు ఏ పని చేస్తారు?", "q_hi": "आप क्या काम करते हैं?"},
    "land_acres": {"type": "float", "en": "Land (acres)", "te": "భూమి (ఎకరాలు)", "hi": "भूमि (एकड़)",
                   "q_en": "How much land does your family own (in acres)?", "q_te": "మీ కుటుంబానికి ఎన్ని ఎకరాల భూమి ఉంది?", "q_hi": "आपके परिवार के पास कितनी जमीन (एकड़) है?"},
    "land_type": {"type": "enum", "options": ["wet", "dry"], "en": "Land type", "te": "భూమి రకం", "hi": "भूमि प्रकार",
                  "q_en": "Is your land wet (irrigated) or dry?", "q_te": "మీ భూమి మాగాణి (తడి) లేక మెట్ట (పొడి)?", "q_hi": "आपकी जमीन सिंचित है या असिंचित?"},
    "annual_income": {"type": "int", "en": "Household income (₹/year)", "te": "కుటుంబ ఆదాయం (₹/సంవత్సరం)", "hi": "पारिवारिक आय (₹/वर्ष)",
                      "q_en": "What is your total household income per year (₹)?", "q_te": "మీ కుటుంబ వార్షిక ఆదాయం ఎంత (₹)?", "q_hi": "आपके परिवार की सालाना आय कितनी है (₹)?"},
    "disability_percent": {"type": "int", "en": "Disability %", "te": "వైకల్యం %", "hi": "दिव्यांगता %",
                           "q_en": "Do you have a disability certificate? What percentage?", "q_te": "మీకు వైకల్య ధృవపత్రం ఉందా? ఎంత శాతం?", "q_hi": "क्या आपके पास दिव्यांगता प्रमाणपत्र है? कितने प्रतिशत?"},
    "health_conditions": {"type": "multi", "options": HEALTH_CONDITIONS, "en": "Chronic illness", "te": "దీర్ఘకాలిక వ్యాధి", "hi": "दीर्घकालिक रोग"},
    "is_pregnant": {"type": "bool", "en": "Pregnant / new mother", "te": "గర్భిణీ / బాలింత", "hi": "गर्भवती / नई माँ",
                    "q_en": "Are you pregnant or a new mother?", "q_te": "మీరు గర్భిణీ లేదా బాలింతా?", "q_hi": "क्या आप गर्भवती हैं या हाल ही में माँ बनी हैं?"},
    "children_in_school": {"type": "int", "en": "Children in school (Class 1–12)", "te": "బడికి వెళ్లే పిల్లలు (1–12 తరగతి)", "hi": "स्कूल जाने वाले बच्चे (कक्षा 1–12)",
                           "q_en": "How many of your children study in Class 1–12?", "q_te": "మీ పిల్లల్లో ఎంత మంది 1–12 తరగతి చదువుతున్నారు?", "q_hi": "आपके कितने बच्चे कक्षा 1–12 में पढ़ते हैं?"},
    "has_daughter_under_10": {"type": "bool", "en": "Daughter under 10", "te": "10 ఏళ్ల లోపు కుమార్తె", "hi": "10 साल से कम उम्र की बेटी",
                              "q_en": "Do you have a daughter below 10 years?", "q_te": "మీకు 10 ఏళ్ల లోపు కుమార్తె ఉందా?", "q_hi": "क्या आपकी 10 साल से कम उम्र की बेटी है?"},
    "has_lpg_connection": {"type": "bool", "en": "LPG gas connection", "te": "గ్యాస్ కనెక్షన్", "hi": "एलपीजी कनेक्शन",
                           "q_en": "Does your household have an LPG gas connection?", "q_te": "మీ ఇంటికి గ్యాస్ కనెక్షన్ ఉందా?", "q_hi": "क्या आपके घर में एलपीजी गैस कनेक्शन है?"},
    "has_rice_card": {"type": "bool", "en": "Rice card (white ration card)", "te": "బియ్యం కార్డు (తెల్ల రేషన్ కార్డు)", "hi": "राशन कार्ड (सफेद)",
                      "q_en": "Does your family have a rice card (white ration card)?", "q_te": "మీ కుటుంబానికి బియ్యం కార్డు (తెల్ల రేషన్ కార్డు) ఉందా?", "q_hi": "क्या आपके परिवार के पास सफेद राशन कार्ड है?"},
    "owns_pucca_house": {"type": "bool", "en": "Owns a pucca house", "te": "పక్కా ఇల్లు ఉంది", "hi": "पक्का मकान है",
                         "q_en": "Does your family own a pucca (concrete) house?", "q_te": "మీ కుటుంబానికి పక్కా ఇల్లు ఉందా?", "q_hi": "क्या आपके परिवार के पास पक्का मकान है?"},
    "is_student": {"type": "bool", "en": "Currently a student", "te": "ప్రస్తుతం విద్యార్థి", "hi": "वर्तमान में छात्र",
                   "q_en": "Are you currently studying?", "q_te": "మీరు ప్రస్తుతం చదువుతున్నారా?", "q_hi": "क्या आप अभी पढ़ाई कर रहे हैं?"},
    "education_level": {"type": "enum", "options": ["none", "primary", "secondary", "intermediate", "iti", "polytechnic", "degree", "professional", "pg"],
                        "en": "Education", "te": "విద్య", "hi": "शिक्षा",
                        "q_en": "What is your education level (or the course you are studying)?", "q_te": "మీ విద్యార్హత (లేదా చదువుతున్న కోర్సు) ఏమిటి?", "q_hi": "आपकी शिक्षा (या जो कोर्स पढ़ रहे हैं) क्या है?"},
    "class12_top20": {"type": "bool", "en": "Top 20 percentile in Class 12", "te": "ఇంటర్‌లో టాప్ 20 శాతం", "hi": "12वीं में टॉप 20 प्रतिशत",
                      "q_en": "Were you in the top 20% of your Class 12 / Intermediate board (usually around 80%+ marks)?",
                      "q_te": "ఇంటర్మీడియట్‌లో మీ బోర్డులో టాప్ 20% లో ఉన్నారా (సాధారణంగా 80%+ మార్కులు)?",
                      "q_hi": "क्या आप 12वीं बोर्ड में टॉप 20% में थे (आमतौर पर 80%+ अंक)?"},
    "in_quality_institution": {"type": "bool", "en": "NIRF-ranked / govt institute", "te": "NIRF ర్యాంక్ / ప్రభుత్వ సంస్థ", "hi": "NIRF रैंक / सरकारी संस्थान",
                               "q_en": "Is your college NIRF-ranked or a government institute (IIT, NIT, IIIT, central/state university)?",
                               "q_te": "మీ కళాశాల NIRF ర్యాంక్ ఉన్నదా లేదా ప్రభుత్వ సంస్థా (IIT, NIT, IIIT, విశ్వవిద్యాలయం)?",
                               "q_hi": "क्या आपका कॉलेज NIRF रैंक वाला या सरकारी संस्थान (IIT, NIT, IIIT, विश्वविद्यालय) है?"},
    "wants_education_loan": {"type": "bool", "en": "Needs an education loan", "te": "విద్యా రుణం కావాలి", "hi": "शिक्षा ऋण चाहिए",
                             "q_en": "Do you have, or need, an education loan for your course?",
                             "q_te": "మీ కోర్సు కోసం విద్యా రుణం ఉందా లేదా కావాలా?",
                             "q_hi": "क्या आपके पास शिक्षा ऋण है या चाहिए?"},
    "first_year_of_course": {"type": "bool", "en": "In 1st year of course", "te": "కోర్సు మొదటి సంవత్సరం", "hi": "कोर्स का पहला वर्ष"},
    "gate_qualified": {"type": "bool", "en": "GATE qualified", "te": "GATE అర్హత", "hi": "GATE योग्य"},
    "other_scholarship": {"type": "bool", "en": "Already gets another scholarship", "te": "ఇప్పటికే వేరే స్కాలర్‌షిప్", "hi": "पहले से अन्य छात्रवृत्ति"},
    "studies_outside_ap": {"type": "bool", "en": "College outside AP", "te": "కళాశాల ఏపీ బయట", "hi": "कॉलेज आंध्र के बाहर"},
    "outside_ap_admission_ok": {"type": "bool", "en": "Admitted via entrance test (not private/deemed univ.)",
                                "te": "ప్రవేశ పరీక్ష ద్వారా ప్రవేశం", "hi": "प्रवेश परीक्षा से दाखिला"},
    "govt_employee": {"type": "bool", "en": "Govt employee in family", "te": "కుటుంబంలో ప్రభుత్వ ఉద్యోగి", "hi": "परिवार में सरकारी कर्मचारी"},
    "income_tax_payer": {"type": "bool", "en": "Income-tax payer", "te": "ఆదాయపు పన్ను చెల్లింపుదారు", "hi": "आयकर दाता"},
    "owns_four_wheeler": {"type": "bool", "en": "Owns a car", "te": "కారు ఉంది", "hi": "कार है"},
    "owns_commercial_vehicle": {"type": "bool", "en": "Owns auto/taxi", "te": "సొంత ఆటో/ట్యాక్సీ", "hi": "अपना ऑटो/टैक्सी"},
    "wants_to_start_business": {"type": "bool", "en": "Wants to start a business", "te": "వ్యాపారం ప్రారంభించాలనుకుంటున్నారు", "hi": "व्यवसाय शुरू करना चाहते हैं",
                                "q_en": "Do you want to start your own business or unit?", "q_te": "మీరు సొంత వ్యాపారం ప్రారంభించాలనుకుంటున్నారా?", "q_hi": "क्या आप अपना व्यवसाय शुरू करना चाहते हैं?"},
}

# Derived fields map back to the raw fields a citizen can answer.
DERIVED_SOURCES = {
    "ap_resident": ["state"],
    "income_within_ap_limit": ["annual_income", "area"],
    "land_within_ap_limit": ["land_acres", "land_type"],
    "is_unorganised_worker": ["occupations"],
    "employed_full_time": ["occupations"],
}
