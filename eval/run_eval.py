"""Eligibility evaluation: 50 hand-labelled synthetic citizens.

    python -m eval.run_eval                 # offline rule-based extractor
    python -m eval.run_eval --llm           # Claude extractor (needs ANTHROPIC_API_KEY)
    python -m eval.run_eval --backend neo4j # run the match in Neo4j instead of the in-memory graph

Pipeline under test: free text -> profile extraction -> graph match -> "eligible" bucket.
Reports micro/macro precision & recall, per-scheme scores, per-language scores, field-level
extraction accuracy and every error, and writes eval/results/<run>.md + .json.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from yojana_mitra import llm  # noqa: E402
from yojana_mitra.extract import extract  # noqa: E402
from yojana_mitra.graph import get_store  # noqa: E402
from yojana_mitra.matcher import match_profile  # noqa: E402
from yojana_mitra.schemes import scheme_index  # noqa: E402

FIELDS = ["age", "gender", "state", "area", "marital_status", "occupations", "land_acres", "annual_income",
          "children_in_school"]


def prf(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    p = tp / (tp + fp) if tp + fp else 1.0
    r = tp / (tp + fn) if tp + fn else 1.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f


def field_ok(field: str, gold, pred) -> bool:
    if field == "occupations":
        return set(gold) <= set(pred or [])
    if field in ("land_acres", "annual_income") and gold is not None and pred is not None:
        return abs(float(gold) - float(pred)) <= max(1.0, 0.02 * float(gold))
    if field == "state":
        return (pred or "").lower() == str(gold).lower()
    return gold == pred


def run(use_llm: bool, backend: str | None, limit: int | None, file: str = "profiles.yaml") -> dict:
    data = yaml.safe_load((ROOT / "eval" / file).read_text(encoding="utf-8"))["profiles"]
    if limit:
        data = data[:limit]
    known = set(scheme_index())
    for p in data:
        bad = set(p["eligible"]) - known
        assert not bad, f"{p['id']}: unknown scheme ids {bad}"

    store = get_store(force=backend) if backend else get_store()
    tp = fp = fn = 0
    tp_l = fp_l = fn_l = 0  # lenient: eligible + need_info counted as predicted
    per_scheme = defaultdict(lambda: [0, 0, 0])
    per_lang = defaultdict(lambda: [0, 0, 0])
    field_hits = defaultdict(lambda: [0, 0])
    macro_p, macro_r = [], []
    rows = []
    t0 = time.time()
    methods = defaultdict(int)
    for p in data:
        ex = extract(p["text"], use_llm=use_llm)
        methods[ex.method] += 1
        res = match_profile(ex.profile, store=store)
        pred = {m.scheme_id for m in res.eligible}
        lenient = pred | {m.scheme_id for m in res.need_info}
        gold = set(p["eligible"])
        a, b, c = len(pred & gold), len(pred - gold), len(gold - pred)
        tp, fp, fn = tp + a, fp + b, fn + c
        al, bl, cl = len(lenient & gold), len(lenient - gold), len(gold - lenient)
        tp_l, fp_l, fn_l = tp_l + al, fp_l + bl, fn_l + cl
        pp, rr, _ = prf(a, b, c)
        macro_p.append(pp)
        macro_r.append(rr)
        lang = p["lang"]
        per_lang[lang][0] += a; per_lang[lang][1] += b; per_lang[lang][2] += c
        for s in pred & gold:
            per_scheme[s][0] += 1
        for s in pred - gold:
            per_scheme[s][1] += 1
        for s in gold - pred:
            per_scheme[s][2] += 1
        fdiff = {}
        got = ex.profile.model_dump()
        for f in FIELDS:
            if f in p["profile"]:
                ok = field_ok(f, p["profile"][f], got.get(f))
                field_hits[f][0] += ok
                field_hits[f][1] += 1
                if not ok:
                    fdiff[f] = {"gold": p["profile"][f], "pred": got.get(f)}
        rows.append({"id": p["id"], "lang": lang, "method": ex.method, "precision": round(pp, 3),
                     "recall": round(rr, 3), "false_positives": sorted(pred - gold),
                     "false_negatives": sorted(gold - pred), "field_errors": fdiff})

    P, R, F = prf(tp, fp, fn)
    Pl, Rl, Fl = prf(tp_l, fp_l, fn_l)
    return {
        "config": {"dataset": file, "extractor": f"llm-{llm.provider()}" if use_llm else "rules", "model": llm.model() if use_llm else None, "methods_used": dict(methods),
                   "graph_backend": store.name, "profiles": len(data), "schemes": len(known),
                   "seconds": round(time.time() - t0, 1)},
        "micro": {"precision": P, "recall": R, "f1": F, "tp": tp, "fp": fp, "fn": fn},
        "macro": {"precision": sum(macro_p) / len(macro_p), "recall": sum(macro_r) / len(macro_r)},
        "lenient_micro": {"precision": Pl, "recall": Rl, "f1": Fl},
        "per_language": {k: dict(zip(("precision", "recall", "f1"), prf(*v)), n=v) for k, v in per_lang.items()},
        "per_scheme": {k: dict(zip(("precision", "recall", "f1"), prf(*v)), tp=v[0], fp=v[1], fn=v[2])
                       for k, v in sorted(per_scheme.items())},
        "field_accuracy": {k: {"accuracy": v[0] / v[1], "n": v[1]} for k, v in field_hits.items()},
        "rows": rows,
    }


def to_markdown(r: dict) -> str:
    c, m = r["config"], r["micro"]
    out = [f"# Eligibility evaluation – {c['dataset']} – extractor: {c['extractor']}, graph: {c['graph_backend']}", "",
           f"{c['profiles']} hand-labelled profiles × {c['schemes']} schemes · {c['seconds']} s", "",
           "| Metric | Precision | Recall | F1 |", "|---|---|---|---|",
           f"| Micro (scheme-level) | {m['precision']:.3f} | {m['recall']:.3f} | {m['f1']:.3f} |",
           f"| Macro (per citizen) | {r['macro']['precision']:.3f} | {r['macro']['recall']:.3f} | – |",
           f"| Lenient (eligible + need-info) | {r['lenient_micro']['precision']:.3f} | {r['lenient_micro']['recall']:.3f} | {r['lenient_micro']['f1']:.3f} |",
           "", f"TP={m['tp']} FP={m['fp']} FN={m['fn']}", "", "## By language", "",
           "| Lang | P | R | F1 |", "|---|---|---|---|"]
    for k, v in sorted(r["per_language"].items()):
        out.append(f"| {k} | {v['precision']:.3f} | {v['recall']:.3f} | {v['f1']:.3f} |")
    out += ["", "## Extraction field accuracy", "", "| Field | Accuracy | n |", "|---|---|---|"]
    for k, v in sorted(r["field_accuracy"].items(), key=lambda x: x[1]["accuracy"]):
        out.append(f"| {k} | {v['accuracy']:.2f} | {v['n']} |")
    out += ["", "## Per scheme (worst F1 first)", "", "| Scheme | P | R | TP | FP | FN |", "|---|---|---|---|---|---|"]
    for k, v in sorted(r["per_scheme"].items(), key=lambda x: x[1]["f1"]):
        out.append(f"| {k} | {v['precision']:.2f} | {v['recall']:.2f} | {v['tp']} | {v['fp']} | {v['fn']} |")
    out += ["", "## Errors", ""]
    for row in r["rows"]:
        if row["false_positives"] or row["false_negatives"] or row["field_errors"]:
            out.append(f"- **{row['id']}** ({row['lang']}) FP={row['false_positives']} FN={row['false_negatives']} "
                       f"fields={json.dumps(row['field_errors'], ensure_ascii=False)}")
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm", action="store_true", help="use the LLM extractor (Groq or Claude, whichever key is set)")
    ap.add_argument("--backend", choices=["memory", "neo4j"], default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--file", default="profiles.yaml", help="profiles.yaml or profiles_holdout.yaml")
    args = ap.parse_args()
    r = run(args.llm, args.backend, args.limit, args.file)
    outdir = ROOT / "eval" / "results"
    outdir.mkdir(exist_ok=True)
    name = f"eligibility_{r['config']['extractor']}" + ("_holdout" if "holdout" in args.file else "")
    (outdir / f"{name}.json").write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
    md = to_markdown(r)
    (outdir / f"{name}.md").write_text(md, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
