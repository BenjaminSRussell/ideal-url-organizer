"""Crawl job lifecycle: launch a detached rust_sitemap subprocess, and
derive its status fresh from disk (meta.json + log file + pid liveness) on
every call. There is no in-memory job registry and nothing to reattach on
restart -- status is always recomputed from what's on disk.
"""
import json
import os
import re
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

JOBS_DIR = Path(__file__).resolve().parent / "jobs"

CRAWL_FLAG_MAP = {
    "start_url": "--start-url",
    "data_dir": "--data-dir",
    "preset": "--preset",
    "workers": "--workers",
    "user_agent": "--user-agent",
    "timeout": "--timeout",
    "ignore_robots": "--ignore-robots",
    "seeding_strategy": "--seeding-strategy",
    "enable_redis": "--enable-redis",
    "redis_url": "--redis-url",
    "lock_ttl": "--lock-ttl",
    "save_interval": "--save-interval",
    "max_urls": "--max-urls",
    "duration": "--duration",
}

PROGRESS_BLOCK_RE = re.compile(
    r"PROGRESS REPORT \((?P<elapsed>\d+)s elapsed.*?\)\s*\n"
    r"\s*URLs Processed: (?P<processed>\d+) \((?P<rate>[\d.]+)/sec\) \| "
    r"Success: (?P<success>\d+) \| Failed: (?P<failed>\d+) \| Timeout: (?P<timeout>\d+)\s*\n"
    r"\s*Success Rate: (?P<success_rate>[\d.]+)% \| Total Discovered: (?P<discovered>\d+)"
)
COMPLETE_RE = re.compile(r"GRACEFUL SHUTDOWN: Crawl Complete")


def build_argv(binary: Path, params: dict) -> list:
    argv = [str(binary), "crawl"]
    for key, flag in CRAWL_FLAG_MAP.items():
        if key not in params or params[key] is None:
            continue
        value = params[key]
        if isinstance(value, bool):
            if value:
                argv.append(flag)
        else:
            argv.extend([flag, str(value)])
    return argv


def start_crawl(cfg, params: dict, jobs_dir: Path) -> str:
    if not params.get("start_url"):
        raise ValueError("params['start_url'] is required")

    binary = cfg.rust_sitemap_binary()
    job_id = uuid.uuid4().hex[:12]
    job_dir = jobs_dir / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    log_path = job_dir / "log.txt"
    argv = build_argv(binary, params)

    log_fh = open(log_path, "wb")
    proc = subprocess.Popen(
        argv,
        stdout=log_fh,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        cwd=str(cfg.rust_sitemapper_repo),
        start_new_session=True,
    )

    meta = {
        "id": job_id,
        "pid": proc.pid,
        "argv": argv,
        "params": params,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "log_path": str(log_path),
    }
    (job_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return job_id


def parse_latest_progress(log_text: str):
    matches = list(PROGRESS_BLOCK_RE.finditer(log_text))
    if not matches:
        return None
    m = matches[-1]
    return {
        "elapsed_secs": int(m.group("elapsed")),
        "processed": int(m.group("processed")),
        "rate_per_sec": float(m.group("rate")),
        "success": int(m.group("success")),
        "failed": int(m.group("failed")),
        "timeout": int(m.group("timeout")),
        "success_rate_pct": float(m.group("success_rate")),
        "discovered": int(m.group("discovered")),
    }


def is_pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def get_job_status(job_id: str, jobs_dir: Path) -> dict:
    meta_path = jobs_dir / job_id / "meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"No job found with id {job_id}")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    log_path = Path(meta["log_path"])
    log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""

    progress = parse_latest_progress(log_text)
    completed = bool(COMPLETE_RE.search(log_text))
    alive = is_pid_alive(meta["pid"])

    if completed:
        state = "completed"
    elif alive:
        state = "running"
    else:
        state = "failed"

    status = {
        "id": job_id,
        "state": state,
        "started_at": meta["started_at"],
        "params": meta["params"],
        "progress": progress,
    }
    if state == "failed":
        status["stderr_tail"] = "\n".join(log_text.splitlines()[-40:])
    return status


def list_jobs(jobs_dir: Path) -> list:
    if not jobs_dir.exists():
        return []
    ids = sorted(p.parent.name for p in jobs_dir.glob("*/meta.json"))
    return [get_job_status(job_id, jobs_dir) for job_id in ids]
