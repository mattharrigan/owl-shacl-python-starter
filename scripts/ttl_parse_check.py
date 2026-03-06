
#!/usr/bin/env python3
"""
Pre-commit hook: parse RDF Turtle files to catch syntax errors early.
Usage (pre-commit will pass staged filenames):
  python scripts/ttl_parse_check.py file1.ttl file2.ttl ...
"""
import sys
from rdflib import Graph
from pathlib import Path

if len(sys.argv) <= 1:
    sys.exit(0)  # Nothing to check

errors = []
for fname in sys.argv[1:]:
    p = Path(fname)
    if not p.exists():
        continue
    try:
        g = Graph()
        fmt = None
        if p.suffix in (".ttl", ".turtle"):
            fmt = "turtle"
        elif p.suffix in (".nt", ".ntriples"):
            fmt = "nt"
        elif p.suffix in (".trig",):
            fmt = "trig"
        elif p.suffix in (".nq",):
            fmt = "nquads"
        g.parse(p.as_posix(), format=fmt)
    except Exception as e:
        errors.append((p.as_posix(), str(e)))

if errors:
    print("[RDF PARSE] Found parsing errors:")
    for f, msg in errors:
        print(f"  - {f}: {msg}")
    sys.exit(1)

print("[RDF PARSE] OK")
