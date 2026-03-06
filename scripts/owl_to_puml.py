
#!/usr/bin/env python3
"""
Generate PlantUML class diagrams from OWL/Turtle.

Usage:
  python scripts/owl_to_puml.py     --input ontologies/domain.ttl     --output diagrams/domain.puml

Notes:
- Maps owl:Class -> UML classes
- rdfs:subClassOf -> inheritance
- owl:DatatypeProperty (with rdfs:domain/range xsd:*) -> attributes
- owl:ObjectProperty (with rdfs:domain/range) -> associations
- owl:disjointWith -> note "A ⟂ B"
- Simple OWL restrictions (min/max/cardinality) on subclass axioms -> multiplicities
"""
from rdflib import Graph, Namespace, RDF, RDFS, OWL, XSD
from rdflib.term import BNode
from pathlib import Path
import argparse
import re

# Helper: extract a compact name for display
def short(n):
    s = str(n)
    if "#" in s:
        return s.split("#")[-1]
    if "/" in s:
        return s.rstrip("/").split("/")[-1]
    return s

# Helper: format multiplicity
def mult_str(minc, maxc):
    def to_m(v):
        if v is None:
            return None
        try:
            iv = int(v)
            return str(iv)
        except Exception:
            return None
    a = to_m(minc)
    b = to_m(maxc)
    if a is None and b is None:
        return None
    if a is None:
        a = "0"
    if b is None:
        b = "*"
    return f"{a}..{b}" if a != b else a


def parse(input_paths, output_path):
    g = Graph()
    for inp in input_paths:
        g.parse(inp)

    classes = set()
    inherits = []
    disjoints = set()
    attributes = {}
    associations = [] # (domain, range, prop, mult)
    restrictions = {} # (class, prop) -> {min,max,exact,range}

    # Classes
    for c in g.subjects(RDF.type, OWL.Class):
        classes.add(c)
    for child, parent in g.subject_objects(RDFS.subClassOf):
        if isinstance(child, BNode):
            continue
        classes.add(child)
        if not isinstance(parent, BNode):
            classes.add(parent)
            inherits.append((child, parent))

    # Disjoint
    for a, b in g.subject_objects(OWL.disjointWith):
        if not isinstance(a, BNode) and not isinstance(b, BNode):
            classes.update([a, b])
            disjoints.add(frozenset((a, b)))

    # Datatype properties -> attributes
    for p in g.subjects(RDF.type, OWL.DatatypeProperty):
        doms = list(g.objects(p, RDFS.domain)) or [None]
        rngs = list(g.objects(p, RDFS.range)) or [XSD.string]
        p_name = short(p)
        dtype = short(rngs[0]) if rngs else "string"
        for d in doms:
            if d is None:
                continue
            classes.add(d)
            attributes.setdefault(d, []).append((p_name, dtype))

    # Object properties -> associations
    for p in g.subjects(RDF.type, OWL.ObjectProperty):
        p_name = short(p)
        doms = list(g.objects(p, RDFS.domain))
        rngs = list(g.objects(p, RDFS.range))
        for d in doms:
            for r in rngs:
                classes.update([d, r])
                associations.append((d, r, p_name, None))

    # Restrictions for multiplicity
    for cls, sup in g.subject_objects(RDFS.subClassOf):
        if isinstance(sup, BNode) and (sup, RDF.type, OWL.Restriction) in g:
            on_prop = next(g.objects(sup, OWL.onProperty), None)
            if on_prop is None:
                continue
            minc = next(g.objects(sup, OWL.minCardinality), None)
            maxc = next(g.objects(sup, OWL.maxCardinality), None)
            exact = next(g.objects(sup, OWL.cardinality), None)
            some = next(g.objects(sup, OWL.someValuesFrom), None)
            allv = next(g.objects(sup, OWL.allValuesFrom), None)
            info = restrictions.setdefault((cls, on_prop), {"min": None, "max": None, "exact": None, "range": None})
            if exact is not None:
                info["min"] = int(exact.toPython())
                info["max"] = int(exact.toPython())
            if minc is not None:
                info["min"] = int(minc.toPython())
            if maxc is not None:
                info["max"] = int(maxc.toPython())
            info["range"] = some or allv or info.get("range")

    # Index ranges for properties
    prop_ranges = {}
    for p in g.subjects(RDF.type, OWL.ObjectProperty):
        prop_ranges[p] = list(g.objects(p, RDFS.range))

    # Associations implied by restrictions
    for (cls, prop), info in restrictions.items():
        rngs = prop_ranges.get(prop, [])
        if info.get("range") is not None:
            rngs = [info["range"]]
        mult = mult_str(info.get("min"), info.get("max"))
        for r in rngs:
            if isinstance(r, BNode):
                continue
            classes.update([cls, r])
            associations.append((cls, r, short(prop), mult))

    # Attach multiplicities to existing associations where possible
    assoc_enriched = []
    for d, r, p_name, m in associations:
        if m is not None:
            assoc_enriched.append((d, r, p_name, m))
            continue
        candidate_props = [p for p in g.subjects(RDF.type, OWL.ObjectProperty) if short(p) == p_name]
        mult = None
        for p in candidate_props:
            info = restrictions.get((d, p))
            if info:
                mult = mult_str(info.get("min"), info.get("max"))
                if mult:
                    break
        assoc_enriched.append((d, r, p_name, mult))

    # Emit PlantUML
    lines = []
    lines.append("@startuml")
    lines.append("hide empty members")
    lines.append("skinparam classAttributeIconSize 0")
    lines.append("title Ontology Class Diagram")

    for c in sorted(classes, key=lambda x: short(x).lower()):
        cname = short(c)
        lines.append(f"class {cname} {{")
        for (pname, dtype) in sorted(attributes.get(c, [])):
            dtype_s = re.sub(r"[^\w\*\.]+", "", dtype)
            pname_s = re.sub(r"[^\w]+", "_", pname)
            lines.append(f"  {pname_s} : {dtype_s}")
        lines.append("}")

    for child, parent in inherits:
        lines.append(f"{short(child)} --|> {short(parent)}")

    for d, r, pname, mult in assoc_enriched:
        right = f' "{mult}"' if mult else ' "*"'
        lines.append(f"{short(d)} --{right} {short(r)} : {pname}")

    idx = 1
    for pair in sorted(disjoints, key=lambda s: sorted([short(x) for x in s])):
        a, b = list(pair)
        nid = f"N{idx}"
        lines.append(f"note "{short(a)} ⟂ {short(b)}" as {nid}")
        lines.append(f"{short(a)} .. {nid}")
        lines.append(f"{short(b)} .. {nid}")
        idx += 1

    lines.append("@enduml")

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("
".join(lines), encoding="utf-8")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", "-i", action="append", required=False, default=["ontologies/domain.ttl"],
                    help="Input Turtle file(s). Repeat to merge multiple ontologies.")
    ap.add_argument("--output", "-o", default="diagrams/domain.puml", help="Output PlantUML file path.")
    args = ap.parse_args()
    parse(args.input, args.output)
