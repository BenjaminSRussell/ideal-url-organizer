"""FastAPI sidecar: serves cross-site insight data and launches/monitors
rust-sitemapper crawls + the bridge import, all over 127.0.0.1 only."""
import subprocess
import sys
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from server.aggregator import RESULTS_DIR, aggregate_all, aggregate_site
from server.config import ServerConfig, load_config
from server.jobs import JOBS_DIR, get_job_status, list_jobs, start_crawl

app = FastAPI(title="sitemapper-viewer sidecar")


@app.exception_handler(FileNotFoundError)
async def _file_not_found_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": str(exc)})


def get_config() -> ServerConfig:
    return load_config()


def get_jobs_dir() -> Path:
    return JOBS_DIR


def get_results_dir() -> Path:
    return RESULTS_DIR


class CrawlRequest(BaseModel):
    start_url: str
    data_dir: Optional[str] = None
    preset: Optional[str] = None
    workers: Optional[int] = None
    user_agent: Optional[str] = None
    timeout: Optional[int] = None
    ignore_robots: Optional[bool] = None
    seeding_strategy: Optional[str] = None
    enable_redis: Optional[bool] = None
    redis_url: Optional[str] = None
    lock_ttl: Optional[int] = None
    save_interval: Optional[int] = None
    max_urls: Optional[int] = None
    duration: Optional[int] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/overview")
def overview(results_dir: Path = Depends(get_results_dir)):
    return aggregate_all(results_dir)


@app.get("/sites")
def sites(results_dir: Path = Depends(get_results_dir)):
    return aggregate_all(results_dir)["sites"]


@app.get("/sites/{name}")
def site_detail(name: str, results_dir: Path = Depends(get_results_dir)):
    site_dir = results_dir / name
    if not site_dir.exists():
        raise HTTPException(status_code=404, detail=f"No site named {name}")
    return aggregate_site(site_dir)


@app.post("/crawls")
def create_crawl(
    req: CrawlRequest,
    cfg: ServerConfig = Depends(get_config),
    jobs_dir: Path = Depends(get_jobs_dir),
):
    params = req.model_dump(exclude_none=True)
    try:
        job_id = start_crawl(cfg, params, jobs_dir)
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": job_id}


@app.get("/crawls")
def crawls(jobs_dir: Path = Depends(get_jobs_dir)):
    return list_jobs(jobs_dir)


@app.get("/crawls/{job_id}")
def crawl_status(job_id: str, jobs_dir: Path = Depends(get_jobs_dir)):
    try:
        return get_job_status(job_id, jobs_dir)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/crawls/{job_id}/import")
def import_crawl(
    job_id: str,
    cfg: ServerConfig = Depends(get_config),
    jobs_dir: Path = Depends(get_jobs_dir),
):
    try:
        status = get_job_status(job_id, jobs_dir)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    if status["state"] != "completed":
        raise HTTPException(
            status_code=409,
            detail=f"Job {job_id} is not completed (state={status['state']})",
        )
    data_dir_param = status["params"].get("data_dir") or "./data"
    sitemap_path = cfg.rust_sitemapper_repo / data_dir_param / "sitemap.jsonl"
    if not sitemap_path.exists():
        raise HTTPException(
            status_code=404, detail=f"No sitemap.jsonl found at {sitemap_path}"
        )

    result = subprocess.run(
        [sys.executable, "scripts/import_rust_sitemapper.py", str(sitemap_path)],
        cwd=str(Path(__file__).resolve().parent.parent),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr[-2000:])
    return {"ok": True, "output": result.stdout[-2000:]}
