# Yojana Mitra · యోజన మిత్ర

**Government scheme eligibility finder for Andhra Pradesh: Graph RAG over a scheme knowledge graph.**

A citizen describes themselves in their own words, in English, Telugu, Hindi or a mix, typed or spoken.
Yojana Mitra extracts a structured profile, queries a knowledge graph of
`(Scheme)-[:REQUIRES]->(Criterion)` to find matching schemes, and explains each match (benefits,
documents, how to apply) from retrieved guideline text, with citations.

```
"I'm a 45-year-old woman farmer in a village near Guntur with 2 acres..."
        │
        ▼  1. Extract profile ── Claude structured output (or offline rules: EN / TE / HI)
{age: 45, gender: female, state: AP, area: rural, occupations: [farmer], land_acres: 2, ...}
        │  + derived facts: ap_resident, income_within_ap_limit, land_within_ap_limit ...
        ▼  2. Graph match ── one Cypher query (Neo4j) or the same logic on an in-memory graph
eligible: Talliki Vandanam, Annadata Sukhibhava, PM-KISAN, Stree Shakti, Deepam 2.0 ...
need info: Widow pension (marital status?)  →  follow-up questions, ranked by schemes unlocked
        ▼  3. RAG explain ── hybrid retrieval (multilingual-e5 + TF-IDF, RRF) → Claude, cited [n]
"Why you qualify / What you get / Documents / How to apply" in English, Telugu or Hindi
```

**Project page:** https://yojana-mitra-ihwk.netlify.app/ (screenshots, features, results) · **Live app:** https://yojana-mitra-2gbc.onrender.com

New to the code? Open [docs/explainer.html](docs/explainer.html) in a browser for a step-by-step visual walkthrough with a live matching demo, a pitch and interview practice.

## What makes it work

| Piece | Design |
|---|---|
| **Knowledge base** | [data/schemes.yaml](data/schemes.yaml): 43 schemes (18 AP state, 25 central) with benefits, documents, steps, portals, sources and machine-readable criteria. Reviewed Nov 2026 (NTR Bharosa pensions, Talliki Vandanam, Annadata Sukhibhava, Stree Shakti, Deepam 2.0, Auto Driverla Sevalo, Matsyakarula Sevalo, Universal Health Policy, VB-G RAM G, which replaced MGNREGA on 1 July 2026, plus college scholarships and education-loan schemes: CSSS, PM Vidyalaxmi, CSIS, AICTE Pragati/Saksham/PG). Contributory schemes like Atal Pension Yojana are labelled *retirement savings*, not welfare pensions. |
| **Graph** | 43 `Scheme` + 71 `Criterion` nodes, 195 `REQUIRES` edges. Identical conditions are *shared* nodes (e.g. "AP resident" links 18 schemes). OR-conditions are edge groups, so each scheme is a formula in conjunctive normal form. |
| **Focus on what was asked** | [intent.py](yojana_mitra/intent.py) detects the topic the citizen asked about (scholarships, fees, pension, hospital, housing, farming, jobs… in EN/TE/HI), or infers it (students → education). Those schemes and their questions come first, and everything else they qualify for is collapsed under "You also qualify for". |
| **Tri-state matching** | Each criterion is *met* (1), *unknown* (0) or *not met* (−1). Groups are OR = max and schemes are AND = min. Unknown facts don't silently fail: they produce **follow-up questions**, ranked by how many schemes they would unlock. Standard exclusions (govt employee, income-tax payer, car) are `assume`d and shown as "please confirm". |
| **Two graph backends** | `MATCH_CYPHER` in [graph.py](yojana_mitra/graph.py) runs in Neo4j. `MemoryGraph` (networkx) runs the same semantics, so the app and evals work with no database. |
| **Extraction** | Claude (`claude-opus-5-5`, JSON-schema structured output) when `ANTHROPIC_API_KEY` is set. Otherwise a rule-based extractor for English, Telugu and Hindi (amounts in lakh/k/per month, acres/cents/hectares, AP districts, relatives vs. speaker). |
| **Retrieval** | Section-level chunks per scheme plus any PDFs in `data/pdfs/`. Dense: `intfloat/multilingual-e5-small` (Telugu and Hindi queries work). Sparse: word + char-n-gram TF-IDF. Fused with Reciprocal Rank Fusion. Chroma when available, otherwise in-memory vectors. |
| **Generation** | Claude answers **only from retrieved passages**, cites `[n]`, and writes in the user's language. Offline it falls back to template/extractive answers built from the same passages. |
| **UI** | Single page, no build step: EN/తెలుగు/हिंदी, voice input (Web Speech API: te-IN / hi-IN / en-IN), editable profile, one-tap follow-ups, cited explanations, Q&A, dark mode, mobile layout. |

## Run it

```bash
pip install -r requirements.txt
```

```bash
python -m uvicorn yojana_mitra.api:app --port 8000
```

Open http://localhost:8000. With no key it runs fully offline. For AI extraction and Telugu/Hindi
answers, copy `.env.example` to `.env` and set `ANTHROPIC_API_KEY`.

**Deploy on Render (free plan):** the repo includes [render.yaml](render.yaml). In Render choose
New → Blueprint, pick this repository, and paste your `GROQ_API_KEY` when asked. It installs the slim
[requirements-render.txt](requirements-render.txt) and runs with `YM_DENSE=off` (about 150 MB RAM instead
of loading PyTorch): retrieval is TF-IDF only, and Telugu/Hindi questions are translated to English by the
LLM before searching. Free instances sleep after 15 minutes idle, so the first request after that takes
about a minute.

**Neo4j (optional):**

```bash
docker compose up -d neo4j
```

Then set `NEO4J_URI=bolt://localhost:7687` and `NEO4J_PASSWORD=yojanamitra` in `.env`, and run:

```bash
python scripts/load_neo4j.py
```

The app uses Neo4j automatically when `NEO4J_URI` is set, and falls back to the in-memory graph if it is unreachable.

## Evaluation

```bash
python -m eval.run_eval
```

```bash
python -m eval.run_eval --file profiles_holdout.yaml
```

```bash
python -m eval.faithfulness --engine lexical
```

Add `--llm` to `run_eval` for the Claude extractor. Use `--engine claude` or `--engine ragas` for real faithfulness scoring (needs a key).

**Data.** [eval/profiles.yaml](eval/profiles.yaml) holds 50 synthetic citizens (39 English, 6 Telugu, 4 Hindi, 1 romanised Telugu), with the eligible schemes hand-labelled against the rules (labelling convention at the top of the file). [eval/profiles_holdout.yaml](eval/profiles_holdout.yaml) holds 15 more, written *after* tuning and scored once.

**Results: offline rule-based extractor, in-memory graph** (full reports in [eval/results/](eval/results/))

| Set | Precision | Recall | F1 |
|---|---|---|---|
| 50 profiles, first run, before any extractor fixes | 0.997 | 0.934 | 0.964 |
| 50 profiles, after fixing extractor bugs found on this set | 0.997 | 1.000 | 0.998 |
| 15 held-out profiles (untuned), rules | 0.986 | 0.726 | 0.836 |

**Groq LLM extractor** (`openai/gpt-oss-120b`, `python -m eval.run_eval --llm`):

| Set | Precision | Recall | F1 |
|---|---|---|---|
| 50 profiles | 0.990 | 0.984 | 0.987 |
| **15 held-out profiles** | **0.978** | **0.958** | **0.968** |

The held-out rules row is 0.726 rather than the 0.734 measured earlier because one label was corrected: AICTE Pragati was added to the knowledge base after the holdout labels were written, and h08 qualifies for it.

How to read this:
- The **held-out row is the honest estimate** for the offline extractor. The 50-profile set was used to fix extractor bugs, so its post-fix score is optimistic.
- **Precision stays near 1.0 everywhere.** The graph rules almost never recommend a wrong scheme. The one false positive (p42) comes from "start a dairy business" being read as the person already being a dairy farmer.
- **Every recall loss is an extraction miss**, not a matching error. Examples: "Widow, 58" and "I'm the wife, 31" (age with no "years"), a Hindi income written as "आमदनी 4000 रुपये महीना", and Telugu "అమ్మాయిని" (girl). A missed fact moves a scheme to "need info" and triggers a follow-up question instead of a wrong answer: lenient recall (eligible + need-info) is 1.000 on both sets.
- The LLM extractor closes exactly this gap: held-out recall goes from 0.726 (rules) to 0.958 (Groq) while precision stays above 0.97. Its remaining misses are mostly occupation granularity (a cobbler tagged only as "artisan"), and it occasionally leaves gender empty in Telugu/Hindi texts.

**Faithfulness.** [eval/faithfulness.py](eval/faithfulness.py) builds 40 samples: 30 scheme explanations plus 10 free-form questions (EN/TE/HI). It has three engines:
- `ragas`: the RAGAS `Faithfulness` metric with Claude as judge.
- `claude`: the same claim-decomposition and verification algorithm, written directly against the Anthropic SDK.
- `lexical`: an offline word-overlap proxy, currently 1.000 on all 40 samples. Offline answers are copied from the retrieved passages, so this mostly confirms the plumbing. It can't detect paraphrased hallucinations, so treat it as a smoke test.
- **`llm` (RAGAS-style claim checking), Groq `openai/gpt-oss-20b` generating and judging: 0.910 overall** (scheme explanations 0.888, free-form Q&A in EN/TE/HI 0.975), with 325 of 366 claims supported. Of the 41 unsupported claims:
  - ~20 are rule mix-ups: the person's own value is restated as the scheme rule (e.g. "eligibility requires age 52" when the rule is 50+), and twice requirements were invented.
  - ~10 restate the citizen's own facts, which the model is given separately from the passages.
  - 4 state an assumed condition ("no government employee in the family") as a fact.
  - A few are real factual slips, e.g. "the full ₹15,000 goes to the mother" when the passage says ₹13,000.
  - Run on gpt-oss-20b because the free-tier daily token quota for gpt-oss-120b was used up by the extraction evals.
- **v2 (in progress): explanation prompt now separates citizen facts, rule check and passages, and the judge is told what the citizen said.** On the first 7 of 40 samples, faithfulness went from 0.870 to 0.953 on the same samples and model. The run stopped at Groq's daily token limit and resumes with `python -m eval.faithfulness --engine llm --generator llm --model openai/gpt-oss-20b` (progress is saved per sample).
- An earlier run scored 0.975 because the Hindi question retrieved nothing: Hindi/Telugu questions were searched before the multilingual model had loaded. Search now waits for that model when needed, and a regression test covers it.
- **Retrieval** finds the right scheme as the top result for 10/10 of the free-form questions (8 English, 1 Telugu, 1 Hindi).

## Project layout

```
data/schemes.yaml          curated scheme KB + criteria (edit this to add schemes)
data/pdfs/                 optional guideline PDFs (auto-indexed for RAG)
yojana_mitra/
  profile.py               Profile model, derived facts, field labels/questions (EN/TE/HI)
  schemes.py               KB loader, macros, CNF criteria
  graph.py                 MemoryGraph + Neo4jGraph, MATCH_CYPHER
  matcher.py               buckets, explanations of met/unmet, follow-up ranking
  extract.py / extract_rules.py / llm.py   Claude + rule-based extraction
  rag.py / explain.py      hybrid retrieval, grounded explanations and Q&A
  api.py                   FastAPI + static UI
web/                       index.html, app.js, styles.css
eval/                      profiles, holdout, questions, run_eval.py, faithfulness.py, results/
tests/                     pytest (matcher, extractor, API, Neo4j parity when NEO4J_URI is set)
```

## Adding a scheme

Add an entry to `data/schemes.yaml` with `criteria` built from profile fields and the ops
`eq | in | gte | lte | is_true | is_false | any_in`. Use `any_of: [...]` for OR conditions and
`use: ap_welfare_standard` for the usual AP income/land/vehicle checks. Restart the app; the
graph, retrieval index and UI pick it up. Then add labelled profiles to the eval set.

## Limitations

- Scheme rules and amounts change. Data was compiled from official portals and news coverage up to
  November 2026, and every scheme lists its sources. Some facts were contested at review time, for
  example tenant-farmer coverage under Annadata Sukhibhava and the cover limits in the Universal Health
  Policy rollout. Each scheme's `status_note` flags these, and the UI tells users to confirm at the
  Village/Ward Secretariat.
- Eligibility is necessary-condition screening, not a sanction decision. Some rules can't be checked
  from a description: electricity use, urban property size, one pension per person.
- Only one pension is paid per person, even when someone qualifies for two categories (e.g. old age and widow).
- The Neo4j path has a parity test (`tests/test_matcher.py`) but has not yet been run against a live
  Neo4j instance in this environment.
- Without an API key, explanations stay in English (UI labels and scheme names are localised).

*Independent helper, not a government website.*
