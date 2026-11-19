# Faithfulness – engine: llm, generator: llm, model: groq openai/gpt-oss-20b

7 of 40 samples (**incomplete** – stopped at sample 8/40: Error code: 429 - {'error': {'message': 'Rate limit reached for model `openai/gpt-oss-20b` in organization `org_01kmr9d5g7frfbwmsdgyx16e7e` service tier `on_demand` on tokens per day (TPD): Limit 2000; re-run to resume)

| Set | Faithfulness | n |
|---|---|---|
| All | 0.953 | 7 |
| Scheme explanations | 0.953 | 7 |
| Free-form Q&A (EN/TE/HI) | nan | 0 |

## Lowest-scoring samples

- **p03:pm_internship** 0.77: Explain PM Internship Scheme to me and how to apply.
    - unsupported: The PM Internship Scheme is a government program that offers 12 months of work experience in a top‑500 company. (Official passage states "Paid 12-month internships in India's top companies" but does not specify top‑500.)
    - unsupported: Applicants must have passed 10th grade or higher and have professional education. (Passage states passed 10th or higher (including ITI, diploma, degree) but does not mention a professional education requirement.)
    - unsupported: Applicants must not be in full‑time employment; students are eligible. (Passage states not in full-time employment but does not explicitly state that students are eligible.)
- **p01:talliki_vandanam** 0.90: Explain Talliki Vandanam to me and how to apply.
    - unsupported: The ₹15,000 is credited to the mother’s bank account and ₹2,000 is allocated to the school maintenance fund. (Passage [3] states ₹13,000 is credited to the mother’s account and ₹2,000 goes to the school maintenance fund, not ₹15,000.)
- **p01:deepam_2** 1.00: Explain Deepam 2.0 – Free LPG Cylinders to me and how to apply.
- **p02:ntr_bharosa_widow** 1.00: Explain NTR Bharosa Pension – Widows to me and how to apply.
- **p02:ntr_bharosa_old_age** 1.00: Explain NTR Bharosa Pension – Old Age to me and how to apply.
