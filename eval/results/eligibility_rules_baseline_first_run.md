# Eligibility evaluation – extractor: rules, graph: in-memory graph (networkx)

50 hand-labelled profiles × 37 schemes · 0.2 s

| Metric | Precision | Recall | F1 |
|---|---|---|---|
| Micro (scheme-level) | 0.997 | 0.934 | 0.964 |
| Macro (per citizen) | 0.998 | 0.938 | – |
| Lenient (eligible + need-info) | 0.529 | 0.965 | 0.683 |

TP=295 FP=1 FN=21

## By language

| Lang | P | R | F1 |
|---|---|---|---|
| en | 0.996 | 0.967 | 0.981 |
| hi | 1.000 | 1.000 | 1.000 |
| te | 1.000 | 0.775 | 0.873 |
| te-en | 1.000 | 0.429 | 0.600 |

## Extraction field accuracy

| Field | Accuracy | n |
|---|---|---|
| children_in_school | 0.75 | 8 |
| gender | 0.92 | 49 |
| occupations | 0.92 | 37 |
| age | 0.96 | 50 |
| state | 1.00 | 48 |
| area | 1.00 | 43 |
| land_acres | 1.00 | 21 |
| annual_income | 1.00 | 49 |
| marital_status | 1.00 | 8 |

## Per scheme (worst F1 first)

| Scheme | P | R | TP | FP | FN |
|---|---|---|---|---|---|
| pmegp | 1.00 | 0.00 | 0 | 0 | 2 |
| auto_driverla_sevalo | 1.00 | 0.50 | 1 | 0 | 1 |
| ntr_bharosa_weavers | 1.00 | 0.50 | 1 | 0 | 1 |
| talliki_vandanam | 1.00 | 0.60 | 3 | 0 | 2 |
| pm_ujjwala | 1.00 | 0.67 | 2 | 0 | 1 |
| ap_fee_reimbursement | 1.00 | 0.75 | 3 | 0 | 1 |
| pmmvy | 1.00 | 0.75 | 3 | 0 | 1 |
| pm_sym | 0.90 | 0.90 | 9 | 1 | 1 |
| annadata_sukhibhava | 1.00 | 0.83 | 5 | 0 | 1 |
| pm_internship | 1.00 | 0.83 | 5 | 0 | 1 |
| pm_kisan | 1.00 | 0.83 | 5 | 0 | 1 |
| pmfby | 1.00 | 0.86 | 6 | 0 | 1 |
| kisan_credit_card | 1.00 | 0.90 | 9 | 0 | 1 |
| vb_g_ram_g | 1.00 | 0.93 | 25 | 0 | 2 |
| pmsby | 1.00 | 0.96 | 46 | 0 | 2 |
| atal_pension_yojana | 1.00 | 0.96 | 24 | 0 | 1 |
| pmjjby | 1.00 | 0.97 | 34 | 0 | 1 |
| ab_pmjay_vay_vandana | 1.00 | 1.00 | 2 | 0 | 0 |
| deepam_2 | 1.00 | 1.00 | 5 | 0 | 0 |
| matsyakara_sevalo | 1.00 | 1.00 | 1 | 0 | 0 |
| ntr_bharosa_chronic_illness | 1.00 | 1.00 | 1 | 0 | 0 |
| ntr_bharosa_cobblers | 1.00 | 1.00 | 1 | 0 | 0 |
| ntr_bharosa_disabled | 1.00 | 1.00 | 2 | 0 | 0 |
| ntr_bharosa_fishermen | 1.00 | 1.00 | 1 | 0 | 0 |
| ntr_bharosa_old_age | 1.00 | 1.00 | 7 | 0 | 0 |
| ntr_bharosa_single_women | 1.00 | 1.00 | 2 | 0 | 0 |
| ntr_bharosa_toddy_tappers | 1.00 | 1.00 | 1 | 0 | 0 |
| ntr_bharosa_transgender | 1.00 | 1.00 | 1 | 0 | 0 |
| ntr_bharosa_widow | 1.00 | 1.00 | 3 | 0 | 0 |
| ntr_vaidya_seva | 1.00 | 1.00 | 47 | 0 | 0 |
| pm_kisan_maandhan | 1.00 | 1.00 | 3 | 0 | 0 |
| pm_svanidhi | 1.00 | 1.00 | 2 | 0 | 0 |
| pm_vishwakarma | 1.00 | 1.00 | 4 | 0 | 0 |
| pmay_gramin | 1.00 | 1.00 | 2 | 0 | 0 |
| pmay_urban | 1.00 | 1.00 | 3 | 0 | 0 |
| stree_shakti | 1.00 | 1.00 | 23 | 0 | 0 |
| sukanya_samriddhi | 1.00 | 1.00 | 3 | 0 | 0 |

## Errors

- **p01** (en) FP=[] FN=['talliki_vandanam'] fields={"children_in_school": {"gold": 2, "pred": null}}
- **p04** (hi) FP=[] FN=[] fields={"gender": {"gold": "male", "pred": null}}
- **p05** (en) FP=[] FN=['auto_driverla_sevalo', 'pm_sym'] fields={"occupations": {"gold": ["auto_driver"], "pred": []}}
- **p07** (te) FP=[] FN=['ntr_bharosa_weavers', 'pmsby', 'vb_g_ram_g'] fields={"age": {"gold": 52, "pred": 2}, "gender": {"gold": "male", "pred": null}}
- **p15** (en) FP=[] FN=['talliki_vandanam'] fields={"children_in_school": {"gold": 1, "pred": null}}
- **p19** (en) FP=[] FN=['pmegp'] fields={}
- **p22** (hi) FP=[] FN=[] fields={"gender": {"gold": "male", "pred": null}}
- **p23** (en) FP=[] FN=['ap_fee_reimbursement', 'pm_internship'] fields={"occupations": {"gold": ["student"], "pred": []}}
- **p39** (te-en) FP=[] FN=['annadata_sukhibhava', 'kisan_credit_card', 'pm_kisan', 'pmfby'] fields={"occupations": {"gold": ["farmer"], "pred": []}}
- **p42** (en) FP=['pm_sym'] FN=['pmegp'] fields={}
- **p45** (te) FP=[] FN=['atal_pension_yojana', 'pm_ujjwala', 'pmjjby', 'pmmvy', 'pmsby', 'vb_g_ram_g'] fields={"age": {"gold": 29, "pred": 9}}
- **p49** (hi) FP=[] FN=[] fields={"gender": {"gold": "male", "pred": null}}
