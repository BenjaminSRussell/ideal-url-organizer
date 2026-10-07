"""Golden-set eval harness (#4)."""
from pathlib import Path

from src.eval.harness import PRIMARY_METHOD, evaluate_methods, main

GOLDEN = Path(__file__).parent / "fixtures" / "urls.jsonl"


def test_primary_method_accuracy():
    report = evaluate_methods(GOLDEN, methods=[PRIMARY_METHOD])
    m = report["metrics"][0]
    assert m["accuracy"] >= 0.99
    assert m["n"] >= 5


def test_eval_cli_exit_zero(tmp_path):
    code = main([
        "--golden", str(GOLDEN),
        "--db", str(tmp_path / "eval.sqlite"),
        "--html", str(tmp_path / "d.html"),
        "--fail-under", "0.99",
    ])
    assert code == 0
    assert (tmp_path / "d.html").exists()
    assert (tmp_path / "eval.sqlite").exists()


def test_disagreement_html_lists_urls(tmp_path):
    report = evaluate_methods(GOLDEN)
    from src.eval.harness import write_disagreement_html
    out = tmp_path / "d.html"
    write_disagreement_html(report, out)
    body = out.read_text()
    assert "www.example.com" in body
    assert "method_01_by_domain" in body
