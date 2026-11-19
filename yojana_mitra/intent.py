"""What is the citizen actually looking for?

Eligibility answers "what CAN you get"; intent answers "what did you ASK for". A student asking
about fee reimbursement should see scholarships first, not gas cylinders and insurance, even if
they technically qualify for those too.

Focus comes from explicit request words (EN / TE / HI) or, failing that, from the profile
(a current student is focused on education).
"""
from __future__ import annotations

import re

from .profile import Profile

# Strong keywords: their presence alone signals the request.
STRONG = {
    "education": r"scholarship|fee ?reimburse|reimbursement|tuition|education loan|study loan|hostel fee|"
                 r"exam fee|fees?\b|internship|vidya|jnanabhumi|స్కాలర్‌?షిప్|ఉపకార వేతన|ఫీజు|"
                 r"छात्रवृत्ति|स्कॉलरशिप|फीस|शिक्षा ऋण",
    "health": r"hospital|treatment|surgery|operation|medical (?:help|bill|expense)|health (?:card|insurance|scheme)|"
              r"aarogyasri|vaidya seva|ఆసుపత్రి|వైద్యం|చికిత్స|अस्पताल|इलाज",
    "housing": r"housing scheme|house scheme|build (?:a |my )?house|house site|awas|ఇంటి స్థలం|ఇల్లు కట్ట|आवास योजना|घर बनाना",
    "agriculture": r"crop insurance|crop loan|fertili[sz]er|seeds?\b|investment support|rythu bharosa|annadata|"
                   r"పంట (?:బీమా|రుణం)|पीएम किसान|फसल बीमा",
    "pension": r"\bpension\b|పింఛను|పెన్షన్|पेंशन",
    "livelihood": r"business loan|self[- ]employment|start (?:a|my own) (?:business|unit)|\bjob\b|employment|"
                  r"ఉపాధి|ఉద్యోగం|रोजगार|नौकरी",
    "women": r"women'?s scheme|scheme for women|మహిళా పథకం|महिला योजना",
}
LABELS = {
    "education": {"en": "your studies", "te": "మీ చదువు", "hi": "आपकी पढ़ाई"},
    "health": {"en": "health care", "te": "ఆరోగ్యం", "hi": "स्वास्थ्य"},
    "housing": {"en": "housing", "te": "ఇల్లు", "hi": "आवास"},
    "agriculture": {"en": "farming", "te": "వ్యవసాయం", "hi": "खेती"},
    "pension": {"en": "pensions", "te": "పింఛన్లు", "hi": "पेंशन"},
    "livelihood": {"en": "jobs & livelihood", "te": "ఉపాధి", "hi": "रोज़गार"},
    "women": {"en": "women", "te": "మహిళలు", "hi": "महिलाएँ"},
}
# Categories that count as matching a focus.
FOCUS_CATEGORIES = {
    "education": {"education"},
    "health": {"health", "insurance"},
    "housing": {"housing"},
    "agriculture": {"agriculture"},
    "pension": {"pension"},
    "livelihood": {"livelihood"},
    "women": {"women"},
}


def detect_focus(text: str, profile: Profile) -> dict:
    t = (text or "").lower()
    found = [k for k, pat in STRONG.items() if re.search(pat, t)]
    reason = "asked"
    if not found and (profile.is_student or "student" in profile.occupations):
        found, reason = ["education"], "student"
    cats: set[str] = set()
    for f in found:
        cats |= FOCUS_CATEGORIES[f]
    return {"topics": found, "categories": sorted(cats), "reason": reason if found else None,
            "labels": {f: LABELS[f] for f in found}}
