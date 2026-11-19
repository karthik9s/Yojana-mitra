# Eligibility evaluation – profiles.yaml – extractor: rules, graph: in-memory graph (networkx)

50 hand-labelled profiles × 43 schemes · 0.2 s

| Metric | Precision | Recall | F1 |
|---|---|---|---|
| Micro (scheme-level) | 0.997 | 1.000 | 0.998 |
| Macro (per citizen) | 0.998 | 1.000 | – |
| Lenient (eligible + need-info) | 0.544 | 1.000 | 0.705 |

TP=316 FP=1 FN=0

## By language

| Lang | P | R | F1 |
|---|---|---|---|
| en | 0.996 | 1.000 | 0.998 |
| hi | 1.000 | 1.000 | 1.000 |
| te | 1.000 | 1.000 | 1.000 |
| te-en | 1.000 | 1.000 | 1.000 |

## Extraction field accuracy

| Field | Accuracy | n |
|---|---|---|
| age | 1.00 | 50 |
| gender | 1.00 | 49 |
| state | 1.00 | 48 |
| area | 1.00 | 43 |
| occupations | 1.00 | 37 |
| land_acres | 1.00 | 21 |
| annual_income | 1.00 | 49 |
| children_in_school | 1.00 | 8 |
| marital_status | 1.00 | 8 |

## Per scheme (worst F1 first)

| Scheme | P | R | TP | FP | FN |
|---|---|---|---|---|---|
| pm_sym | 0.91 | 1.00 | 10 | 1 | 0 |
| ab_pmjay_vay_vandana | 1.00 | 1.00 | 2 | 0 | 0 |
| annadata_sukhibhava | 1.00 | 1.00 | 6 | 0 | 0 |
| ap_fee_reimbursement | 1.00 | 1.00 | 4 | 0 | 0 |
| atal_pension_yojana | 1.00 | 1.00 | 25 | 0 | 0 |
| auto_driverla_sevalo | 1.00 | 1.00 | 2 | 0 | 0 |
| deepam_2 | 1.00 | 1.00 | 5 | 0 | 0 |
| kisan_credit_card | 1.00 | 1.00 | 10 | 0 | 0 |
| matsyakara_sevalo | 1.00 | 1.00 | 1 | 0 | 0 |
| ntr_bharosa_chronic_illness | 1.00 | 1.00 | 1 | 0 | 0 |
| ntr_bharosa_cobblers | 1.00 | 1.00 | 1 | 0 | 0 |
| ntr_bharosa_disabled | 1.00 | 1.00 | 2 | 0 | 0 |
| ntr_bharosa_fishermen | 1.00 | 1.00 | 1 | 0 | 0 |
| ntr_bharosa_old_age | 1.00 | 1.00 | 7 | 0 | 0 |
| ntr_bharosa_single_women | 1.00 | 1.00 | 2 | 0 | 0 |
| ntr_bharosa_toddy_tappers | 1.00 | 1.00 | 1 | 0 | 0 |
| ntr_bharosa_transgender | 1.00 | 1.00 | 1 | 0 | 0 |
| ntr_bharosa_weavers | 1.00 | 1.00 | 2 | 0 | 0 |
| ntr_bharosa_widow | 1.00 | 1.00 | 3 | 0 | 0 |
| ntr_vaidya_seva | 1.00 | 1.00 | 47 | 0 | 0 |
| pm_internship | 1.00 | 1.00 | 6 | 0 | 0 |
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
| stree_shakti | 1.00 | 1.00 | 23 | 0 | 0 |
| sukanya_samriddhi | 1.00 | 1.00 | 3 | 0 | 0 |
| talliki_vandanam | 1.00 | 1.00 | 5 | 0 | 0 |
| vb_g_ram_g | 1.00 | 1.00 | 27 | 0 | 0 |

## Errors

- **p42** (en) FP=['pm_sym'] FN=[] fields={}
