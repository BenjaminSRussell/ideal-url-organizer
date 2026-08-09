"""Tests for server/jobs.py"""
import json
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
    parse_completion_summary,
    is_pid_alive,
    get_job_status,
    list_jobs,
    _read_log_tail,
)


class FakeConfig:
    def __init__(self, binary_path, repo_dir):
        self._binary_path = binary_path
        self.rust_sitemapper_repo = repo_dir

    def rust_sitemap_binary(self):
        return self._binary_path


def _write_fake_binary(tmp_dir: Path, extra_lines: str = "") -> Path:
    # Reproduces the real rust_sitemap binary's exact PROGRESS REPORT layout
    # (src/bfs_crawler.rs:808-818 in the rust-sitemapper repo): a `====`
    # separator line between the elapsed-time line and the URLs-Processed
    # line, and a trailing Frontier line + separator. PROGRESS_BLOCK_RE must
    # match this real shape, not a simplified one, or the regex can pass
    # tests while never matching a genuine crawl's output.
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
    # Matches the real binary's exact layout (src/bfs_crawler.rs:808-818):
    # a `====` separator between the elapsed-time line and URLs Processed,
    # and a trailing Frontier line + separator after Total Discovered.
    log = (
        "\n"
        "================================================================================\n"
        "  PROGRESS REPORT (5s elapsed, 25s remaining)\n"
        "================================================================================\n"
        "  URLs Processed: 10 (2.0/sec) | Success: 8 | Failed: 1 | Timeout: 1\n"
        "  Success Rate: 80.0% | Total Discovered: 20\n"
        "  Frontier: 5 queued | 1 hosts | 1 with work | 0 in backoff\n"
        "================================================================================\n"
        "\n"
        "================================================================================\n"
        "  PROGRESS REPORT (10s elapsed, 20s remaining)\n"
        "================================================================================\n"
        "  URLs Processed: 30 (3.0/sec) | Success: 25 | Failed: 3 | Timeout: 2\n"
        "  Success Rate: 83.3% | Total Discovered: 50\n"
        "  Frontier: 8 queued | 2 hosts | 2 with work | 0 in backoff\n"
        "================================================================================\n"
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


def test_parse_completion_summary_matches_real_final_line():
    # This is the real binary's final summary line, formatted exactly as
    # src/main.rs:120-123 in the rust-sitemapper repo prints it, with
    # command_type == "Crawl" for the `crawl` subcommand (src/main.rs:241).
    # A crawl that processes very few URLs can exit without ever printing a
    # periodic PROGRESS REPORT block, but it always prints this line, so the
    # regex is checked against the genuine format rather than a fixture.
    log = (
        "   GRACEFUL SHUTDOWN: Crawl Complete\n"
        "Crawl complete: discovered 15235, processed 10755 (9582 success, "
        "767 failed, 406 timeout, 89.1% success rate), 1804s, data: ./data\n"
    )
    summary = parse_completion_summary(log)
    assert summary["discovered"] == 15235
    assert summary["processed"] == 10755
    assert summary["success"] == 9582
    assert summary["failed"] == 767
    assert summary["timeout"] == 406
    assert summary["success_rate_pct"] == 89.1
    assert summary["elapsed_secs"] == 1804
    assert abs(summary["rate_per_sec"] - (10755 / 1804)) < 1e-9
    print("PASS")


def test_parse_completion_summary_returns_none_without_summary():
    # A still-running crawl has printed progress blocks but no final line.
    log = (
        "  PROGRESS REPORT (5s elapsed, 25s remaining)\n"
        "  URLs Processed: 10 (2.0/sec) | Success: 8 | Failed: 1 | Timeout: 1\n"
    )
    assert parse_completion_summary(log) is None
    print("PASS")


def test_parse_completion_summary_handles_zero_elapsed():
    # duration_secs is a u64 and can legitimately be 0 for an instant crawl;
    # rate_per_sec must not divide by zero.
    log = (
        "Crawl complete: discovered 3, processed 1 (1 success, 0 failed, "
        "0 timeout, 100.0% success rate), 0s, data: ./data\n"
    )
    summary = parse_completion_summary(log)
    assert summary["elapsed_secs"] == 0
    assert summary["rate_per_sec"] == 0.0
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


def test_start_crawl_reaches_failed_state_when_child_dies_without_marker():
    # The child exits without ever printing the completion marker. Because we
    # never wait() on it, it becomes a zombie of this process -- and
    # os.kill(pid, 0) succeeds for zombies forever, so a raw pid check would
    # report "running" indefinitely and "failed" would be unreachable.
    # Polling the tracked Popen handle reaps it and reports the exit.
    tmp_dir = Path(tempfile.mkdtemp())
    script = tmp_dir / "dying_rust_sitemap.sh"
    script.write_text("#!/bin/bash\necho 'boom: crawl died'\nexit 1\n", encoding="utf-8")
    script.chmod(0o755)
    cfg = FakeConfig(binary_path=script, repo_dir=tmp_dir)
    jobs_dir = tmp_dir / "jobs"

    job_id = start_crawl(cfg, {"start_url": "https://example.com"}, jobs_dir)

    deadline = time.time() + 5
    status = None
    while time.time() < deadline:
        status = get_job_status(job_id, jobs_dir)
        if status["state"] == "failed":
            break
        time.sleep(0.1)

    assert status["state"] == "failed", f"expected failed, got {status['state']}"
    assert "boom: crawl died" in status["stderr_tail"]
    print("PASS")


def test_start_crawl_assigns_per_job_data_dir_when_unset():
    # Without this, every job inherits rust_sitemap's ./data default and
    # overwrites the previous job's sitemap.jsonl, so importing an older job
    # would silently import a newer crawl's data.
    tmp_dir = Path(tempfile.mkdtemp())
    binary = _write_fake_binary(
        tmp_dir, extra_lines="echo '   GRACEFUL SHUTDOWN: Crawl Complete'\n"
    )
    cfg = FakeConfig(binary_path=binary, repo_dir=tmp_dir)
    jobs_dir = tmp_dir / "jobs"

    job_id = start_crawl(cfg, {"start_url": "https://example.com"}, jobs_dir)
    status = get_job_status(job_id, jobs_dir)
    # The persisted params must record the directory actually used, since
    # import_crawl resolves the sitemap from status["params"]["data_dir"].
    assert status["params"]["data_dir"] == f"./data/jobs/{job_id}"

    argv = json.loads((jobs_dir / job_id / "meta.json").read_text(encoding="utf-8"))["argv"]
    assert argv[argv.index("--data-dir") + 1] == f"./data/jobs/{job_id}"

    # An explicit data_dir from the caller is left alone.
    other_id = start_crawl(
        cfg, {"start_url": "https://example.com", "data_dir": "./custom"}, jobs_dir
    )
    assert get_job_status(other_id, jobs_dir)["params"]["data_dir"] == "./custom"
    print("PASS")


def test_read_log_tail_returns_only_the_tail():
    tmp_dir = Path(tempfile.mkdtemp())
    log_path = tmp_dir / "log.txt"
    log_path.write_text("A" * 5000 + "TAIL-MARKER", encoding="utf-8")
    tail = _read_log_tail(log_path, max_bytes=100)
    assert len(tail) == 100
    assert tail.endswith("TAIL-MARKER")
    assert _read_log_tail(tmp_dir / "missing.txt") == ""
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
        test_parse_completion_summary_matches_real_final_line,
        test_parse_completion_summary_returns_none_without_summary,
        test_parse_completion_summary_handles_zero_elapsed,
        test_is_pid_alive_true_for_self,
        test_is_pid_alive_false_after_process_exits,
        test_start_crawl_reaches_completed_state,
        test_start_crawl_reaches_failed_state_when_child_dies_without_marker,
        test_start_crawl_assigns_per_job_data_dir_when_unset,
        test_read_log_tail_returns_only_the_tail,
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
