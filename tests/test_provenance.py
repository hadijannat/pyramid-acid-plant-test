"""Tests for the provenance manifest written beside every generated result."""
import json
import platform
import re
import subprocess
from datetime import datetime, timedelta

import numpy
import yaml

from pyramid import REPO_ROOT, ledger, provenance


def test_manifest_records_case_commit_ledger_and_versions():
    led = ledger.load()
    record = provenance.manifest("tier0", led)
    assert record["case"] == "tier0"
    assert record["ledger"] == led.digest
    assert re.fullmatch(r"[0-9a-f]{40}", record["commit"])
    assert datetime.fromisoformat(record["timestamp"]).utcoffset() == timedelta(0)
    assert record["python"] == platform.python_version()
    assert set(record["versions"]) == {"numpy", "scipy", "pyyaml", "gmsh", "trimesh", "matplotlib", "pytest"}
    assert record["versions"]["numpy"] == numpy.__version__
    assert record["versions"]["pyyaml"] == yaml.__version__


def test_manifest_merges_extra():
    record = provenance.manifest("R1", ledger.load(), {"wall_time_s": 1.5, "mesh": {"cells": 10}})
    assert record["case"] == "R1"
    assert record["wall_time_s"] == 1.5
    assert record["mesh"] == {"cells": 10}


def test_commit_is_unknown_outside_a_repository(monkeypatch):
    def not_a_repository(*args, **kwargs):
        raise subprocess.CalledProcessError(128, "git")

    monkeypatch.setattr(subprocess, "run", not_a_repository)
    assert provenance.manifest("tier0", ledger.load())["commit"] == "unknown"


def test_write_manifest_writes_manifest_json_into_out_dir(tmp_path):
    led = ledger.load()
    out_dir = tmp_path / "results" / "tier0"  # does not exist yet
    path = provenance.write_manifest(out_dir, "tier0", led, {"note": "screening table"})
    assert path == out_dir / "manifest.json"
    written = json.loads(path.read_text())
    assert written["case"] == "tier0"
    assert written["ledger"] == led.digest
    assert written["note"] == "screening table"
    assert written["versions"]["numpy"] == numpy.__version__


def test_committed_results_were_generated_from_the_ledger_in_the_repository():
    """An edit of the ledger leaves the committed results stale until they are regenerated (see README.md)."""
    digest = ledger.load().digest
    for folder, command in (
        ("results/tier0", "uv run python -m pyramid.screening"),
        ("viewer/data", "uv run python -m pyramid.viewer_data"),
        ("results/summary", "uv run python -m pyramid.summary"),
    ):
        recorded = json.loads((REPO_ROOT / folder / "manifest.json").read_text())["ledger"]
        assert recorded == digest, (
            f"{folder} was generated from another ledger: run `{command}` on a clean tree and commit the result"
        )
    from pyramid.verdicts import stale
    assert stale(ledger.load()) == [], "run `uv run python -m pyramid.<package>` for each on a clean tree and commit"


def test_the_committed_cycle_is_what_its_sources_give_today():
    """The ledger digest covers parameters.yaml and claims.yaml; cycle.yaml, species.yaml and the verdicts are the
    viewer's other sources, and an edit of any of them leaves cycle.json stale until it is regenerated."""
    from pyramid import viewer_data
    from pyramid.species import load_species
    from pyramid.verdicts import merged

    led = ledger.load()
    committed = json.loads((REPO_ROOT / "viewer" / "data" / "cycle.json").read_text())
    statuses = {claim: status for claim, (status, _) in merged(led)[1].items()}
    fresh = viewer_data.cycle_payload(led, committed["curves"], load_species(step_ids=set(led.claims)), statuses)
    assert json.loads(json.dumps(fresh)) == committed, (
        "viewer/data/cycle.json is stale: run `uv run python -m pyramid.viewer_data` on a clean tree and commit")
