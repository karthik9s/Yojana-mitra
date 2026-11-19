"""Knowledge graph of (Scheme)-[:REQUIRES {group, assume, label}]->(Criterion).

Two interchangeable backends run the same tri-state matching logic:

* Neo4jGraph   - real Neo4j, the match is a single Cypher query (MATCH_CYPHER).
* MemoryGraph  - a networkx graph with identical semantics, so the app and the evaluation
                 run anywhere without a database.

Tri-state semantics, per criterion:   1 = met, 0 = unknown (fact not provided), -1 = not met.
A criterion marked `assume` evaluates to 1 when its fact is missing (and is reported as
"assumed - please confirm"). Criteria in one REQUIRES group are OR-ed (max), groups are
AND-ed (min). A scheme's status is therefore 1 (eligible), 0 (need more info) or -1.
"""
from __future__ import annotations

import logging
from typing import Iterable, Protocol

import networkx as nx

from . import config
from .schemes import Criterion, Scheme, load_schemes

log = logging.getLogger(__name__)


class CriterionResult(dict):
    """{id, field, label, status, assumed, group}"""


class GraphStore(Protocol):
    name: str

    def load(self, schemes: Iterable[Scheme]) -> None: ...
    def match(self, facts: dict) -> dict[str, tuple[int, list[CriterionResult]]]: ...
    def stats(self) -> dict: ...


def _is_missing(c: Criterion, v) -> bool:
    return v is None or (c.is_list_field and len(v) == 0)


def evaluate(c: Criterion, v, assume: bool) -> tuple[int, bool]:
    """Python twin of the CASE expression in MATCH_CYPHER."""
    if _is_missing(c, v):
        return (1, True) if assume else (0, False)
    op = c.op
    try:
        if op == "eq":
            ok = v == c.value
        elif op == "in":
            ok = v in (c.values or [])
        elif op == "gte":
            ok = v >= c.value
        elif op == "lte":
            ok = v <= c.value
        elif op == "is_true":
            ok = v is True
        elif op == "is_false":
            ok = v is False
        elif op == "any_in":
            ok = any(x in (c.values or []) for x in v)
        else:
            return 0, False
    except TypeError:  # Cypher compares mismatched types as null -> ELSE -1
        return -1, False
    return (1 if ok else -1), False


class MemoryGraph:
    name = "in-memory graph (networkx)"

    def __init__(self) -> None:
        self.g = nx.MultiDiGraph()

    def load(self, schemes: Iterable[Scheme]) -> None:
        self.g.clear()
        for s in schemes:
            self.g.add_node(("Scheme", s.id), kind="Scheme", name=s.name, category=s.category, level=s.level)
            self.g.add_node(("Category", s.category), kind="Category")
            self.g.add_edge(("Scheme", s.id), ("Category", s.category), type="IN_CATEGORY")
            for c in s.criteria:
                self.g.add_node(("Criterion", c.id), kind="Criterion", crit=c)
                self.g.add_edge(("Scheme", s.id), ("Criterion", c.id), type="REQUIRES",
                                group=c.group, assume=c.assume, label=c.label)

    def match(self, facts: dict) -> dict[str, tuple[int, list[CriterionResult]]]:
        out: dict[str, tuple[int, list[CriterionResult]]] = {}
        for node, data in self.g.nodes(data=True):
            if data.get("kind") != "Scheme":
                continue
            groups: dict[int, int] = {}
            details: list[CriterionResult] = []
            for _, tgt, e in self.g.out_edges(node, data=True):
                if e["type"] != "REQUIRES":
                    continue
                c: Criterion = self.g.nodes[tgt]["crit"]
                st, assumed = evaluate(c, facts.get(c.field), e["assume"])
                groups[e["group"]] = max(groups.get(e["group"], -1), st)
                details.append(CriterionResult(id=c.id, field=c.field, label=e["label"], status=st,
                                               assumed=assumed, group=e["group"]))
            status = min(groups.values()) if groups else 1
            out[node[1]] = (status, sorted(details, key=lambda d: d["group"]))
        return out

    def stats(self) -> dict:
        kinds: dict[str, int] = {}
        for _, d in self.g.nodes(data=True):
            kinds[d["kind"]] = kinds.get(d["kind"], 0) + 1
        rels = sum(1 for *_, e in self.g.edges(data=True) if e["type"] == "REQUIRES")
        shared = sum(1 for n, d in self.g.nodes(data=True)
                     if d["kind"] == "Criterion" and self.g.in_degree(n) > 1)
        return {"backend": self.name, "nodes": kinds, "requires_edges": rels, "shared_criteria": shared}


# ---------------------------------------------------------------------------------------
# Neo4j
# ---------------------------------------------------------------------------------------
LOAD_CYPHER = """
UNWIND $schemes AS s
MERGE (sc:Scheme {id: s.id})
SET sc.name = s.name, sc.name_te = s.name_te, sc.level = s.level, sc.category = s.category,
    sc.amount = s.amount, sc.summary = s.summary, sc.portal = s.portal
MERGE (cat:Category {name: s.category})
MERGE (sc)-[:IN_CATEGORY]->(cat)
MERGE (d:Department {name: s.department})
MERGE (sc)-[:OFFERED_BY]->(d)
WITH sc, s
UNWIND s.criteria AS c
MERGE (cr:Criterion {id: c.id})
SET cr.field = c.field, cr.op = c.op, cr.value = c.value, cr.values = c.values,
    cr.list_field = c.list_field
MERGE (sc)-[r:REQUIRES {group: c.group, cid: c.id}]->(cr)
SET r.assume = c.assume, r.label = c.label
"""

DOCS_CYPHER = """
UNWIND $schemes AS s
MATCH (sc:Scheme {id: s.id})
UNWIND s.documents AS doc
MERGE (dd:Document {name: doc})
MERGE (sc)-[:NEEDS_DOCUMENT]->(dd)
"""

# The eligibility query. $p is the citizen's fact map (profile + derived facts).
MATCH_CYPHER = """
MATCH (s:Scheme)-[r:REQUIRES]->(c:Criterion)
WITH s, r, c, $p[c.field] AS v
WITH s, r, c, v,
     (v IS NULL OR CASE WHEN c.list_field THEN size(v) = 0 ELSE false END) AS missing
WITH s, r, c,
     CASE
       WHEN missing THEN CASE WHEN r.assume THEN 1 ELSE 0 END
       WHEN c.op = 'eq'       THEN CASE WHEN v = c.value THEN 1 ELSE -1 END
       WHEN c.op = 'in'       THEN CASE WHEN v IN c.values THEN 1 ELSE -1 END
       WHEN c.op = 'gte'      THEN CASE WHEN v >= c.value THEN 1 ELSE -1 END
       WHEN c.op = 'lte'      THEN CASE WHEN v <= c.value THEN 1 ELSE -1 END
       WHEN c.op = 'is_true'  THEN CASE WHEN v = true THEN 1 ELSE -1 END
       WHEN c.op = 'is_false' THEN CASE WHEN v = false THEN 1 ELSE -1 END
       WHEN c.op = 'any_in'   THEN CASE WHEN any(x IN v WHERE x IN c.values) THEN 1 ELSE -1 END
       ELSE 0
     END AS st,
     (missing AND r.assume) AS assumed
WITH s, r.group AS g, max(st) AS gst,
     collect({id: c.id, field: c.field, label: r.label, status: st, assumed: assumed, group: r.group}) AS det
WITH s, min(gst) AS status, collect(det) AS dets
RETURN s.id AS id, status, reduce(acc = [], d IN dets | acc + d) AS details
"""


class Neo4jGraph:
    name = "Neo4j"

    def __init__(self, uri: str, user: str, password: str) -> None:
        from neo4j import GraphDatabase  # optional dependency

        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.driver.verify_connectivity()

    def load(self, schemes: Iterable[Scheme]) -> None:
        payload = []
        for s in schemes:
            payload.append({
                "id": s.id, "name": s.name, "name_te": s.name_te, "level": s.level, "category": s.category,
                "amount": s.amount, "summary": s.summary, "portal": s.portal, "department": s.department or "Unknown",
                "documents": s.documents,
                "criteria": [{"id": c.id, "field": c.field, "op": c.op, "value": c.value, "values": c.values,
                              "list_field": c.is_list_field, "group": c.group, "assume": c.assume, "label": c.label}
                             for c in s.criteria],
            })
        with self.driver.session() as sess:
            sess.run("CREATE CONSTRAINT scheme_id IF NOT EXISTS FOR (s:Scheme) REQUIRE s.id IS UNIQUE")
            sess.run("CREATE CONSTRAINT criterion_id IF NOT EXISTS FOR (c:Criterion) REQUIRE c.id IS UNIQUE")
            sess.run("MATCH (n) WHERE n:Scheme OR n:Criterion OR n:Category OR n:Department OR n:Document DETACH DELETE n")
            sess.run(LOAD_CYPHER, schemes=payload)
            sess.run(DOCS_CYPHER, schemes=payload)

    def match(self, facts: dict) -> dict[str, tuple[int, list[CriterionResult]]]:
        with self.driver.session() as sess:
            rows = sess.run(MATCH_CYPHER, p=facts).data()
        return {r["id"]: (r["status"], sorted([CriterionResult(d) for d in r["details"]], key=lambda d: d["group"]))
                for r in rows}

    def stats(self) -> dict:
        with self.driver.session() as sess:
            nodes = sess.run("MATCH (n) RETURN labels(n)[0] AS k, count(*) AS c").data()
            rels = sess.run("MATCH ()-[r:REQUIRES]->() RETURN count(r) AS c").single()["c"]
            shared = sess.run("MATCH (c:Criterion)<-[:REQUIRES]-(s) WITH c, count(s) AS n WHERE n > 1 "
                              "RETURN count(c) AS c").single()["c"]
        return {"backend": self.name, "nodes": {r["k"]: r["c"] for r in nodes}, "requires_edges": rels,
                "shared_criteria": shared}


_store: GraphStore | None = None


def get_store(force: str | None = None) -> GraphStore:
    """Return the configured graph store (cached)."""
    global _store
    if _store is not None and force is None:
        return _store
    choice = force or config.GRAPH_BACKEND
    store: GraphStore | None = None
    if choice in ("auto", "neo4j") and config.NEO4J_URI:
        try:
            store = Neo4jGraph(config.NEO4J_URI, config.NEO4J_USER, config.NEO4J_PASSWORD)
            store.load(load_schemes())
        except Exception as e:  # pragma: no cover - depends on a running DB
            if choice == "neo4j":
                raise
            log.warning("Neo4j unavailable (%s); falling back to in-memory graph", e)
            store = None
    if store is None:
        store = MemoryGraph()
        store.load(load_schemes())
    if force is None:
        _store = store
    return store
