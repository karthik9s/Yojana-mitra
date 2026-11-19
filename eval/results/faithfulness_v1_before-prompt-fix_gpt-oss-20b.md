# Faithfulness – engine: llm, generator: llm, model: groq openai/gpt-oss-20b

40 of 40 samples

| Set | Faithfulness | n |
|---|---|---|
| All | 0.910 | 40 |
| Scheme explanations | 0.888 | 30 |
| Free-form Q&A (EN/TE/HI) | 0.975 | 10 |

## Lowest-scoring samples

- **p02:ntr_bharosa_old_age** 0.50: Explain NTR Bharosa Pension – Old Age to me and how to apply.
    - unsupported: You are 64 years old and live in a rural area of Andhra Pradesh. (Not stated in the context.)
    - unsupported: Your household income is ₹60 000 per year, which is ₹5 000 per month – below the ₹10 000 limit for rural families. (Not stated in the context.)
    - unsupported: Your land is 0 acres, well below the 3‑acre limit. (Not stated in the context.)
    - unsupported: These facts meet the main eligibility rules for the NTR Bharosa Pension – Old Age scheme. (Not stated in the context.)
    - unsupported: There is no government employee or pensioner in your family. (Not stated in the context.)
    - unsupported: You are not an income‑tax payer. (Not stated in the context.)
    - unsupported: You do not own a private four‑wheeler (taxis, tractors and autos are exempt). (Not stated in the context.)
- **p12:ntr_bharosa_transgender** 0.62: Explain NTR Bharosa Pension – Transgender Persons to me and how to apply.
    - unsupported: Eligibility requires the applicant to be 29 years old in the example. (Context specifies age 18 and above, no mention of 29.)
    - unsupported: The applicant’s monthly household income is ₹7,000, which is below the ₹12,000/month limit for urban areas. (Context gives income limits but does not provide applicant’s income.)
    - unsupported: The applicant does not own a private four‑wheeler. (Context lists no private four‑wheeler as a requirement, but does not state applicant’s ownership.)
- **p05:auto_driverla_sevalo** 0.67: Explain Auto Driverla Sevalo to me and how to apply.
    - unsupported: The Auto Driverla Sevalo scheme is for residents of Andhra Pradesh who own and drive a self‑owned auto, taxi or mini‑cab. (The context specifies residents of Andhra Pradesh who own and drive a self‑owned auto, taxi, or maxi‑cab, not mini‑cab.)
    - unsupported: Eligibility requires the vehicle to be registered in Andhra Pradesh, the applicant to have a valid driving licence and to be 31 years old. (The age requirement in the context is 18 or older, not 31.)
- **p07:ntr_bharosa_weavers** 0.75: Explain NTR Bharosa Pension – Handloom Weavers to me and how to apply.
    - unsupported: Eligibility requires the applicant to be 52 years old in the example. (Context specifies age 50 years or above, but does not mention 52 years.)
    - unsupported: Eligibility requires the applicant to live in a rural area of Andhra Pradesh. (Context gives different income limits for rural and urban but does not require rural residence.)
    - unsupported: Eligibility requires the applicant’s household income to be ₹80 000 per year, which is below the ₹10 000 per month limit for rural families. (Context states household income must be within ₹10,000/month (rural) or ₹12,000/month (urban); no mention of ₹80,000 per year.)
    - unsupported: Eligibility requires the applicant’s landholding to be 0 acres, below the 3‑acre wet‑land limit. (Context requires land below 3 acres wet / 10 acres dry, but does not specify 0 acres.)
- **q02** 0.75: How much money does Talliki Vandanam give per child?
    - unsupported: The ₹15,000 is credited to the mother’s account (The context specifies that ₹13,000 of the ₹15,000 is credited to the mother’s account, with the remaining ₹2,000 going to the school maintenance fund, so the entire amount is not credited to the mother.)
