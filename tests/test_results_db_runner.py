"""Results DB + unified runner (#3/#5)."""
from __future__ import annotations

from pathlib import Path

from src.results.db import ResultsDB
from src.results.runner import run_methods


def test_results_db_assignments(tmp_path: Path):
    db = ResultsDB(tmp_path / "r.db")
    db.add_assignment("method_01_by_domain", "https://a.example/", label="a.example")
    db.add_assignment("method_01_by_domain", "https://b.example/", label="b.example")
    assert db.count_assignments("method_01_by_domain") == 2
    db.close()


def test_run_two_methods_into_db(tmp_path: Path):
    urls = ["https://alpha.example/x", "https://beta.example/y"]
    db_path = tmp_path / "results.db"
    summary = run_methods(
        urls,
        ["method_01_by_domain", "method_08_by_protocol"],
        db_path,
        export_fs=False,
        project_root=Path(__file__).resolve().parents[1],
    )
    assert summary["results"]["method_01_by_domain"] == "success"
    assert summary["results"]["method_08_by_protocol"] == "success"
    assert summary["assignments"] >= 2
    db = ResultsDB(db_path)
    assert db.count_assignments() >= 2
    db.close()
