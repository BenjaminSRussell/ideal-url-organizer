import json
from pathlib import Path
from src.export.seeds import seeds_from_organized, write_seeds_jsonl, load_organized_json


def test_seeds_round_trip(tmp_path):
    organized = {
        "example.com": [{"url": "https://example.com/a"}, {"url": "https://example.com/b"}],
        "other.test": [{"url": "https://other.test/"}],
    }
    rows = seeds_from_organized(organized, method="by_domain")
    assert len(rows) == 3
    assert all("url" in r and "priority" in r and "labels" in r for r in rows)
    out = tmp_path / "seeds.jsonl"
    assert write_seeds_jsonl(rows, out) == 3
    loaded = [json.loads(line) for line in out.read_text().splitlines()]
    assert loaded[0]["method"] == "by_domain"
    # reload organized fixture
    org_path = tmp_path / "org.json"
    org_path.write_text(json.dumps(organized))
    assert set(load_organized_json(org_path)) == {"example.com", "other.test"}
