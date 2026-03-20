# Getting Started Guide: OWL + SHACL Python Starter

This guide will help you get up and running with the OWL + SHACL Python Starter repo, and walk you through adding a new OWL class with attributes and SHACL constraints. It also covers recommended git workflow best practices.

---

## 1. Setup

```bash
# Create and activate a virtual environment
python -m venv .venv
# On Unix/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install
```

---

## 2. Repo Structure Overview

- [`ontologies/domain.ttl`](ontologies/domain.ttl): Main OWL ontology (Turtle)
- [`shapes/shapes.ttl`](shapes/shapes.ttl): SHACL shapes for validation
- [`data/`](data/): Example data files
- [`scripts/`](scripts/): Validation, diagram generation, and utility scripts
- [`diagrams/`](diagrams/): Generated PlantUML and rendered SVG diagrams

---

## 3. Validating and Generating Diagrams

```bash
# Validate example data against SHACL and OWL
python scripts/validate.py --data data/example-valid.ttl --shapes shapes/shapes.ttl --ontology ontologies/domain.ttl

# Generate PlantUML diagram from ontology
python scripts/owl_to_puml.py --input ontologies/domain.ttl --output diagrams/domain.puml
```

---

## 4. Example: Adding a New OWL Class with Attributes and Constraints

Suppose you want to add a new class `ex:Project` with a string attribute `projectName` and a constraint that every Project must have a unique name.

### a. Update the Ontology ([`ontologies/domain.ttl`](ontologies/domain.ttl))

Add the following:

```turtle
ex:Project a owl:Class .

ex:projectName a owl:DatatypeProperty ;
  rdfs:domain ex:Project ;
  rdfs:range xsd:string .
```

### b. Add SHACL Constraints ([`shapes/shapes.ttl`](shapes/shapes.ttl))

Add a shape to require every Project to have a `projectName`:

```turtle
ex:ProjectShape a sh:NodeShape ;
  sh:targetClass ex:Project ;
  sh:property [
    sh:path ex:projectName ;
    sh:datatype xsd:string ;
    sh:minCount 1 ;
    sh:maxCount 1 ;
  ] .
```

To enforce uniqueness, you can add a constraint (note: SHACL core does not enforce global uniqueness, but you can use sh:uniqueLang or custom SPARQL constraints for advanced cases).

### c. Add Example Data ([`data/example-valid.ttl`](data/example-valid.ttl))

```turtle
ex:myProject a ex:Project ;
  ex:projectName "Apollo" .
```

### d. Validate

```bash
python scripts/validate.py --data data/example-valid.ttl --shapes shapes/shapes.ttl --ontology ontologies/domain.ttl
```

### e. Regenerate Diagrams

```bash
python scripts/owl_to_puml.py --input ontologies/domain.ttl --output diagrams/domain.puml
```

---

## 5. Git Workflow Best Practices

1. **Create a new branch for your feature or fix:**
   ```bash
   git checkout -b feature/add-project-class
   ```
2. **Make your changes and commit:**
   ```bash
   git add ontologies/domain.ttl shapes/shapes.ttl data/example-valid.ttl
   git commit -m "Add Project class with projectName attribute and SHACL constraints"
   ```
3. **Push your branch to GitHub:**
   ```bash
   git push origin feature/add-project-class
   ```
4. **Open a Pull Request (PR):**
   - Go to your repository on GitHub
   - Click "Compare & pull request"
   - Fill in details and submit for review

**Tips:**
- Keep branches focused and small for easier review.
- Use descriptive commit messages.
- Run pre-commit and validation scripts before pushing.
- Address review comments promptly.

---

## 6. Resources
- [OWL 2 Primer](https://www.w3.org/TR/owl2-primer/)
- [SHACL Specification](https://www.w3.org/TR/shacl/)
- [pySHACL Documentation](https://pyshacl.readthedocs.io/)

---

You're ready to start modeling and validating ontologies with this starter kit!
