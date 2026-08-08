"""Tests for server/jobs.py"""
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from server.jobs import (
    build_argv,
    start_crawl,
    parse_latest_progress,
    is_pid_alive,
    get_job_status,
    list_jobs,
)


class FakeConfig:
    def __init__(self, binary_path, repo_dir):
        self._binary_path = binary_path
        self.rust_sitemapper_repo = repo_dir

    def rust_sitemap_binary(self):
        return self._binary_path


def _write_fake_binary(tmp_dir: Path, extra_lines: str = "") -> Path:
    script = tmp_dir / "fake_rust_sitemap.sh"
    script.write_text(
        "#!/bin/bash\n"
        "echo '  PROGRESS REPORT (5s elapsed, 25s remaining)'\n"
        "echo '  URLs Processed: 10 (2.0/sec) | Success: 8 | Failed: 1 | Timeout: 1'\n"
        "echo '  Success Rate: 80.0% | Total Discovered: 20'\n"
        + extra_lines,
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


def test_build_argv_maps_known_flags():
    argv = build_argv(Path("/bin/rust_sitemap"), {
        "start_url": "https://example.com",
        "workers": 128,
        "ignore_robots": True,
        "enable_redis": False,
        "max_urls": None,
    })
    assert argv[0] == "/bin/rust_sitemap"
    assert argv[1] == "crawl"
    assert "--start-url" in argv and argv[argv.index("--start-url") + 1] == "https://example.com"
    assert "--workers" in argv and argv[argv.index("--workers") + 1] == "128"
    assert "--ignore-robots" in argv
    assert "--enable-redis" not in argv
    assert "--max-urls" not in argv
    print("PASS")


def test_parse_latest_progress_picks_last_block():
    log = (
        "  PROGRESS REPORT (5s elapsed, 25s remaining)\n"
        "  URLs Processed: 10 (2.0/sec) | Success: 8 | Failed: 1 | Timeout: 1\n"
        "  Success Rate: 80.0% | Total Discovered: 20\n"
        "  PROGRESS REPORT (10s elapsed, 20s remaining)\n"
        "  URLs Processed: 30 (3.0/sec) | Success: 25 | Failed: 3 | Timeout: 2\n"
        "  Success Rate: 83.3% | Total Discovered: 50\n"
    )
    progress = parse_latest_progress(log)
    assert progress["elapsed_secs"] == 10
    assert progress["processed"] == 30
    assert progress["rate_per_sec"] == 3.0
    assert progress["success"] == 25
    assert progress["failed"] == 3
    assert progress["timeout"] == 2
    assert progress["success_rate_pct"] == 83.3
    assert progress["discovered"] == 50
    print("PASS")


def test_parse_latest_progress_returns_none_when_absent():
    assert parse_latest_progress("nothing here\n") is None
    print("PASS")


def test_is_pid_alive_true_for_self():
    import os
    assert is_pid_alive(os.getpid()) is True
    print("PASS")


def test_is_pid_alive_false_after_process_exits():
    proc = subprocess.Popen(["true"])
    proc.wait()
    assert is_pid_alive(proc.pid) is False
    print("PASS")


def test_start_crawl_reaches_completed_state():
    tmp_dir = Path(tempfile.mkdtemp())
    binary = _write_fake_binary(
        tmp_dir, extra_lines="echo '   GRACEFUL SHUTDOWN: Crawl Complete'\n"
    )
    cfg = FakeConfig(binary_path=binary, repo_dir=tmp_dir)
    jobs_dir = tmp_dir / "jobs"

    job_id = start_crawl(cfg, {"start_url": "https://example.com"}, jobs_dir)

    deadline = time.time() + 5
    status = None
    while time.time() < deadline:
        status = get_job_status(job_id, jobs_dir)
        if status["state"] == "completed":
            break
        time.sleep(0.1)

    assert status["state"] == "completed"
    assert status["progress"]["discovered"] == 20
    assert status["params"]["start_url"] == "https://example.com"

    jobs = list_jobs(jobs_dir)
    assert any(j["id"] == job_id for j in jobs)
    print("PASS")


def test_get_job_status_unknown_id_raises():
    tmp_dir = Path(tempfile.mkdtemp())
    try:
        get_job_status("does-not-exist", tmp_dir)
        raise AssertionError("expected FileNotFoundError")
    except FileNotFoundError:
        pass
    print("PASS")


def run_all_tests():
    print("\nserver.jobs Test Suite")
    tests = [
        test_build_argv_maps_known_flags,
        test_parse_latest_progress_picks_last_block,
        test_parse_latest_progress_returns_none_when_absent,
        test_is_pid_alive_true_for_self,
        test_is_pid_alive_false_after_process_exits,
        test_start_crawl_reaches_completed_state,
        test_get_job_status_unknown_id_raises,
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
