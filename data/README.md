# Data directory (gitignored)

Runtime crawl inputs and organizer outputs live here and are **not** tracked.

- Put crawl JSONL under `raw/` (e.g. `raw/urls.jsonl`).
- Organizer methods write under `processed/`.

For tests, use `tests/fixtures/sample_urls.jsonl` (tiny deterministic sample).
