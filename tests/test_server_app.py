"""Tests for server/app.py"""
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient

from server.app import app, get_config, get_jobs_dir, get_results_dir


class FakeConfig:
    def __init__(self, binary_path, repo_dir):
        self._binary_path = binary_path
        self.rust_sitemapper_repo = repo_dir

    def rust_sitemap_binary(self):
        return self._binary_path


def _write_fake_binary(tmp_dir: Path) -> Path:
    # Matches the real binary's exact PROGRESS REPORT layout
    # (src/bfs_crawler.rs:808-818 in rust-sitemapper) -- see the identical
    # fixture in tests/test_jobs.py for why the separator lines matter.
    script = tmp_dir / "fake_rust_sitemap.sh"
    script.write_text(
        "#!/bin/bash\n"
        "echo\n"
        "echo '================================================================================'\n"
        "echo '  PROGRESS REPORT (5s elapsed, 25s remaining)'\n"
        "echo '================================================================================'\n"
        "echo '  URLs Processed: 10 (2.0/sec) | Success: 8 | Failed: 1 | Timeout: 1'\n"
        "echo '  Success Rate: 80.0% | Total Discovered: 20'\n"
        "echo '  Frontier: 5 queued | 1 hosts | 1 with work | 0 in backoff'\n"
        "echo '================================================================================'\n"
        "echo '   GRACEFUL SHUTDOWN: Crawl Complete'\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def test_health_returns_ok():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
    print("PASS")


def test_overview_on_empty_results_dir():
    tmp_results = Path(tempfile.mkdtemp()) / "does-not-exist"
    app.dependency_overrides[get_results_dir] = lambda: tmp_results
    try:
        client = TestClient(app)
        resp = client.get("/overview")
        assert resp.status_code == 200
        assert resp.json()["rollup"]["site_count"] == 0
    finally:
        app.dependency_overrides.clear()
    print("PASS")


def test_site_detail_404_for_unknown_site():
    tmp_results = Path(tempfile.mkdtemp())
    app.dependency_overrides[get_results_dir] = lambda: tmp_results
    try:
        client = TestClient(app)
        resp = client.get("/sites/does-not-exist-xyz")
        assert resp.status_code == 404
    finally:
        app.dependency_overrides.clear()
    print("PASS")


def test_create_crawl_and_lifecycle():
    tmp_dir = Path(tempfile.mkdtemp())
    binary = _write_fake_binary(tmp_dir)
    fake_cfg = FakeConfig(binary_path=binary, repo_dir=tmp_dir)
    jobs_dir = tmp_dir / "jobs"

    app.dependency_overrides[get_config] = lambda: fake_cfg
    app.dependency_overrides[get_jobs_dir] = lambda: jobs_dir
    try:
        client = TestClient(app)
        resp = client.post("/crawls", json={"start_url": "https://example.com"})
        assert resp.status_code == 200
        job_id = resp.json()["id"]

        deadline = time.time() + 5
        state = None
        while time.time() < deadline:
            status_resp = client.get(f"/crawls/{job_id}")
            assert status_resp.status_code == 200
            state = status_resp.json()["state"]
            if state == "completed":
                break
            time.sleep(0.1)
        assert state == "completed"

        list_resp = client.get("/crawls")
        assert any(j["id"] == job_id for j in list_resp.json())
    finally:
        app.dependency_overrides.clear()
    print("PASS")


def test_crawl_status_404_for_unknown_job():
    tmp_dir = Path(tempfile.mkdtemp())
    app.dependency_overrides[get_jobs_dir] = lambda: tmp_dir
    try:
        client = TestClient(app)
        resp = client.get("/crawls/does-not-exist")
        assert resp.status_code == 404
    finally:
        app.dependency_overrides.clear()
    print("PASS")


def test_import_crawl_404_for_unknown_job():
    tmp_dir = Path(tempfile.mkdtemp())
    fake_cfg = FakeConfig(binary_path=tmp_dir / "unused", repo_dir=tmp_dir)
    app.dependency_overrides[get_config] = lambda: fake_cfg
    app.dependency_overrides[get_jobs_dir] = lambda: tmp_dir
    try:
        client = TestClient(app)
        resp = client.post("/crawls/does-not-exist/import")
        assert resp.status_code == 404
    finally:
        app.dependency_overrides.clear()
    print("PASS")


def test_import_crawl_409_when_job_not_completed():
    tmp_dir = Path(tempfile.mkdtemp())
    binary = _write_fake_binary(tmp_dir)
    fake_cfg = FakeConfig(binary_path=binary, repo_dir=tmp_dir)
    jobs_dir = tmp_dir / "jobs"

    app.dependency_overrides[get_config] = lambda: fake_cfg
    app.dependency_overrides[get_jobs_dir] = lambda: jobs_dir
    try:
        client = TestClient(app)
        create_resp = client.post("/crawls", json={"start_url": "https://example.com"})
        job_id = create_resp.json()["id"]
        resp = client.post(f"/crawls/{job_id}/import")
        # Either the job is still running (409) or it raced to completion
        # and hit the next gate (sitemap.jsonl won't exist for a fake
        # binary that never wrote one, giving 404) -- both are the
        # "not importable yet" outcome this test cares about, never a
        # bare 500 or a false 200.
        assert resp.status_code in (404, 409)
    finally:
        app.dependency_overrides.clear()
    print("PASS")


def run_all_tests():
    print("\nserver.app Test Suite")
    tests = [
        test_health_returns_ok,
        test_overview_on_empty_results_dir,
        test_site_detail_404_for_unknown_site,
        test_create_crawl_and_lifecycle,
        test_crawl_status_404_for_unknown_job,
        test_import_crawl_404_for_unknown_job,
        test_import_crawl_409_when_job_not_completed,
    ]
    passed = failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\nFAIL: {test.__name__}\n  Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    print(f"\nPassed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
