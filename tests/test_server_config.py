"""Tests for server/config.py"""
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from server.config import load_config, ServerConfig


def test_load_config_reads_repo_path():
    tmp_dir = Path(tempfile.mkdtemp())
    config_path = tmp_dir / "config.yaml"
    config_path.write_text("rust_sitemapper_repo: /tmp/fake-repo\n", encoding="utf-8")
    cfg = load_config(config_path)
    assert cfg.rust_sitemapper_repo == Path("/tmp/fake-repo")
    print("PASS")


def test_load_config_missing_file_raises():
    missing = Path(tempfile.mkdtemp()) / "nope.yaml"
    try:
        load_config(missing)
        raise AssertionError("expected FileNotFoundError")
    except FileNotFoundError:
        pass
    print("PASS")


def test_load_config_missing_key_raises():
    tmp_dir = Path(tempfile.mkdtemp())
    config_path = tmp_dir / "config.yaml"
    config_path.write_text("other_key: 1\n", encoding="utf-8")
    try:
        load_config(config_path)
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
    print("PASS")


def test_rust_sitemap_binary_prefers_newest_build():
    tmp_dir = Path(tempfile.mkdtemp())
    debug_bin = tmp_dir / "target" / "debug" / "rust_sitemap"
    release_bin = tmp_dir / "target" / "release" / "rust_sitemap"
    debug_bin.parent.mkdir(parents=True)
    release_bin.parent.mkdir(parents=True)
    debug_bin.write_text("debug")
    release_bin.write_text("release")
    now = time.time()
    os.utime(release_bin, (now - 100, now - 100))
    os.utime(debug_bin, (now, now))
    cfg = ServerConfig(rust_sitemapper_repo=str(tmp_dir))
    assert cfg.rust_sitemap_binary() == debug_bin
    print("PASS")


def test_rust_sitemap_binary_missing_raises():
    tmp_dir = Path(tempfile.mkdtemp())
    cfg = ServerConfig(rust_sitemapper_repo=str(tmp_dir))
    try:
        cfg.rust_sitemap_binary()
        raise AssertionError("expected FileNotFoundError")
    except FileNotFoundError:
        pass
    print("PASS")


def run_all_tests():
    print("\nserver.config Test Suite")
    tests = [
        test_load_config_reads_repo_path,
        test_load_config_missing_file_raises,
        test_load_config_missing_key_raises,
        test_rust_sitemap_binary_prefers_newest_build,
        test_rust_sitemap_binary_missing_raises,
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
