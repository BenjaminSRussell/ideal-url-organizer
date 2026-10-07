"""Method registry discovery (#6)."""
from pathlib import Path

from src.organizers.registry import discover_methods, render_methods_md, write_methods_md


def test_discovers_method_modules():
    methods = discover_methods()
    ids = {m.id for m in methods}
    assert "method_01_by_domain" in ids
    assert any(m.status == "implemented" for m in methods)


def test_methods_md_roundtrip(tmp_path: Path):
    out = tmp_path / "METHODS.md"
    write_methods_md(out)
    text = out.read_text(encoding="utf-8")
    assert "| id |" in text
    assert "method_01_by_domain" in text
    assert render_methods_md() 
