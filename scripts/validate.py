
#!/usr/bin/env python3
"""
Validate RDF data against SHACL shapes using pySHACL.

Usage examples:
  python scripts/validate.py     --data data/example-valid.ttl     --shapes shapes/shapes.ttl     --ontology ontologies/domain.ttl

Multiple --data arguments are allowed. Exits with non-zero code if not conformant.
"""
import argparse
import sys
from pathlib import Path
from rdflib import Graph
from pyshacl import validate


def load_graph(path: Path, public_id: str | None = None) -> Graph:
    g = Graph()
    fmt = None
    if path.suffix in (".ttl", ".turtle"):
        fmt = "turtle"
    elif path.suffix in (".nt", ".ntriples"):
        fmt = "nt"
    elif path.suffix in (".trig",):
        fmt = "trig"
    elif path.suffix in (".nq",):
        fmt = "nquads"
    g.parse(path.as_posix(), format=fmt, publicID=public_id)
    return g


def main():
    parser = argparse.ArgumentParser(description="Validate RDF data with SHACL")
    parser.add_argument("--data", "-d", action="append", required=True,
                        help="Path(s) to data graph(s). Repeat for multiple.")
    parser.add_argument("--shapes", "-s", required=True, help="Path to SHACL shapes graph.")
    parser.add_argument("--ontology", "-o", default=None, help="Optional ontology graph (OWL/RDFS) to help validation.")
    parser.add_argument("--inference", choices=["none", "rdfs", "owlrl"], default="rdfs",
                        help="Apply simple RDFS/OWL-RL inference during validation (default: rdfs).")
    parser.add_argument("--report-format", choices=["human", "turtle", "json-ld"], default="human",
                        help="Validation report format to print to stdout (RDF report is always written to build/).")
    parser.add_argument("--abort", action="store_true", help="Stop on first violation (faster).")

    args = parser.parse_args()

    data_graph = Graph()
    for dp in args.data:
        if any(ch in dp for ch in "*?[]"):
            for path in Path().glob(dp):
                data_graph += load_graph(path)
        else:
            data_graph += load_graph(Path(dp))

    shacl_graph = load_graph(Path(args.shapes))

    ont_graph = None
    if args.ontology:
        ont_graph = load_graph(Path(args.ontology))

    conforms, results_graph, results_text = validate(
        data_graph,
        shacl_graph=shacl_graph,
        ont_graph=ont_graph,
        inference=None if args.inference == "none" else args.inference,
        abort_on_first=args.abort,
        advanced=True,
        meta_shacl=True,
        inplace=False,
        allow_infos=True,
        allow_warnings=True,
    )

    # Write RDF results graph (Turtle) to build/
    build_dir = Path("build")
    build_dir.mkdir(parents=True, exist_ok=True)
    out_file = build_dir / "validation-report.ttl"
    results_graph.serialize(destination=out_file.as_posix(), format="turtle")

    if args.report_format == "human":
        print(results_text)
    elif args.report_format == "turtle":
        print(results_graph.serialize(format="turtle").decode())
    else:
        print(results_graph.serialize(format="json-ld", indent=2).decode())

    sys.exit(0 if conforms else 1)


if __name__ == "__main__":
    main()
