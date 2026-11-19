"""Load the scheme knowledge graph into Neo4j and print a sample match.

    docker compose up -d neo4j
    set NEO4J_URI / NEO4J_PASSWORD (see .env.example)
    python scripts/load_neo4j.py

Then explore in the Neo4j browser (http://localhost:7474), e.g.
    MATCH (s:Scheme)-[r:REQUIRES]->(c:Criterion) RETURN s, r, c LIMIT 100
    // criteria shared by the most schemes
    MATCH (c:Criterion)<-[:REQUIRES]-(s) RETURN c.id, count(s) AS n ORDER BY n DESC LIMIT 10
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from yojana_mitra import config  # noqa: E402
from yojana_mitra.graph import MATCH_CYPHER, Neo4jGraph  # noqa: E402
from yojana_mitra.profile import Profile, derive  # noqa: E402
from yojana_mitra.schemes import load_schemes  # noqa: E402

if not config.NEO4J_URI:
    sys.exit("Set NEO4J_URI (and NEO4J_PASSWORD) first - see .env.example")

g = Neo4jGraph(config.NEO4J_URI, config.NEO4J_USER, config.NEO4J_PASSWORD)
g.load(load_schemes())
print("Loaded:", g.stats())

p = Profile(age=45, gender="female", state="Andhra Pradesh", area="rural", occupations=["farmer"],
            land_acres=2, annual_income=90000, children_in_school=2)
res = g.match(derive(p))
print("\nEligible for the sample 45-year-old woman farmer:")
for sid, (status, _) in sorted(res.items()):
    if status == 1:
        print("  -", sid)
print("\nCypher used:\n", MATCH_CYPHER)
