"""Provenance manifest: which code, ledger and libraries produced a result."""
import json
import platform
import subprocess
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from pyramid import REPO_ROOT
from pyramid.ledger import Ledger

CORE_DEPENDENCIES = ("numpy", "scipy", "pyyaml", "gmsh", "trimesh", "matplotlib", "pytest")


def _commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
        )
    except (subprocess.CalledProcessError, OSError):  # not a repository, or git is not installed
        return "unknown"
    return result.stdout.strip()


def manifest(case: str, ledger: Ledger, extra: dict | None = None) -> dict:
    return {
        "case": case,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "commit": _commit(),
        "ledger": ledger.digest,
        "python": platform.python_version(),
        "versions": {name: version(name) for name in CORE_DEPENDENCIES},
        **(extra or {}),
    }


def write_manifest(out_dir: Path, case: str, ledger: Ledger, extra: dict | None = None) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "manifest.json"
    path.write_text(json.dumps(manifest(case, ledger, extra), indent=2) + "\n")
    return path
