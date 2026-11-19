# Eligibility evaluation – profiles_holdout.yaml – extractor: rules, graph: in-memory graph (networkx)

15 hand-labelled profiles × 43 schemes · 0.2 s

| Metric | Precision | Recall | F1 |
|---|---|---|---|
| Micro (scheme-level) | 0.986 | 0.726 | 0.836 |
| Macro (per citizen) | 0.983 | 0.748 | – |
| Lenient (eligible + need-info) | 0.422 | 1.000 | 0.594 |

TP=69 FP=1 FN=26

## By language

| Lang | P | R | F1 |
|---|---|---|---|
| en | 0.975 | 0.639 | 0.772 |
| hi | 1.000 | 1.000 | 1.000 |
| te | 1.000 | 0.800 | 0.889 |

## Extraction field accuracy

| Field | Accuracy | n |
|---|---|---|
| children_in_school | 0.50 | 4 |
| age | 0.67 | 15 |
| gender | 0.77 | 13 |
| occupations | 0.88 | 8 |
| area | 0.92 | 12 |
| state | 0.92 | 13 |
| marital_status | 1.00 | 3 |
| annual_income | 1.00 | 15 |
| land_acres | 1.00 | 6 |

## Per scheme (worst F1 first)

| Scheme | P | R | TP | FP | FN |
|---|---|---|---|---|---|
| aicte_pragati | 1.00 | 0.00 | 0 | 0 | 1 |
| ap_fee_reimbursement | 1.00 | 0.00 | 0 | 0 | 1 |
| ntr_bharosa_single_women | 1.00 | 0.00 | 0 | 0 | 1 |
| pm_internship | 1.00 | 0.00 | 0 | 0 | 2 |
| pm_sym | 1.00 | 0.00 | 0 | 0 | 2 |
| ntr_bharosa_widow | 1.00 | 0.50 | 1 | 0 | 1 |
| pm_vishwakarma | 1.00 | 0.50 | 1 | 0 | 1 |
| pmay_urban | 1.00 | 0.50 | 1 | 0 | 1 |
| talliki_vandanam | 1.00 | 0.50 | 2 | 0 | 2 |
| atal_pension_yojana | 1.00 | 0.67 | 6 | 0 | 3 |
| pmsby | 1.00 | 0.67 | 10 | 0 | 5 |
| pmjjby | 1.00 | 0.73 | 8 | 0 | 3 |
| stree_shakti | 1.00 | 0.75 | 6 | 0 | 2 |
| vb_g_ram_g | 1.00 | 0.83 | 5 | 0 | 1 |
| ntr_vaidya_seva | 0.93 | 1.00 | 14 | 1 | 0 |
| annadata_sukhibhava | 1.00 | 1.00 | 1 | 0 | 0 |
| deepam_2 | 1.00 | 1.00 | 1 | 0 | 0 |
| kisan_credit_card | 1.00 | 1.00 | 2 | 0 | 0 |
| matsyakara_sevalo | 1.00 | 1.00 | 1 | 0 | 0 |
| ntr_bharosa_chronic_illness | 1.00 | 1.00 | 1 | 0 | 0 |
| ntr_bharosa_cobblers | 1.00 | 1.00 | 1 | 0 | 0 |
| ntr_bharosa_old_age | 1.00 | 1.00 | 2 | 0 | 0 |
| pm_kisan | 1.00 | 1.00 | 1 | 0 | 0 |
| pm_ujjwala | 1.00 | 1.00 | 2 | 0 | 0 |
| pmay_gramin | 1.00 | 1.00 | 1 | 0 | 0 |
| pmfby | 1.00 | 1.00 | 1 | 0 | 0 |
| pmmvy | 1.00 | 1.00 | 1 | 0 | 0 |

## Errors

- **h01** (en) FP=[] FN=['ntr_bharosa_widow', 'pm_vishwakarma', 'pmsby'] fields={"age": {"gold": 58, "pred": null}}
- **h03** (en) FP=[] FN=['atal_pension_yojana', 'pm_internship', 'pmjjby', 'pmsby'] fields={"age": {"gold": 21, "pred": null}, "occupations": {"gold": ["student"], "pred": []}}
- **h05** (en) FP=[] FN=['talliki_vandanam'] fields={"children_in_school": {"gold": 1, "pred": null}}
- **h06** (en) FP=[] FN=['pmsby'] fields={"age": {"gold": 64, "pred": null}}
- **h08** (te) FP=[] FN=['aicte_pragati', 'ap_fee_reimbursement', 'pm_internship', 'stree_shakti'] fields={"gender": {"gold": "female", "pred": null}}
- **h09** (en) FP=[] FN=['atal_pension_yojana', 'pm_sym', 'pmjjby', 'pmsby', 'stree_shakti', 'vb_g_ram_g'] fields={"age": {"gold": 31, "pred": null}, "gender": {"gold": "female", "pred": null}}
- **h10** (en) FP=['ntr_vaidya_seva'] FN=[] fields={"state": {"gold": "Telangana", "pred": "Andhra Pradesh"}}
- **h11** (hi) FP=[] FN=[] fields={"gender": {"gold": "male", "pred": null}}
- **h14** (te) FP=[] FN=[] fields={"area": {"gold": "urban", "pred": null}}
- **h15** (en) FP=[] FN=['atal_pension_yojana', 'ntr_bharosa_single_women', 'pm_sym', 'pmay_urban', 'pmjjby', 'pmsby', 'talliki_vandanam'] fields={"age": {"gold": 38, "pred": null}, "children_in_school": {"gold": 1, "pred": null}}
