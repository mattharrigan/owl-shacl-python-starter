
# OWL + SHACL Starter (Python + pySHACL) with Automatic PlantUML

A minimal, Git-friendly starter for modeling with **OWL (Turtle)** and **SHACL**, with:
- Local validation via **pySHACL**
- **Pre-commit hooks** (syntax, SHACL, diagram regeneration)
- **Automatic PlantUML** diagram generation (.puml) and **CI-rendered SVG** artifacts

## Repo Structure

```
.
├─ ontologies/
│  └─ domain.ttl           # Example OWL ontology (Turtle)
├─ shapes/
│  └─ shapes.ttl           # Example SHACL shapes (Turtle)
├─ data/
│  ├─ example-valid.ttl    # Sample conformant data
│  └─ example-invalid.ttl  # Sample non-conformant data
├─ diagrams/
│  ├─ domain.puml          # Generated PlantUML (text)
│  └─ out/                  # Rendered diagrams (SVG) in CI
├─ scripts/
│  ├─ validate.py          # Validate data against SHACL
│  ├─ format_rdf.py        # Optional: sorted N-Triples output
│  ├─ ttl_parse_check.py   # Hook: parse TTL files
│  └─ owl_to_puml.py       # Generate PlantUML from OWL/Turtle
├─ .github/workflows/
│  └─ ontology.yml         # CI: validate + build diagrams
├─ .vscode/
│  ├─ settings.json
│  └─ tasks.json
├─ build/                  # Validation reports, formatted RDF
├─ .pre-commit-config.yaml
├─ requirements.txt
└─ .gitignore
```

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scriptsctivate
pip install -r requirements.txt

# Validate sample datasets
python scripts/validate.py       --data data/example-valid.ttl       --shapes shapes/shapes.ttl       --ontology ontologies/domain.ttl

# Generate PlantUML from ontology
python scripts/owl_to_puml.py --input ontologies/domain.ttl --output diagrams/domain.puml

# Install git hooks
pre-commit install
```

## UML diagrams (automatic PlantUML)

The script `scripts/owl_to_puml.py` maps:
- **Classes**: `owl:Class` → UML classes
- **Inheritance**: `rdfs:subClassOf` → generalization
- **Attributes**: `owl:DatatypeProperty` with `rdfs:domain` + `rdfs:range` (xsd types)
- **Associations**: `owl:ObjectProperty` with `rdfs:domain` + `rdfs:range`
- **Cardinalities**: Simple `owl:Restriction` (`min`/`max`/`cardinality`) on subclass axioms → multiplicities
- **Disjointness**: `owl:disjointWith` → note `A ⟂ B`

In CI, we also render **SVG** with PlantUML and upload as artifacts.

## Pre-commit hooks

```bash
pip install -r requirements.txt
pre-commit install
# Run on all files
pre-commit run --all-files
```

Hooks included:
- Hygiene: trailing whitespace, EOF newline, YAML checks
- RDF/Turtle parse check (via `rdflib`)
- SHACL validation of `data/*.ttl`
- **OWL→PlantUML** generation (fails commit if regenerated `.puml` differs)

## License
MIT
