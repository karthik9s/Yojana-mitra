"""Rule-based profile extraction (offline fallback; English + common Telugu/Hindi terms).

It is intentionally conservative: it only sets a field when the text clearly states it.
The LLM extractor (extract.py) is used when credentials are available.
"""
from __future__ import annotations

import re
from typing import Optional

from .profile import Profile

AP_PLACES = [
    "andhra pradesh", "andhra", "visakhapatnam", "vizag", "vijayawada", "guntur", "nellore", "kurnool",
    "kadapa", "cuddapah", "anantapur", "anantapuram", "tirupati", "chittoor", "ongole", "prakasam",
    "srikakulam", "vizianagaram", "kakinada", "rajahmundry", "rajamahendravaram", "eluru", "machilipatnam",
    "krishna district", "east godavari", "west godavari", "godavari", "amaravati", "palnadu", "bapatla",
    "anakapalli", "nandyal", "sri sathya sai", "puttaparthi", "annamayya", "konaseema", "alluri",
    "parvathipuram", "ntr district", "tenali", "bhimavaram", "hindupur", "proddatur", "madanapalle",
    "narasaraopet", "chirala", "srikalahasti", "araku", "paderu", "amalapuram",
    "ఆంధ్రప్రదేశ్", "ఆంధ్ర", "గుంటూరు", "విజయవాడ", "విశాఖ", "నెల్లూరు", "కర్నూలు", "కడప", "అనంతపురం",
    "తిరుపతి", "చిత్తూరు", "ఒంగోలు", "శ్రీకాకుళం", "విజయనగరం", "కాకినాడ", "రాజమండ్రి", "ఏలూరు", "గోదావరి",
    "आंध्र प्रदेश", "आंध्र", "नेल्लोर", "विशाखापत्तनम", "विजयवाड़ा", "गुंटूर", "तिरुपति", "कुरनूल", "काकीनाडा",
]
LOCAL_DISTRICT = {
    "గుంటూరు": "Guntur", "విజయవాడ": "Vijayawada", "విశాఖ": "Visakhapatnam", "నెల్లూరు": "Nellore",
    "కర్నూలు": "Kurnool", "కడప": "Kadapa", "అనంతపురం": "Anantapur", "తిరుపతి": "Tirupati", "చిత్తూరు": "Chittoor",
    "ఒంగోలు": "Ongole", "శ్రీకాకుళం": "Srikakulam", "విజయనగరం": "Vizianagaram", "కాకినాడ": "Kakinada",
    "రాజమండ్రి": "Rajahmundry", "ఏలూరు": "Eluru", "గోదావరి": "Godavari", "नेल्लोर": "Nellore",
    "विशाखापत्तनम": "Visakhapatnam", "विजयवाड़ा": "Vijayawada", "गुंटूर": "Guntur", "तिरुपति": "Tirupati",
    "कुरनूल": "Kurnool", "काकीनाडा": "Kakinada", "vizag": "Visakhapatnam",
}
LOCAL_NUM = {"ఒక": 1, "ఒక్క": 1, "ఇద్దరు": 2, "ముగ్గురు": 3, "నలుగురు": 4, "एक": 1, "दो": 2, "तीन": 3, "चार": 4}
AP_CITIES_LOCAL = {"नेल्लोर", "विशाखापत्तनम", "विजयवाड़ा", "गुंटूर", "तिरुपति", "कुरनूल", "काकीनाडा"}
AP_CITIES = {"visakhapatnam", "vizag", "vijayawada", "guntur", "nellore", "kurnool", "kadapa", "tirupati",
             "kakinada", "rajahmundry", "rajamahendravaram", "eluru", "ongole", "anantapur", "anantapuram",
             "విజయవాడ", "విశాఖ", "గుంటూరు", "తిరుపతి"}
OTHER_STATES = {
    "telangana": "Telangana", "hyderabad": "Telangana", "warangal": "Telangana", "karimnagar": "Telangana",
    "karnataka": "Karnataka", "bengaluru": "Karnataka", "bangalore": "Karnataka", "tamil nadu": "Tamil Nadu",
    "chennai": "Tamil Nadu", "odisha": "Odisha", "maharashtra": "Maharashtra", "mumbai": "Maharashtra",
    "kerala": "Kerala", "delhi": "Delhi", "uttar pradesh": "Uttar Pradesh", "bihar": "Bihar",
    "west bengal": "West Bengal", "gujarat": "Gujarat", "rajasthan": "Rajasthan", "తెలంగాణ": "Telangana",
    "तेलंगाना": "Telangana",
}

OCC_PATTERNS: list[tuple[str, str]] = [
    ("tenant_farmer", r"tenant farm|tenant cultivat|lease[ds]? (?:land|farm)|cultivat\w* on lease|koulu|kaulu|కౌలు|sharecrop|ccrc"),
    ("agricultural_labourer", r"agri\w* labou?r|farm labou?r|farm worker|daily wage|coolie|కూలీ|వ్యవసాయ కూలి|खेतिहर मजदूर|मजदूर"),
    ("farmer", r"\bfarmer|\bfarming\b|cultivat|agricultur(?!al labou?r)|\bpaddy\b|\bryot|\brythu|\brai?th?u\b|రైతు|వ్యవసాయం|किसान|खेती"),
    ("dairy_farmer", r"dairy|cattle|buffalo|goat rear|sheep rear|poultry|పాడి|पशुपालन"),
    ("fisherman", r"fisher|fishing|\bfish\b|మత్స్య|చేపల|मछुआर|मछली"),
    ("weaver", r"weav|handloom|చేనేత|నేత|बुनकर"),
    ("toddy_tapper", r"toddy|gouda|gowda|గీత|కల్లు|ताड़ी"),
    ("cobbler", r"cobbler|shoe repair|చెప్పులు|మోచీ|मोची"),
    ("artisan", r"carpenter|blacksmith|goldsmith|potter|pottery|sculpt|stone carv|barber|washer ?man|dhobi|tailor|mason|basket|mat weav|broom|locksmith|toy mak|garland|boat mak|net mak|వడ్రంగి|కుమ్మరి|కంసాలి|టైలర్|దర్జీ|నాయీ|చాకలి|बढ़ई|कुम्हार|दर्जी|नाई|धोबी|सुनार|लोहार"),
    ("street_vendor", r"street vendor|vendor|hawker|push ?cart|road ?side (?:stall|shop)|tiffin (?:cart|stall)|vegetable sell|fruit sell|sell\w* (?:vegetables|fruits|flowers|tea)|tea stall|bandi|తోపుడు బండి|రోడ్డు పక్కన|रेहड़ी|ठेला"),
    ("auto_driver", r"auto ?(?:rickshaw)? ?driver|(?:drive|run|own) (?:an?|my|my own|the|our) (?:own )?auto|taxi|cab driver|maxi ?cab|ఆటో|ऑटो"),
    ("construction_worker", r"construction|building work|mason helper|బిల్డింగ్ పని|निर्माण"),
    ("domestic_worker", r"domestic work|house ?maid|maid\b|housemaid|ఇంటి పని|घरेलू"),
    ("student", r"\bstudent|\bstudying|\bstudy\b|pursuing|doing (?:my |a )?(?:b\.?\s?tech|m\.?\s?tech|b\.?\s?sc|m\.?\s?sc|b\.?com|m\.?com|b\.?a\b|m\.?a\b|mba|mca|degree|diploma|iti|inter|phd)|i am in (?:class|\d+(?:st|nd|rd|th))|విద్యార్థి|చదువుతున్న|छात्र|पढ़ रह"),
    ("unemployed", r"unemploy|jobless|no job|looking for (?:a )?job|నిరుద్యోగ|बेरोजगार"),
    ("homemaker", r"homemaker|housewife|house wife|గృహిణి|गृहिणी"),
    ("govt_employee", r"government (?:employee|job|teacher|servant)|govt\.? (?:employee|job|teacher)|ప్రభుత్వ ఉద్యోగ|सरकारी नौकरी"),
    ("salaried_private", r"software|private (?:job|company|employee)|i work (?:at|for|in) (?:a|an) (?:company|firm|it)|salaried|\bit (?:job|company|employee)|accountant|engineer at"),
    ("self_employed", r"small (?:shop|business)|kirana|own (?:a )?shop|self[- ]employed|petty shop|దుకాణం|दुकान"),
    ("retired", r"retired|రిటైర్|सेवानिवृत्त"),
]

EDU_PATTERNS: list[tuple[str, str]] = [
    ("pg", r"\bm\.?\s?(?:tech|sc|com|ba|ca)\b|\bmba\b|\bmca\b|post ?grad|master'?s|\bpg\b"),
    ("professional", r"b\.?\s?tech|\bb\.?e\.?\b|engineering|mbbs|\bmedicine\b|b\.?\s?pharm|pharmacy|nursing|\bllb\b|\bbds\b|\bb\.?arch"),
    ("polytechnic", r"polytechnic|diploma"),
    ("iti", r"\biti\b"),
    ("degree", r"\bdegree\b|\bb\.?\s?(?:sc|com|a)\b|\bbsc\b|\bbcom\b|\bbba\b|\bbca\b|graduat|డిగ్రీ"),
    ("intermediate", r"intermediate|\binter\b|\b(?:11|12)th\b|class (?:11|12)|junior college|ఇంటర్|इंटर"),
    ("secondary", r"\b(?:10|ssc|9|8)th\b|\bssc\b|tenth|class (?:8|9|10)|పదో తరగతి|दसवीं"),
    ("primary", r"class [1-7]\b|primary school"),
]

WORD_NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "a": 1, "an": 1, "single": 1}
NUM = r"(\d+(?:\.\d+)?|one|two|three|four|five|six)"


def _num(tok: str) -> float:
    tok = tok.lower()
    return float(WORD_NUM[tok]) if tok in WORD_NUM else float(tok.replace(",", ""))


def _amount(num: str, unit: Optional[str]) -> int:
    v = float(num.replace(",", ""))
    unit = (unit or "").lower()
    if unit.startswith(("lakh", "lac", "l", "లక్ష", "लाख")):
        v *= 100_000
    elif unit.startswith(("k", "thousand", "వేల", "हजार", "हज़ार")):
        v *= 1_000
    elif unit.startswith(("crore", "cr")):
        v *= 10_000_000
    return int(v)


def _income(t: str) -> Optional[int]:
    unit = r"(lakhs?|lacs?|l\b|k\b|thousand|crores?|లక్ష\w*|వేల\w*|लाख|हजार|हज़ार)?"
    money = r"(?:rs\.?|₹|inr|rupees)?\s*(\d[\d,]*(?:\.\d+)?)\s*" + unit
    per_month = r"(?:per|a|/|every|each)\s*(?:month|mon|mo)\b|monthly|నెలకు|प्रति माह|महीना|हर महीने"
    per_year = r"(?:per|a|/|every|each)\s*(?:year|annum|yr)\b|annual|yearly|p\.?a\.?|సంవత్సరానికి|సాలీనా|सालाना|प्रति वर्ष"
    ctx = r"(?:\binc?o?me\b|earn\w*|salary|make|making|get|getting|ఆదాయం|సంపాదన|आय|आमदनी|कमा)"
    for m in re.finditer(ctx + r"[^.\n]{0,40}?" + money + r"\s*([^.\n]{0,25})", t):
        amt = _amount(m.group(1), m.group(2))
        tail = m.group(3)
        if amt < 100:
            continue
        if re.search(per_month, tail):
            return amt * 12
        if re.search(per_year, tail):
            return amt
        # No period stated: amounts under ₹50,000 are almost always monthly.
        return amt * 12 if amt < 50_000 else amt
    m = re.search(money + r"\s*(" + per_month + "|" + per_year + ")", t)
    if m and (m.group(1)):
        amt = _amount(m.group(1), m.group(2))
        if amt >= 100:
            return amt * 12 if re.search(per_month, m.group(3)) else amt
    # Period before the amount: "నెలకు 5000", "सालाना 1.2 लाख", "monthly 8000", "महीने की आय 10,000"
    m = re.search(r"(నెలకు|నెల|प्रति माह|महीने|मासिक|monthly|సంవత్సరానికి|సాలీనా|सालाना|वार्षिक|yearly|annual)"
                  r"[^.\d\n]{0,20}?" + money, t)
    if m:
        amt = _amount(m.group(2), m.group(3))
        if amt >= 100:
            return amt * 12 if re.match(r"నెల|प्रति माह|महीने|मासिक|monthly", m.group(1)) else amt
    if re.search(r"no income|zero income|ఆదాయం లేదు|कोई आय नहीं", t):
        return 0
    return None


FEMALE_SELF = r"woman|women|female|lady|girl|mother|housewife|homemaker|widow|grandmother|మహిళ|స్త్రీ|గృహిణి|వితంతు|महिला|औरत|विधवा|गृहिणी"
MALE_SELF = r"man|male|boy|father|gentleman|guy|widower|grandfather|పురుషుడు|పురుష|అబ్బాయి|पुरुष|आदमी|लड़का"


def _gender(t: str) -> Optional[str]:
    if re.search(r"transgender|trans woman|trans man|hijra|ట్రాన్స్|किन्नर|ट्रांसजेंडर", t):
        return "transgender"
    # Spouse references reveal the speaker's gender.
    if re.search(r"\bmy (?:late )?husband|lost my husband|భర్త|मेरे पति", t):
        return "female"
    if re.search(r"\bmy (?:late )?wife\b|భార్య|मेरी पत्नी", t):
        return "male"

    def self_hit(pat: str) -> bool:
        for m in re.finditer(r"(?<![a-z])(?:" + pat + r")(?![a-z])", t):
            before = t[max(0, m.start() - 25):m.start()]
            # "my mother", "my daughter's school", "a girl child" are about someone else.
            if re.search(r"(?:\bmy|\bour|\bhis|\bher|\btheir)\s+(?:\w+\s+){0,1}$", before):
                continue
            after = t[m.end():m.end() + 8]
            if re.match(r"\s*child", after):
                continue
            return True
        return False

    # Grammatical gender of first-person verbs/nouns in Hindi and Telugu.
    hi_m = re.search(r"(?:साल|वर्ष) का\b|(?:रहता|करता|चलाता|लगाता|कमाता) हूँ|मैं [^।.]{0,20}युवक", t)
    hi_f = re.search(r"(?:साल|वर्ष) की\b(?! (?:बेटी|बच्ची))|(?:रहती|करती|चलाती|लगाती|कमाती) हूँ", t)
    te_m = re.search(r"నేను[^.]{0,40}(?:డిని|వాడిని|కుడిని)|పురుషుడిని", t)
    te_f = re.search(r"నేను[^.]{0,40}(?:రాలిని|స్త్రీని|మహిళను|వితంతువును)", t)
    if (hi_m or te_m) and not (hi_f or te_f):
        return "male"
    if (hi_f or te_f) and not (hi_m or te_m):
        return "female"

    f, m_ = self_hit(FEMALE_SELF), self_hit(MALE_SELF)
    if f and not m_:
        return "female"
    if m_ and not f:
        return "male"
    if f and m_:
        # e.g. "I am a woman ... my husband is a man"; prefer the first-person statement
        fi = re.search(r"\bi(?:'m| am)\b[^.]{0,40}(?:" + FEMALE_SELF + ")", t)
        mi = re.search(r"\bi(?:'m| am)\b[^.]{0,40}(?<![a-z])(?:" + MALE_SELF + ")(?![a-z])", t)
        if fi and not mi:
            return "female"
        if mi and not fi:
            return "male"
    return None


def extract_rules(text: str) -> tuple[Profile, list[str]]:
    """Return (profile, notes)."""
    t = " " + text.lower().replace("’", "'") + " "
    # Text about the speaker only: drop clauses describing relatives ("my husband is a farmer",
    # "my mother is a widow") before detecting occupation, marital status, disability, education.
    ts = re.sub(r"\b(?:my|our|his|her)\s+(?:late\s+)?(?:mother|father|husband|wife|son|daughter|brother|sister|"
                r"parents|children|kids|grand\w+|in-laws?|father-in-law|mother-in-law)\b[^.,;!?।]*", " ", t)
    ts = re.sub(r"(?:మా|నా)\s*(?:భర్త|అమ్మ|నాన్న|తల్లి|తండ్రి|కొడుకు|కూతురు)[^.,;!?]*|"
                r"(?:मेरे|मेरी|मेरा)\s*(?:पति|माँ|पिता|बेटे|बेटी|बेटा)[^.,;!?।]*", " ", ts)
    d: dict = {}
    notes: list[str] = []

    # ---- age
    m = (re.search(r"(\d{1,3})\s*(?:-|\s)?\s*(?:years?|yrs?|yo)\b(?:[\s-]*old)?", t)
         or re.search(r"\b(?:age|aged)\s*(?:is|of|:)?\s*(\d{1,3})\b", t)
         or re.search(r"(?:వయస్సు|వయసు|उम्र|आयु)\s*(?:[^\d\s]+\s*)?(\d{1,3})", t)
         or re.search(r"(\d{1,3})\s*(?:ఏళ్ల|ఏళ్లు|సంవత్సరాల|సంవత్సరాలు|ఏండ్ల|साल|वर्ष|बरस)", t)
         or re.search(r"\bi(?:'m| am)\s+(\d{1,3})\b(?!\s*(?:acres?|lakh|k\b|%|children|kids))", t))
    if m:
        a = int(m.group(1))
        if 0 < a < 120:
            d["age"] = a

    # ---- gender (ignore words about relatives: "my son", "my mother"...)
    d_gender = _gender(t)
    if d_gender:
        d["gender"] = d_gender

    # ---- state / district / area
    other = next((v for k, v in OTHER_STATES.items() if k in t), None)
    ap_hit = next((k for k in AP_PLACES if re.search(r"(?<![a-z])" + re.escape(k) + r"(?![a-z])", t)), None)
    other_keys = "|".join(re.escape(k) for k in OTHER_STATES)
    domicile_ap = re.search(r"(?:andhra pradesh|andhra|\bap)\s+(?:citizen|native|domicile|resident|local)|"
                            r"(?:citizen|native|resident|domicile|local) (?:of|from) (?:andhra|ap\b)|"
                            r"\b(?:i am|i'm|im) from (?:andhra|ap\b)|belong to (?:andhra|ap\b)", t)
    lives_other = re.search(r"(?:\blive|\bliving|\bstay|\bstaying|\breside|\bresiding|settled|\bworking|\bwork)\s+(?:in|at)\s+"
                            r"(?:[a-z]+\s+){0,2}?(?:" + other_keys + ")", t)
    studies_other = re.search(r"(?:\bstudy|\bstudying|college|university|b\.?\s?tech|degree|course|pursuing)[^.]{0,40}?"
                              r"\b(?:in|at)\s+(?:" + other_keys + ")", t)
    if ap_hit and other and lives_other and not domicile_ap:
        ap_hit = None  # "I live in Hyderabad, originally from Guntur" -> resident of the other state
    if domicile_ap and not ap_hit:
        ap_hit = "andhra pradesh"
    if ap_hit and studies_other and re.search(OCC_PATTERNS[next(i for i, (n, _) in enumerate(OCC_PATTERNS) if n == "student")][1], t):
        d["studies_outside_ap"] = True
    if ap_hit:
        d["state"] = "Andhra Pradesh"
        if ap_hit not in ("andhra pradesh", "andhra", "ఆంధ్రప్రదేశ్", "ఆంధ్ర", "आंध्र प्रदेश", "आंध्र"):
            d["district"] = LOCAL_DISTRICT.get(ap_hit, ap_hit.title())
    elif other:
        d["state"] = other
    if re.search(r"\bvillage|rural|\bgram\b|hamlet|thanda|tanda|mandal|గ్రామ|ఊరు|పల్లె|गाँव|गांव|ग्रामीण", t):
        d["area"] = "rural"
    elif re.search(r"\bcity\b|\btown\b|urban|municipal|corporation|\bslum|పట్టణ|నగర|शहर", t) or (ap_hit in AP_CITIES | AP_CITIES_LOCAL):
        d["area"] = "urban"

    # ---- social category
    if re.search(r"\bsc\b|scheduled caste|dalit|\bmala\b|madiga|ఎస్సీ|मादिगा|अनुसूचित जाति", t):
        d["social_category"] = "SC"
    elif re.search(r"\bst\b(?! ?(?:class|year|standard))|scheduled tribe|tribal|adivasi|girijan|koya|yanadi|sugali|lambada|chenchu|గిరిజన|ఎస్టీ|आदिवासी|अनुसूचित जनजाति", t):
        d["social_category"] = "ST"
    elif re.search(r"\bbc\b|\bobc\b|backward class|బీసీ|पिछड़ा", t):
        d["social_category"] = "BC"
    elif re.search(r"\bews\b|economically weaker", t):
        d["social_category"] = "EWS"
    elif re.search(r"muslim|christian|minority|మైనారిటీ|अल्पसंख्यक", t):
        d["social_category"] = "minority"
    elif re.search(r"\boc\b|general category|forward caste|\bgeneral\b caste", t):
        d["social_category"] = "general"

    # ---- marital status
    if (re.search(r"widow(?!er)|వితంతు|विधवा", ts)
            or re.search(r"my (?:late )?husband (?:died|passed|expired|is no more|is dead)|lost my husband|"
                         r"భర్త (?:చనిపోయ|మరణ)|पति की मृत्यु", t)):
        d["marital_status"] = "widowed"
    elif re.search(r"widower", ts) or re.search(r"my wife (?:died|passed|expired)", t):
        d["marital_status"] = "widowed"
    elif re.search(r"divorc|విడాకులు|तलाक", ts):
        d["marital_status"] = "divorced"
    elif re.search(r"separated|deserted|abandoned by", ts) or re.search(r"my husband left|left by (?:my )?husband", t):
        d["marital_status"] = "separated"
    elif re.search(r"unmarried|not married|single woman|never married|అవివాహిత|పెళ్లి కాలేదు|अविवाहित", ts):
        d["marital_status"] = "unmarried"
    elif re.search(r"married|my husband|my wife|husband and|wife and|భర్త|భార్య|मेरे पति|मेरी पत्नी", t):
        d["marital_status"] = "married"

    # ---- occupations (speaker's own clauses only)
    occ: list[str] = []
    for name, pat in OCC_PATTERNS:
        if re.search(pat, ts):
            occ.append(name)
    if "dairy_farmer" in occ and "farmer" in occ and not re.search(r"\bfarmer\b(?<!dairy farmer)|farming|cultivat|రైతు|किसान", ts.replace("dairy farmer", "")):
        occ.remove("farmer")
    if "unemployed" not in occ and re.search(r"not working|no work\b|without (?:a )?job", ts):
        occ.append("unemployed")
    if "tenant_farmer" in occ and "farmer" in occ and not re.search(r"own (?:\d|land)|my (?:own )?land|pattadar|పట్టా", t):
        occ.remove("farmer")
    if "agricultural_labourer" in occ and "farmer" in occ and not re.search(r"\bmy (?:own )?(?:land|farm|field)|i own|own \d|acres? of (?:my )?(?:own )?land|have \d+(?:\.\d+)? acres?", t):
        occ.remove("farmer")
    if "salaried_private" in occ and "govt_employee" in occ:
        occ.remove("salaried_private")
    if re.search(r"(?:husband|wife|son|father|daughter|brother) (?:is|works as) (?:a )?(?:government|govt)", t):
        d["govt_employee"] = True
        occ = [o for o in occ if o != "govt_employee"] or occ
    d["occupations"] = occ

    # ---- land
    m = re.search(NUM + r"\s*(?:acres?|acre|ఎకరాలు|ఎకరా|ఎకరాల|एकड़)", t)
    if m:
        d["land_acres"] = _num(m.group(1))
    else:
        m = re.search(NUM + r"\s*(?:hectares?|ha\b|హెక్టార్|हेक्टेयर)", t)
        if m:
            d["land_acres"] = round(_num(m.group(1)) * 2.471, 2)
        else:
            m = re.search(r"(\d+)\s*cents?\b|(\d+)\s*సెంట్లు", t)
            if m:
                d["land_acres"] = int(m.group(1) or m.group(2)) / 100
    if re.search(r"no land|landless|(?:don't|do not|doesn't) own (?:any )?(?:farm ?)?land|without land|భూమి లేదు|जमीन नहीं|ज़मीन नहीं", t):
        d["land_acres"] = 0.0
    if re.search(r"wet land|wetland|irrigated|canal|paddy land|మాగాణి|सिंचित", t):
        d["land_type"] = "wet"
    elif re.search(r"dry ?land|rain[- ]?fed|unirrigated|మెట్ట|असिंचित|बारानी", t):
        d["land_type"] = "dry"

    # ---- income
    inc = _income(t)
    if inc is not None:
        d["annual_income"] = inc

    # ---- disability / health
    m = re.search(r"(\d{1,3})\s*%\s*(?:disab|handicap|వైకల్య|दिव्यांग)|(?:disab\w*|handicap\w*|వైకల్యం)[^.\d]{0,20}(\d{1,3})\s*%", ts)
    if m:
        d["disability_percent"] = int(m.group(1) or m.group(2))
    elif re.search(r"disabled|disability|handicap|blind|deaf|polio|wheelchair|దివ్యాంగ|వికలాంగ|दिव्यांग|विकलांग", ts):
        notes.append("Disability mentioned without a percentage; SADAREM certificate percentage is needed.")
    hc = []
    if re.search(r"dialysis|kidney fail|ckd|kidney disease|డయాలసిస్|కిడ్నీ|डायलिसिस", t):
        hc.append("kidney_dialysis")
    if re.search(r"thalass", t):
        hc.append("thalassemia")
    if re.search(r"sickle", t):
        hc.append("sickle_cell")
    if re.search(r"ha?emophilia", t):
        hc.append("haemophilia")
    if re.search(r"bed[- ]?ridden|paraly|మంచానికే|लकवा", t):
        hc.append("bedridden")
    d["health_conditions"] = hc

    # ---- pregnancy / children
    if re.search(r"pregnan|expecting (?:a|my) (?:baby|child)|months? pregnant|గర్భిణ|గర్భవతి|गर्भवती|delivered (?:a|my)|new ?born|just gave birth", t):
        d["is_pregnant"] = True
    m = re.search(NUM + r"\s*(?:of (?:my|our) )?(?:school[- ]going |school |)(?:children|kids|sons|daughters|పిల్లలు|बच्चे)[^.]{0,40}?(?:school|class|study|studying|చదువు|బడి|स्कूल|पढ़)", t)
    if m:
        d["children_in_school"] = int(_num(m.group(1)))
    elif re.search(r"\b(?:my|our) (?:\w+ )?(?:son|daughter|child|kid|boy|girl)s?\b[^.]{0,30}(?:studies|studying|goes to school|in (?:class|\d+(?:st|nd|rd|th)) |school)", t) \
            or re.search(r"children (?:are )?(?:in|go to|studying in) school|kids (?:go to|in) school|బడికి వెళ్తు", t) \
            or re.search(r"(?:son|daughter|child|kid)\b[^.]{0,40}\b(?:he|she) (?:goes to|studies in|is in) (?:school|class)", t):
        d["children_in_school"] = 2 if re.search(r"(?:son|daughter|child|kid)s? and (?:a )?(?:son|daughter|child|kid)|two|both", t) else 1
    m = re.search(r"(ఒక్క|ఒక|ఇద్దరు|ముగ్గురు|నలుగురు|एक|दो|तीन|चार)\s*(?:పిల్లలు|బిడ్డ\w*|కొడుకు\w*|కూతురు\w*|बच्चे|बच्चा|बेटे|बेटियाँ)[^.]{0,40}?(?:బడి|స్కూల్|చదువు|स्कूल|पढ़)", t)
    if m:
        d["children_in_school"] = LOCAL_NUM[m.group(1)]
    if re.search(r"no children|don't have (?:any )?children|childless", t):
        d["children_in_school"] = 0
    m = re.search(r"daughter[^.]{0,25}?(?:aged? |is |of )?(\d{1,2})\s*(?:years?|yrs?|-year)|(\d{1,2})[- ]year[- ]old daughter|(\d{1,2}) ?(?:yo|y/o) daughter|(\d{1,2})\s*(?:साल|वर्ष) की (?:बेटी|बच्ची)|(\d{1,2})\s*ఏళ్ల (?:కూతురు|పాప)|baby girl|infant daughter|newborn daughter|first baby, a girl|a baby girl", t)
    if m:
        ages = [g for g in m.groups() if g]
        d["has_daughter_under_10"] = (int(ages[0]) < 10) if ages else True

    # ---- household assets
    if re.search(r"no (?:lpg|gas)|without (?:lpg|gas)|don't have (?:an? )?(?:lpg|gas)|do not have (?:an? )?(?:lpg|gas)|(?:cook|cooking) (?:with|on) (?:firewood|wood|kerosene)|firewood|కట్టెల|గ్యాస్ (?:కనెక్షన్ )?లేదు|लकड़ी|गैस नहीं", t):
        d["has_lpg_connection"] = False
    elif re.search(r"lpg|gas connection|gas cylinder|cooking gas|గ్యాస్|गैस", t):
        d["has_lpg_connection"] = True
    if re.search(r"no (?:rice|ration|white) card|don't have (?:a )?(?:rice|ration)", t):
        d["has_rice_card"] = False
    elif re.search(r"rice card|white (?:ration )?card|ration card|bpl card|\bbpl\b|బియ్యం కార్డు|తెల్ల రేషన్|రేషన్ కార్డు|राशन कार्ड|बीपीएल", t):
        d["has_rice_card"] = True
    if re.search(r"no (?:own |pucca )?house|(?:don't|doesn't|do not|does not) (?:own|have) (?:a |our own |my own )?(?:pucca )?house|we rent\b|homeless|kutcha|kachha|katcha|hut\b|thatched|rented (?:house|room)|live (?:on|in a) rent|రేకుల|గుడిసె|సొంత ఇల్లు లేదు|झोपड़ी|कच्चा मकान|किराये", t):
        d["owns_pucca_house"] = False
    elif re.search(r"own (?:a |our |my )?(?:pucca |concrete )?house|pucca house|own home|సొంత ఇల్లు|पक्का मकान", t):
        d["owns_pucca_house"] = True
    if re.search(r"\bcar\b|four[- ]wheeler|\bsuv\b|కారు", t) and not re.search(r"no car|don't (?:own|have) a car|taxi", t):
        d["owns_four_wheeler"] = True
    if re.search(r"income tax|file (?:my )?itr|pay (?:income )?tax|tax payer|taxpayer", t):
        d["income_tax_payer"] = not re.search(r"(?:not|don't|do not|never) (?:pay|file)|no income tax|not an? (?:income )?tax", t)
    if "auto_driver" in d["occupations"]:
        if re.search(r"own (?:an? |my )?(?:auto|taxi|cab|vehicle)|my (?:own )?(?:auto|taxi|cab)|సొంత ఆటో|अपना ऑटो|खुद का ऑटो", t):
            d["owns_commercial_vehicle"] = True
        elif re.search(r"rent(?:ed)? (?:an? )?(?:auto|taxi)|(?:auto|taxi) on rent|owner'?s (?:auto|taxi|car)|someone else'?s|"
                       r"belongs to (?:my |the |an? )?owner|not my own|on (?:a )?salary", t):
            d["owns_commercial_vehicle"] = False
    if re.search(r"start (?:a|my own|my|an?|our own) (?:[a-z-]+ ){0,3}(?:business|unit|shop|enterprise|venture|factory)|set up (?:a|my) (?:unit|business)|business idea|వ్యాపారం (?:ప్రారంభ|పెట్ట)|व्यवसाय शुरू|अपना काम", t):
        d["wants_to_start_business"] = True

    # ---- education
    student = "student" in d["occupations"]
    for lvl, pat in EDU_PATTERNS:
        if re.search(pat, ts):
            d["education_level"] = lvl
            break
    if student:
        d["is_student"] = True
    if re.search(r"illiterate|never went to school|no schooling|చదువు రాదు|अनपढ़", t):
        d["education_level"] = "none"
    # A parent describing a child's class should not set the parent's education.
    if not student and d.get("education_level") in ("primary",) and d.get("children_in_school"):
        d.pop("education_level")

    # ---- student details (scholarships / education loans)
    if student:
        if re.search(r"top 20|20 ?percentile|board topper|\b(?:9\d|100)\s*%[^.]{0,25}(?:inter|12th|class 12|board)|"
                     r"(?:inter|12th|class 12|board)[^.]{0,25}\b(?:9\d|100)\s*%", ts):
            d["class12_top20"] = True
        if re.search(r"\b(?:iit|nit|iiit|iiser|iisc|aiims|nirf|central university|state university|"
                     r"government (?:engineering )?college|govt\.? (?:engineering )?college|jntu|andhra university|"
                     r"\bsvu\b|osmania|\bau\b college)", ts):
            d["in_quality_institution"] = True
        if re.search(r"education loan|study loan|loan for (?:my )?(?:studies|education|fees|course)|విద్యా రుణం|शिक्षा ऋण|एजुकेशन लोन", t):
            d["wants_education_loan"] = not re.search(r"(?:no|don't need|do not need|without) (?:an? )?(?:education )?loan", t)
        if re.search(r"\b(?:1st|first) year\b|మొదటి సంవత్సరం|पहले (?:साल|वर्ष)", ts):
            d["first_year_of_course"] = True
        elif re.search(r"\b(?:2nd|3rd|4th|5th|second|third|fourth|fifth|final|last) year\b|చివరి సంవత్సరం|अंतिम वर्ष", ts):
            d["first_year_of_course"] = False
        if re.search(r"\bgate\b[^.]{0,20}(?:qualified|cleared|score|rank)|qualified (?:in )?gate|cleared gate", ts):
            d["gate_qualified"] = True
        if re.search(r"(?:already|currently) (?:get|getting|receive|receiving|have) (?:a |an )?scholarship", ts):
            d["other_scholarship"] = True

    prof = Profile.model_validate(d)
    return prof, notes
