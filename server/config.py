"""Loads server/config.yaml and resolves the rust_sitemap binary path."""
from pathlib import Path

import yaml

SERVER_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = SERVER_DIR / "config.yaml"


class ServerConfig:
    def __init__(self, rust_sitemapper_repo: str):
        self.rust_sitemapper_repo = Path(rust_sitemapper_repo).expanduser()

    def rust_sitemap_binary(self) -> Path:
        candidates = []
        for profile in ("release", "debug"):
            p = self.rust_sitemapper_repo / "target" / profile / "rust_sitemap"
            if p.exists():
                candidates.append(p)
        if not candidates:
            raise FileNotFoundError(
                f"No rust_sitemap binary found under {self.rust_sitemapper_repo}/target/"
                "{release,debug}. Build it first with `cargo build` (or `cargo build "
                "--release`) in that repo."
            )
        return max(candidates, key=lambda p: p.stat().st_mtime)


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> ServerConfig:
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Copy server/config.yaml.example to server/config.yaml "
            "and set rust_sitemapper_repo."
        )
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    if "rust_sitemapper_repo" not in raw:
        raise ValueError(f"{path} is missing required key 'rust_sitemapper_repo'")
    return ServerConfig(rust_sitemapper_repo=raw["rust_sitemapper_repo"])
