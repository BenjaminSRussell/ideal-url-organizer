# Cross-site insight aggregator + SwiftUI viewer app

**Date:** 2026-08-08
**Status:** Approved

## Problem

url-organizer's pipeline already produces rich per-site output under
`data/results_by_site/<site>/` (data quality report, comprehensive
intelligence report, per-method summaries, charts) for eleven crawled
datasets (wikipedia, hackernews, nike, target, allbirds, reactdev, walmart,
stubhub, zillow, target-massive, target-massive-v2). There is no view across
all of them, and no way to look at or act on any of this data outside a
terminal — reading JSON files, tailing crawl stdout, and re-running the
bridge script by hand.

## Goals

1. Produce one aggregate view across everything collected so far (not just
   the latest run), computed from the reports that already exist on disk.
2. A native macOS app to browse that data, drill into any single site's
   results, launch new rust-sitemapper crawls with full control over the
   crawler's config, and run the url-organizer bridge/pipeline against a
   finished crawl — all without a terminal.

## Non-goals

- Re-implementing any of url-organizer's analysis methods in Swift or
  elsewhere — the app reads what the existing Python pipeline already
  produces.
- Cross-platform support. This is a personal macOS tool.
- Authentication / multi-user support. Sidecar server binds to localhost
  only.
- Editing crawl data from the app. It is a viewer + a launcher for
  existing scripts, not a data editor.

## Architecture

Three independently-versioned projects, matching the existing split
between rust-sitemapper (crawler) and url-organizer (analysis):

1. **rust-sitemapper** — existing crawler. Unchanged.
2. **url-organizer** — existing analysis pipeline, plus a new `server/`
   package containing a FastAPI sidecar.
3. **sitemapper-viewer** — new SwiftUI macOS app project (new directory,
   new git repo, lives alongside the other two on Desktop).

```
rust-sitemapper (binary: target/{debug,release}/rust_sitemap)
        ^
        | subprocess (crawl / resume)
        |
url-organizer/server/  --- reads/writes --->  data/results_by_site/*
        ^                                     data/raw/urls.jsonl
        | HTTP (localhost only)
        |
sitemapper-viewer (SwiftUI app, spawns+owns the sidecar process)
```

## Components

### 1. Cross-site aggregator (`url-organizer/server/aggregator.py`)

Pure function(s) over the filesystem, no state of its own:

- Scans `data/results_by_site/*/`.
- For each site directory, reads (if present — see error handling):
  - `analysis/data_quality_report.json`
  - `reports/comprehensive_intelligence_report.json`
  - `methods/method_16_canonical_deduplication/summary.json`
- Emits a per-site summary: total URLs, unique domains, success rate
  (crawled / total), duplication rate (1 - unique_canonical / total),
  average URL length, generated timestamp.
- Emits a global rollup across all sites: total URLs collected, combined
  domain count, aggregate duplication rate, count of sites.
- Computed fresh on every call — nothing is cached to disk, so it can
  never go stale relative to what's actually in `results_by_site/`.

### 2. Sidecar server (`url-organizer/server/app.py`, FastAPI)

Binds to `127.0.0.1:8731`. Endpoints:

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | liveness check the Mac app polls after spawning the server |
| GET | `/overview` | aggregator output above |
| GET | `/sites` | list of sites with headline stats |
| GET | `/sites/{name}` | full detail for one site (everything a detail view's charts need) |
| POST | `/crawls` | start a new crawl; body mirrors the `rust_sitemap crawl` subcommand's full flag set |
| GET | `/crawls` | list past + running crawl jobs |
| GET | `/crawls/{id}` | structured live status: elapsed, processed, success/failed/timeout, rate, discovered, state (running/completed/failed), stderr tail if failed |
| POST | `/crawls/{id}/import` | run the existing bridge script + pipeline against that job's `sitemap.jsonl`, landing output under `results_by_site/` |

**Crawl config surface** (POST /crawls body) maps 1:1 to `rust-sitemapper/src/cli.rs`'s `Commands::Crawl` fields: `start_url`, `data_dir`, `preset`, `workers`, `user_agent`, `timeout`, `ignore_robots`, `seeding_strategy`, `enable_redis`, `redis_url`, `lock_ttl`, `save_interval`, `max_urls`, `duration`.

**Progress parsing:** the crawler already prints periodic lines to stdout:
```
  PROGRESS REPORT (Ns elapsed, ...)
  URLs Processed: N (X/sec) | Success: N | Failed: N | Timeout: N
  Success Rate: X% | Total Discovered: N
```
The server tails the subprocess's stdout, parses these with a regex, and
keeps the latest parsed values in the job's in-memory/on-disk state. The
Mac app never parses raw text — `GET /crawls/{id}` returns structured
JSON.

**Job persistence and process lifetime:** each crawl is launched detached
(its own process group, stdout redirected to a log file under
`server/jobs/<id>/log.txt`), and its pid + config + log path are recorded
in `server/jobs/<id>/meta.json`. This means:
- A crawl outlives the sidecar server process. If the app is quit (killing
  the sidecar), the crawl keeps running.
- On startup, the sidecar scans `server/jobs/*/meta.json`, checks which
  pids are still alive, and reattaches (resumes tailing the log file) to
  any that are — so re-opening the app after quitting mid-crawl shows the
  crawl still in progress rather than losing it.
- `rust-sitemapper`'s own `resume` subcommand (already exists) is what
  would be used to pick a genuinely-killed crawl back up; the sidecar
  does not need to implement that logic itself, only surface job state
  and let a user re-trigger a resume manually if a crawl actually died.

**Location of rust-sitemapper binary:** the sidecar reads a small
`server/config.yaml` (real file gitignored, `.example` committed,
mirroring the existing `config/global.yaml` pattern) holding the path to
the rust-sitemapper repo checkout, from which it resolves
`target/release/rust_sitemap` (falling back to `target/debug/rust_sitemap`
if release isn't built).

### 3. SwiftUI app (`sitemapper-viewer`, new project)

New Swift Package Manager executable target using the SwiftUI `App`
lifecycle (no Xcode project file needed; builds with `swift build`, runs
as a real windowed Mac app).

- **App launch:** spawns the sidecar (`python3 -m server.app` inside
  url-organizer's venv) as a child process, polls `/health` until ready,
  then loads the UI. Terminates the sidecar on quit (detached crawl jobs
  are unaffected, per above).
- **Overview tab:** table/cards from `GET /overview` — one row per site,
  sortable by URL count / success rate / duplication rate, plus the
  global rollup at the top.
- **Site Detail view:** native Swift Charts rebuilt directly from
  `GET /sites/{name}` JSON — protocol split, URL-length histogram, depth
  distribution, path-structure top-N, crawl-status breakdown. No PNGs
  embedded; charts are native, resizable, and theme-aware.
- **New Crawl tab:** form with one control per `crawl` flag (text fields
  for URL/data-dir/user-agent, steppers for workers/timeout/lock-ttl/
  save-interval, toggles for ignore-robots/enable-redis, picker for
  seeding-strategy, optional fields for preset/max-urls/duration). Submit
  posts to `/crawls`, then switches to a live progress view polling
  `GET /crawls/{id}` every ~2s.
- **Jobs tab:** history of past + running crawl jobs, each with a
  "Run bridge on this dataset" button that calls `/crawls/{id}/import`
  once a job is completed.

## Data flow example (new crawl end to end)

1. User fills the New Crawl form, submits.
2. App POSTs to `/crawls`; sidecar spawns `rust_sitemap crawl --start-url
   ... ` detached, writes `meta.json`, returns `{id}`.
3. App polls `/crawls/{id}`; sidecar tails the job's log file, parses the
   latest PROGRESS REPORT block, returns structured status.
4. Crawl finishes (or duration/max-urls cap hits, per rust-sitemapper's
   existing behavior); job state flips to `completed`.
5. User taps "Run bridge on this dataset"; app POSTs to
   `/crawls/{id}/import`; sidecar runs the existing
   `scripts/import_rust_sitemapper.py` + `run.sh --all` pipeline against
   that job's `sitemap.jsonl`, writes into `data/results_by_site/<name>/`.
6. `GET /overview` and `GET /sites` now include the new site on next
   fetch — no separate refresh step needed, since both are computed live
   from the filesystem.

## Error handling

- Aggregator: a site directory missing one of its expected JSON files is
  skipped for the fields it can't compute, with a `"partial": true` flag
  and a note of which files were missing — never fails the whole
  `/overview` call over one bad site.
- Sidecar: subprocess launch failures (bad binary path, bad start-url)
  and non-zero exits surface as `state: "failed"` with the stderr tail on
  `GET /crawls/{id}`, not as a 500.
- App: failed sidecar spawn or a `/health` timeout shows a clear inline
  error with the sidecar's stderr rather than a blank window; a failed
  job shows its error inline in the Jobs tab rather than silently
  vanishing.

## Testing

- `server/aggregator.py`: pytest, same style as the existing bridge
  tests — cover the multi-site rollup, the partial-data/missing-file
  case, and the empty-`results_by_site`-directory case.
- `server/app.py`: pytest with FastAPI's `TestClient` covering each
  route, including a mocked/fake subprocess for the `/crawls` flow so
  tests don't actually launch `rust_sitemap`.
- `sitemapper-viewer`: unit tests for the progress-polling view model and
  the crawl-config-to-JSON-body mapping; a manual end-to-end smoke test
  (crawl a small real site like example.com through the app, confirm it
  shows up in Overview) before considering this done.
