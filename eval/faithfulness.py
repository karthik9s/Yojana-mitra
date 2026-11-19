"""Answer-faithfulness evaluation for the RAG layer.

Builds (question, answer, retrieved contexts) samples from two sources:
  * scheme explanations for the top eligible schemes of evaluation profiles
  * free-form citizen questions (eval/questions.yaml)
and scores how much of each answer is supported by its retrieved context.

Engines (--engine):
  ragas   the RAGAS `Faithfulness` metric, with the configured LLM as the judge.
          pip install ragas langchain-groq   (needs GROQ_API_KEY or ANTHROPIC_API_KEY)
  llm     the same algorithm as RAGAS faithfulness implemented directly with the configured LLM
          (Groq or Claude): decompose the answer into atomic claims, then judge each claim against the
          context; score = supported claims / total claims. (needs GROQ_API_KEY or ANTHROPIC_API_KEY)
  lexical offline proxy: an answer sentence counts as supported when >=60% of its content
          words appear in one retrieved passage. Cheap and deterministic, but it cannot catch
          paraphrased hallucinations, so treat it as a smoke test, not a faithfulness score.

    python -m eval.faithfulness --engine lexical
    python -m eval.faithfulness --engine llm --n 20
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from statistics import mean

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from yojana_mitra import llm  # noqa: E402
from yojana_mitra.explain import answer_question, explain_scheme  # noqa: E402
from yojana_mitra.extract import extract  # noqa: E402
from yojana_mitra.matcher import match_profile  # noqa: E402

STOP = set("the a an and or of to for in on at is are be with by from as it this that you your their "
           "per can will may not no if all any each who which what how".split())


def sample_specs(n_profiles: int, per_profile: int) -> list[dict]:
    """Which answers to evaluate. Profiles are read with the offline rules (no LLM tokens spent):
    only the ANSWERS are under test here, not extraction."""
    profiles = yaml.safe_load((ROOT / "eval" / "profiles.yaml").read_text(encoding="utf-8"))["profiles"]
    specs = []
    for p in profiles[:n_profiles]:
        ex = extract(p["text"], use_llm=False)
        res = match_profile(ex.profile)
        for m in res.eligible[:per_profile]:
            specs.append({"kind": "explain", "id": f"{p['id']}:{m.scheme_id}", "scheme_id": m.scheme_id,
                          "profile": ex.profile.model_dump(), "match": m.model_dump(),
                          "question": f"Explain {m.name} to me and how to apply."})
    qs = yaml.safe_load((ROOT / "eval" / "questions.yaml").read_text(encoding="utf-8"))["questions"]
    for i, q in enumerate(qs):
        specs.append({"kind": "qa", "id": f"q{i + 1:02d}", "question": q["question"], "lang": q.get("lang", "en")})
    return specs


def generate(spec: dict, use_llm: bool) -> dict:
    if spec["kind"] == "explain":
        e = explain_scheme(spec["scheme_id"], spec["profile"], spec["match"], lang="en", use_llm=use_llm)
        return {"answer": e["answer"], "contexts": [c["text"] for c in e["contexts"]], "method": e["method"],
                "citizen_facts": e.get("citizen_facts")}
    a = answer_question(spec["question"], lang=spec["lang"], use_llm=use_llm)
    return {"answer": a["answer"], "contexts": [c["text"] for c in a["contexts"]], "method": a["method"]}


def is_rate_limit(e: Exception) -> bool:
    return "RateLimit" in type(e).__name__ or "rate_limit" in str(e) or "429" in str(e)


# ---------------------------------------------------------------------------- lexical proxy
def _words(s: str) -> set[str]:
    return {w for w in re.findall(r"[\w₹,.]+", s.lower().replace(",", "")) if w not in STOP and len(w) > 1}


def lexical_score(answer: str, contexts: list[str]) -> float:
    clean = re.sub(r"\[\d+\]|[*_#>✅❔]", " ", answer)
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", clean)
             if len(_words(s)) >= 4 and not s.strip().endswith(":")]  # skip lead-ins like "Here is ...:"
    if not sents:
        return 1.0
    ctx = [_words(c) for c in contexts]
    ok = 0
    for s in sents:
        w = _words(s)
        ok += any(len(w & c) / len(w) >= 0.6 for c in ctx)
    return ok / len(sents)


# ---------------------------------------------------------------------------- Claude judge
CLAIMS_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["claims"],
                 "properties": {"claims": {"type": "array", "items": {"type": "string"}}}}
VERDICT_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["verdicts"],
                  "properties": {"verdicts": {"type": "array", "items": {
                      "type": "object", "additionalProperties": False, "required": ["claim", "supported", "reason"],
                      "properties": {"claim": {"type": "string"}, "supported": {"type": "boolean"},
                                     "reason": {"type": "string"}}}}}}


def llm_score(question: str, answer: str, contexts: list[str], facts: str | None = None) -> tuple[float, list[dict]]:
    """RAGAS-style faithfulness. `facts` = what the citizen told us; it may support claims ABOUT the
    citizen ("you are 64") but never claims about scheme rules, amounts or steps."""
    claims = llm.complete_json(
        "Break the answer into short, self-contained factual claims (one fact each, resolve pronouns). "
        "Ignore greetings, headings, and requests or questions to the reader (e.g. 'please confirm that…').",
        f"Question: {question}\n\nAnswer:\n{answer}", CLAIMS_SCHEMA, max_tokens=4000, effort="low")["claims"]
    if not claims:
        return 1.0, []
    ctx = "\n\n".join(f"[{i}] {c}" for i, c in enumerate(contexts, 1))
    system = ("You are a strict fact-checker. For each claim decide whether it can be directly inferred from the "
              "context. Anything not stated or implied by the context is unsupported, even if true in the real world.")
    user = f"Official scheme passages:\n{ctx}\n\n"
    if facts:
        system += (" CITIZEN FACTS are what the citizen said about themselves: they can support claims about the "
                   "citizen (their age, income, land, etc.) but NEVER claims about what a scheme requires, pays or "
                   "how to apply - those must come from the official passages.")
        user += f"CITIZEN FACTS:\n{facts}\n\n"
    verdicts = llm.complete_json(system, user + "Claims:\n" + "\n".join(f"- {c}" for c in claims), VERDICT_SCHEMA,
                                 max_tokens=8000, effort="medium")["verdicts"]
    return sum(v["supported"] for v in verdicts) / max(1, len(verdicts)), verdicts


# ---------------------------------------------------------------------------- RAGAS
def ragas_scores(samples: list[dict]) -> list[float]:
    try:
        from ragas import EvaluationDataset, evaluate
        from ragas.llms import LangchainLLMWrapper
        from ragas.metrics import Faithfulness
        if llm.provider() == "groq":
            from langchain_groq import ChatGroq
        else:
            from langchain_anthropic import ChatAnthropic
    except ImportError as e:
        raise SystemExit("RAGAS is not installed in this environment. Run `--engine llm` to generate the "
                         "samples, then score them with eval/ragas_score.py in the isolated ragas venv "
                         f"(see that file's docstring). ({e})")
    from yojana_mitra import config

    ds = EvaluationDataset.from_list([{"user_input": s["question"], "response": s["answer"],
                                       "retrieved_contexts": s["contexts"]} for s in samples])
    if llm.provider() == "groq":
        chat = ChatGroq(model=config.GROQ_MODEL, temperature=0, max_tokens=8000)
    else:
        chat = ChatAnthropic(model=config.CLAUDE_MODEL, max_tokens=8000)
    judge = LangchainLLMWrapper(chat)
    result = evaluate(ds, metrics=[Faithfulness(llm=judge)])
    return [float(x) for x in result.to_pandas()["faithfulness"].tolist()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", choices=["lexical", "llm", "claude", "ragas"], default="lexical")
    ap.add_argument("--n", type=int, default=15, help="number of evaluation profiles to explain")
    ap.add_argument("--per-profile", type=int, default=2)
    ap.add_argument("--generator", choices=["auto", "llm", "template"], default="auto",
                    help="how answers are generated (auto = LLM if a key is set)")
    ap.add_argument("--model", default=None, help="override the Groq model for this run (e.g. openai/gpt-oss-20b)")
    ap.add_argument("--fresh", action="store_true", help="ignore saved progress and start over")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    from yojana_mitra import config
    if args.model:
        config.GROQ_MODEL = args.model
    if args.engine == "claude":
        args.engine = "llm"  # backwards-compatible alias
    if args.engine in ("llm", "ragas") and not llm.available():
        raise SystemExit("This engine needs an LLM key (set GROQ_API_KEY or ANTHROPIC_API_KEY in .env).")
    # Evaluate the full retriever (dense + sparse), not the warm-up state.
    from yojana_mitra.rag import get_retriever
    print("dense retrieval:", "ready" if get_retriever().wait_until_ready() else "UNAVAILABLE (sparse only)")
    use_llm = {"auto": None, "llm": True, "template": False}[args.generator]
    if use_llm is None:
        use_llm = llm.available()
    specs = sample_specs(args.n, args.per_profile)
    model_tag = (llm.model() or "none").replace("/", "_") if use_llm or args.engine == "llm" else "offline"
    # Progress is saved after every sample, so a rate-limit stop can be resumed by re-running.
    cache_path = ROOT / "eval" / "results" / f"_faith_cache_{args.engine}_{model_tag}.json"
    cache = {} if args.fresh or not cache_path.exists() else json.loads(cache_path.read_text(encoding="utf-8"))
    samples, stopped = [], None
    for i, spec in enumerate(specs, 1):
        if spec["id"] in cache:
            samples.append(cache[spec["id"]])
            continue
        try:
            s = {k: spec[k] for k in ("kind", "id", "question")} | generate(spec, use_llm)
            if args.engine == "llm":
                if s["method"] != "llm":
                    raise RuntimeError("answer generation fell back to the template (LLM call failed)")
                s["faithfulness"], s["verdicts"] = llm_score(s["question"], s["answer"], s["contexts"],
                                                             s.get("citizen_facts"))
            elif args.engine == "lexical":
                s["faithfulness"] = lexical_score(s["answer"], s["contexts"])
        except Exception as e:
            if is_rate_limit(e) or "fell back" in str(e):
                stopped = f"stopped at sample {i}/{len(specs)}: {str(e)[:200]}"
                print(stopped)
                break
            raise
        samples.append(s)
        cache[spec["id"]] = s
        cache_path.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
        print(f"[{i}/{len(specs)}] {s['id']}: {s.get('faithfulness')}", flush=True)

    if args.engine == "ragas":
        scores = ragas_scores(samples)
        for s, sc in zip(samples, scores):
            s["faithfulness"] = sc
    if not samples:
        raise SystemExit(stopped or "no samples")

    def avg(kind=None):
        xs = [s["faithfulness"] for s in samples if kind is None or s["kind"] == kind]
        return mean(xs) if xs else float("nan")

    gen = sorted({s["method"] for s in samples})
    judge = f", model: {llm.provider()} {llm.model()}" if args.engine == "llm" else ""
    report = [f"# Faithfulness – engine: {args.engine}, generator: {', '.join(gen)}{judge}", "",
              f"{len(samples)} of {len(specs)} samples" + (f" (**incomplete** – {stopped}; re-run to resume)" if stopped else ""),
              "", "| Set | Faithfulness | n |", "|---|---|---|",
              f"| All | {avg():.3f} | {len(samples)} |",
              f"| Scheme explanations | {avg('explain'):.3f} | {sum(s['kind'] == 'explain' for s in samples)} |",
              f"| Free-form Q&A (EN/TE/HI) | {avg('qa'):.3f} | {sum(s['kind'] == 'qa' for s in samples)} |",
              "", "## Lowest-scoring samples", ""]
    for s in sorted(samples, key=lambda s: s["faithfulness"])[:5]:
        report.append(f"- **{s['id']}** {s['faithfulness']:.2f}: {s['question']}")
        for v in s.get("verdicts", []):
            if not v["supported"]:
                report.append(f"    - unsupported: {v['claim']} ({v['reason']})")
    if args.engine == "lexical":
        report += ["", "_Lexical proxy only: it checks word overlap with retrieved passages and cannot detect "
                   "paraphrased hallucinations. Template answers are copied from the context, so they score ~1.0 "
                   "by construction. Use `--engine llm` or `--engine ragas` for a real faithfulness score._"]
    md = "\n".join(report) + "\n"
    outdir = ROOT / "eval" / "results"
    outdir.mkdir(exist_ok=True)
    name = f"faithfulness_{args.engine}_{'-'.join(gen)}" + (f"_{model_tag}" if args.engine == "llm" else "")
    (outdir / f"{name}.md").write_text(md, encoding="utf-8")
    (outdir / f"{name}.json").write_text(json.dumps(samples, indent=2, ensure_ascii=False), encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
