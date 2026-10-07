"""Auto-generated-friendly method registry from organizers package (#6)."""
from __future__ import annotations

import ast
import importlib
import pkgutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterator, List, Optional


ORG_DIR = Path(__file__).resolve().parent


@dataclass
class MethodInfo:
    id: str
    module: str
    description: str
    status: str  # implemented | stub
    class_name: str = ""


def _module_status(path: Path) -> str:
    """Heuristic: stubs live under organizers/stubs or file mentions NotImplemented/stub."""
    if "stubs" in path.parts:
        return "stub"
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return "implemented"
    lower = text.lower()
    if "notimplementederror" in lower or "status = \"stub\"" in lower or "TODO: stub" in lower:
        return "stub"
    return "implemented"


def _class_and_doc(path: Path) -> tuple[str, str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return "", ""
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            doc = ast.get_docstring(node) or ""
            # first line of docstring or class name
            desc = (doc.strip().splitlines() or [node.name])[0].strip()
            return node.name, desc
    return "", path.stem.replace("_", " ")


def iter_method_modules() -> Iterator[Path]:
    for path in sorted(ORG_DIR.glob("method_*.py")):
        yield path
    stubs = ORG_DIR / "stubs"
    if stubs.is_dir():
        for path in sorted(stubs.glob("*.py")):
            if path.name.startswith("_"):
                continue
            yield path


def discover_methods() -> List[MethodInfo]:
    methods: List[MethodInfo] = []
    for path in iter_method_modules():
        rel = path.relative_to(ORG_DIR.parent)
        mod = ".".join(("src",) + rel.with_suffix("").parts)
        mid = path.stem
        if path.parent.name == "stubs":
            mid = f"stub_{path.stem}"
        class_name, desc = _class_and_doc(path)
        status = _module_status(path)
        if not desc:
            desc = mid.replace("_", " ")
        methods.append(
            MethodInfo(
                id=mid,
                module=mod,
                description=desc,
                status=status,
                class_name=class_name,
            )
        )
    return methods


def render_methods_md(methods: Optional[List[MethodInfo]] = None) -> str:
    methods = methods if methods is not None else discover_methods()
    lines = [
        "# Organization methods registry",
        "",
        "Auto-generated from `src/organizers/` — do not edit by hand. "
        "Regenerate with `python -m src.organizers.registry`.",
        "",
        "| id | module | status | description |",
        "|----|--------|--------|-------------|",
    ]
    for m in methods:
        desc = m.description.replace("|", "\\|")
        lines.append(f"| `{m.id}` | `{m.module}` | {m.status} | {desc} |")
    lines.append("")
    lines.append(f"_Total: {len(methods)} methods "
                 f"({sum(1 for m in methods if m.status=='implemented')} implemented, "
                 f"{sum(1 for m in methods if m.status=='stub')} stub)._")
    lines.append("")
    return "\n".join(lines)


def write_methods_md(out: Path | None = None) -> Path:
    out = out or (ORG_DIR.parents[1] / "docs" / "METHODS.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_methods_md(), encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    import argparse
    import json

    p = argparse.ArgumentParser(prog="python -m src.organizers.registry")
    p.add_argument("--json", action="store_true")
    p.add_argument("--write", action="store_true", help="Write docs/METHODS.md")
    p.add_argument("--check", action="store_true", help="Fail if METHODS.md drifts")
    args = p.parse_args(argv)
    methods = discover_methods()
    if args.json:
        print(json.dumps([asdict(m) for m in methods], indent=2))
        return 0
    md = render_methods_md(methods)
    path = ORG_DIR.parents[1] / "docs" / "METHODS.md"
    if args.check:
        if not path.exists() or path.read_text(encoding="utf-8") != md:
            print("METHODS.md drift — run: python -m src.organizers.registry --write", flush=True)
            return 1
        print("METHODS.md up to date")
        return 0
    if args.write:
        write_methods_md(path)
        print(f"wrote {path}")
        return 0
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
