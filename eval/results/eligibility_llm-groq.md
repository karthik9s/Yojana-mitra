# Eligibility evaluation – profiles.yaml – extractor: llm-groq, graph: in-memory graph (networkx)

50 hand-labelled profiles × 43 schemes · 606.0 s

| Metric | Precision | Recall | F1 |
|---|---|---|---|
| Micro (scheme-level) | 0.990 | 0.984 | 0.987 |
| Macro (per citizen) | 0.993 | 0.982 | – |
| Lenient (eligible + need-info) | 0.654 | 0.994 | 0.789 |

TP=311 FP=3 FN=5

## By language

| Lang | P | R | F1 |
|---|---|---|---|
| en | 0.992 | 0.992 | 0.992 |
| hi | 1.000 | 1.000 | 1.000 |
| te | 1.000 | 0.925 | 0.961 |
| te-en | 0.875 | 1.000 | 0.933 |

## Extraction field accuracy

| Field | Accuracy | n |
|---|---|---|
| marital_status | 0.88 | 8 |
| occupations | 0.92 | 37 |
| gender | 0.94 | 49 |
| age | 1.00 | 50 |
| state | 1.00 | 48 |
| area | 1.00 | 43 |
| land_acres | 1.00 | 21 |
| annual_income | 1.00 | 49 |
| children_in_school | 1.00 | 8 |

## Per scheme (worst F1 first)

| Scheme | P | R | TP | FP | FN |
|---|---|---|---|---|---|
| ntr_bharosa_cobblers | 1.00 | 0.00 | 0 | 0 | 1 |
| ntr_bharosa_weavers | 1.00 | 0.50 | 1 | 0 | 1 |
| auto_driverla_sevalo | 0.67 | 1.00 | 2 | 1 | 0 |
| ntr_bharosa_widow | 1.00 | 0.67 | 2 | 0 | 1 |
| pm_internship | 1.00 | 0.83 | 5 | 0 | 1 |
| pm_sym | 0.91 | 1.00 | 10 | 1 | 0 |
| stree_shakti | 1.00 | 0.96 | 22 | 0 | 1 |
| vb_g_ram_g | 0.96 | 1.00 | 27 | 1 | 0 |
| ab_pmjay_vay_vandana | 1.00 | 1.00 | 2 | 0 | 0 |
| annadata_sukhibhava | 1.00 | 1.00 | 6 | 0 | 0 |
| ap_fee_reimbursement | 1.00 | 1.00 | 4 | 0 | 0 |
| atal_pension_yojana | 1.00 | 1.00 | 25 | 0 | 0 |
| deepam_2 | 1.00 | 1.00 | 5 | 0 | 0 |
| kisan_credit_card | 1.00 | 1.00 | 10 | 0 | 0 |
| matsyakara_sevalo | 1.00 | 1.00 | 1 | 0 | 0 |
| ntr_bharosa_chronic_illness | 1.00 | 1.00 | 1 | 0 | 0 |
| ntr_bharosa_disabled | 1.00 | 1.00 | 2 | 0 | 0 |
| ntr_bharosa_fishermen | 1.00 | 1.00 | 1 | 0 | 0 |
| ntr_bharosa_old_age | 1.00 | 1.00 | 7 | 0 | 0 |
| ntr_bharosa_single_women | 1.00 | 1.00 | 2 | 0 | 0 |
| ntr_bharosa_toddy_tappers | 1.00 | 1.00 | 1 | 0 | 0 |
| ntr_bharosa_transgender | 1.00 | 1.00 | 1 | 0 | 0 |
| ntr_vaidya_seva | 1.00 | 1.00 | 47 | 0 | 0 |
| pm_kisan | 1.00 | 1.00 | 6 | 0 | 0 |
| pm_kisan_maandhan | 1.00 | 1.00 | 3 | 0 | 0 |
| pm_svanidhi | 1.00 | 1.00 | 2 | 0 | 0 |
| pm_ujjwala | 1.00 | 1.00 | 3 | 0 | 0 |
| pm_vishwakarma | 1.00 | 1.00 | 4 | 0 | 0 |
| pmay_gramin | 1.00 | 1.00 | 2 | 0 | 0 |
| pmay_urban | 1.00 | 1.00 | 3 | 0 | 0 |
| pmegp | 1.00 | 1.00 | 2 | 0 | 0 |
| pmfby | 1.00 | 1.00 | 7 | 0 | 0 |
| pmjjby | 1.00 | 1.00 | 35 | 0 | 0 |
| pmmvy | 1.00 | 1.00 | 4 | 0 | 0 |
| pmsby | 1.00 | 1.00 | 48 | 0 | 0 |
| sukanya_samriddhi | 1.00 | 1.00 | 3 | 0 | 0 |
| talliki_vandanam | 1.00 | 1.00 | 5 | 0 | 0 |

## Errors

- **p02** (te) FP=[] FN=['ntr_bharosa_widow', 'stree_shakti'] fields={"gender": {"gold": "female", "pred": null}}
- **p07** (te) FP=[] FN=['ntr_bharosa_weavers'] fields={"gender": {"gold": "male", "pred": null}, "occupations": {"gold": ["weaver"], "pred": ["agricultural_labourer"]}}
- **p08** (en) FP=[] FN=[] fields={"marital_status": {"gold": "married", "pred": null}}
- **p22** (hi) FP=[] FN=[] fields={"gender": {"gold": "male", "pred": null}}
- **p32** (en) FP=[] FN=['ntr_bharosa_cobblers'] fields={"occupations": {"gold": ["cobbler"], "pred": ["artisan"]}}
- **p39** (te-en) FP=['vb_g_ram_g'] FN=[] fields={}
- **p41** (en) FP=[] FN=['pm_internship'] fields={"occupations": {"gold": ["unemployed"], "pred": []}}
- **p42** (en) FP=['pm_sym'] FN=[] fields={}
- **p46** (en) FP=['auto_driverla_sevalo'] FN=[] fields={}
