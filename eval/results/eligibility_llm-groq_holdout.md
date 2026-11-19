# Eligibility evaluation – profiles_holdout.yaml – extractor: llm-groq, graph: in-memory graph (networkx)

15 hand-labelled profiles × 43 schemes · 68.7 s

| Metric | Precision | Recall | F1 |
|---|---|---|---|
| Micro (scheme-level) | 0.978 | 0.958 | 0.968 |
| Macro (per citizen) | 0.977 | 0.964 | – |
| Lenient (eligible + need-info) | 0.676 | 0.968 | 0.797 |

TP=91 FP=2 FN=4

## By language

| Lang | P | R | F1 |
|---|---|---|---|
| en | 0.966 | 0.934 | 0.950 |
| hi | 1.000 | 1.000 | 1.000 |
| te | 1.000 | 1.000 | 1.000 |

## Extraction field accuracy

| Field | Accuracy | n |
|---|---|---|
| occupations | 0.88 | 8 |
| gender | 0.92 | 13 |
| state | 0.92 | 13 |
| age | 1.00 | 15 |
| area | 1.00 | 12 |
| marital_status | 1.00 | 3 |
| annual_income | 1.00 | 15 |
| children_in_school | 1.00 | 4 |
| land_acres | 1.00 | 6 |

## Per scheme (worst F1 first)

| Scheme | P | R | TP | FP | FN |
|---|---|---|---|---|---|
| ntr_bharosa_cobblers | 1.00 | 0.00 | 0 | 0 | 1 |
| ntr_bharosa_single_women | 1.00 | 0.00 | 0 | 0 | 1 |
| pm_sym | 0.50 | 0.50 | 1 | 1 | 1 |
| talliki_vandanam | 1.00 | 0.75 | 3 | 0 | 1 |
| ntr_vaidya_seva | 0.93 | 1.00 | 14 | 1 | 0 |
| aicte_pragati | 1.00 | 1.00 | 1 | 0 | 0 |
| annadata_sukhibhava | 1.00 | 1.00 | 1 | 0 | 0 |
| ap_fee_reimbursement | 1.00 | 1.00 | 1 | 0 | 0 |
| atal_pension_yojana | 1.00 | 1.00 | 9 | 0 | 0 |
| deepam_2 | 1.00 | 1.00 | 1 | 0 | 0 |
| kisan_credit_card | 1.00 | 1.00 | 2 | 0 | 0 |
| matsyakara_sevalo | 1.00 | 1.00 | 1 | 0 | 0 |
| ntr_bharosa_chronic_illness | 1.00 | 1.00 | 1 | 0 | 0 |
| ntr_bharosa_old_age | 1.00 | 1.00 | 2 | 0 | 0 |
| ntr_bharosa_widow | 1.00 | 1.00 | 2 | 0 | 0 |
| pm_internship | 1.00 | 1.00 | 2 | 0 | 0 |
| pm_kisan | 1.00 | 1.00 | 1 | 0 | 0 |
| pm_ujjwala | 1.00 | 1.00 | 2 | 0 | 0 |
| pm_vishwakarma | 1.00 | 1.00 | 2 | 0 | 0 |
| pmay_gramin | 1.00 | 1.00 | 1 | 0 | 0 |
| pmay_urban | 1.00 | 1.00 | 2 | 0 | 0 |
| pmfby | 1.00 | 1.00 | 1 | 0 | 0 |
| pmjjby | 1.00 | 1.00 | 11 | 0 | 0 |
| pmmvy | 1.00 | 1.00 | 1 | 0 | 0 |
| pmsby | 1.00 | 1.00 | 15 | 0 | 0 |
| stree_shakti | 1.00 | 1.00 | 8 | 0 | 0 |
| vb_g_ram_g | 1.00 | 1.00 | 6 | 0 | 0 |

## Errors

- **h02** (te) FP=[] FN=[] fields={"gender": {"gold": "male", "pred": null}}
- **h05** (en) FP=['pm_sym'] FN=[] fields={}
- **h10** (en) FP=['ntr_vaidya_seva'] FN=[] fields={"state": {"gold": "Telangana", "pred": "Andhra Pradesh"}}
- **h13** (en) FP=[] FN=['ntr_bharosa_cobblers'] fields={"occupations": {"gold": ["cobbler"], "pred": ["artisan"]}}
- **h15** (en) FP=[] FN=['ntr_bharosa_single_women', 'pm_sym', 'talliki_vandanam'] fields={}
