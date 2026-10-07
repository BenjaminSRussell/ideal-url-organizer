# CPU CI stub embedder

Default GitHub Actions CI installs `requirements-ci.txt` (no torch / sentence-transformers / CUDA / MLX).

Set `IDEAL_URL_STUB_EMBEDDER=1` (or pass `use_stub=True`) so `BySemanticSimilarityOrganizer` uses `StubSentenceEmbedder` — a deterministic hash embedding for clustering tests.

- Mark real-model tests with `@pytest.mark.gpu` or `@pytest.mark.mlx`.
- Default workflow runs `pytest -m "not gpu and not mlx"`.
- Optional nightly macOS/MLX job can be added later for full model coverage.
