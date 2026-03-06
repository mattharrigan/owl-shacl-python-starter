
#!/usr/bin/env python3
"""
Load RDF files and emit **sorted N-Triples** into build/ for stable, canonical diffs.
This does not overwrite sources; it writes *.nt into build/ keeping lexicographic order.
"""
import argparse
from pathlib import Path
from rdflib import Graph


def to_sorted_nt(in_path: Path, out_dir: Path) -> Path:
    g = Graph()
    fmt = None
    if in_path.suffix in (".ttl", ".turtle"):
        fmt = "turtle"
    elif in_path.suffix in (".trig",):
        fmt = "trig"
    elif in_path.suffix in (".nq",):
        fmt = "nquads"
    elif in_path.suffix in (".nt", ".ntriples"):
        fmt = "nt"
    g.parse(in_path.as_posix(), format=fmt)
    nt_bytes = g.serialize(format="nt")
    # rdflib returns bytes; split and sort
    lines = nt_bytes.decode().splitlines()
    lines = [ln for ln in lines if ln.strip()]
    lines.sort()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (in_path.stem + ".nt")
    out_path.write_text("
".join(lines) + "
", encoding="utf-8")
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", help="RDF files or globs to format (ttl, trig, nt, nq)")
    ap.add_argument("--out", default="build/format", help="Output directory (default: build/format)")
    args = ap.parse_args()

    out_dir = Path(args.out)
    matched = []
    for pattern in args.paths:
        has_glob = any(ch in pattern for ch in "*?[]")
        if has_glob:
            matched += list(Path().glob(pattern))
        else:
            matched.append(Path(pattern))

    for p in matched:
        if p.is_file():
            out_path = to_sorted_nt(p, out_dir)
            print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
