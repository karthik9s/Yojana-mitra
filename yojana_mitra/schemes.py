"""Load the curated scheme knowledge base and normalise criteria into CNF groups."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel

from .config import DATA_DIR

LIST_FIELDS = {"occupations", "health_conditions"}
VALID_OPS = {"eq", "in", "gte", "lte", "is_true", "is_false", "any_in"}


class Criterion(BaseModel):
    field: str
    op: str
    value: Any = None
    values: Optional[list] = None
    label: str
    assume: bool = False
    group: int = 0

    @property
    def id(self) -> str:
        """Canonical id: identical conditions in different schemes share one graph node."""
        if self.values is not None:
            arg = ",".join(sorted(map(str, self.values)))
        elif self.value is not None:
            arg = json.dumps(self.value)
        else:
            arg = ""
        return f"{self.field}|{self.op}|{arg}"

    @property
    def is_list_field(self) -> bool:
        return self.field in LIST_FIELDS


class Scheme(BaseModel):
    id: str
    name: str
    name_te: str = ""
    name_hi: str = ""
    level: str
    category: str
    department: str = ""
    amount: str = ""
    summary: str = ""
    benefits: list[str] = []
    documents: list[str] = []
    how_to_apply: list[str] = []
    portal: str = ""
    sources: list[str] = []
    status_note: str = ""
    details: str = ""
    criteria: list[Criterion] = []

    def display_name(self, lang: str = "en") -> str:
        return {"te": self.name_te, "hi": self.name_hi}.get(lang) or self.name


def _expand(raw: list, macros: dict) -> list[list[dict]]:
    """Turn the YAML criteria list into CNF: a list of OR-groups."""
    groups: list[list[dict]] = []
    for item in raw:
        if "use" in item:
            for c in macros[item["use"]]:
                groups.append([dict(c)])
        elif "any_of" in item:
            groups.append([dict(c) for c in item["any_of"]])
        else:
            groups.append([dict(item)])
    return groups


def parse_kb(doc: dict) -> list[Scheme]:
    macros = doc.get("macros", {})
    out: list[Scheme] = []
    seen: set[str] = set()
    for s in doc["schemes"]:
        if s["id"] in seen:
            raise ValueError(f"duplicate scheme id {s['id']}")
        seen.add(s["id"])
        crits: list[Criterion] = []
        for gi, group in enumerate(_expand(s.get("criteria", []), macros)):
            for c in group:
                if c["op"] not in VALID_OPS:
                    raise ValueError(f"{s['id']}: unknown op {c['op']}")
                crits.append(Criterion(group=gi, **c))
        data = {k: v for k, v in s.items() if k != "criteria"}
        out.append(Scheme(**data, criteria=crits))
    return out


@lru_cache(maxsize=4)
def load_schemes(path: Optional[str] = None) -> tuple[Scheme, ...]:
    p = Path(path) if path else DATA_DIR / "schemes.yaml"
    with open(p, encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    return tuple(parse_kb(doc))


def scheme_index() -> dict[str, Scheme]:
    return {s.id: s for s in load_schemes()}


def kb_meta() -> dict:
    with open(DATA_DIR / "schemes.yaml", encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    return {"version": doc.get("version"), "last_reviewed": doc.get("last_reviewed")}
