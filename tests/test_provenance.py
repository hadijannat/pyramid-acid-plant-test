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


def test_the_committed_results_of_the_fast_packages_are_what_the_code_computes_today(tmp_path):
    """A manifest's digest says which ledger a result came from, not that the code still gives it: an edit of a
    rule, of a basis sentence or of the documentary register leaves the committed summary stale with its digest
    intact. premises, evidence, flow and chem run in seconds, so they are recomputed here and compared."""
    import pytest

    from pyramid import evidence, premises
    from pyramid.chem.__main__ import main as chem
    from pyramid.flow.__main__ import main as flow

    for package, run in (("premises", premises.main), ("evidence", evidence.main), ("flow", flow), ("chem", chem)):
        run(root=tmp_path)
        fresh = json.loads((tmp_path / package / "summary.json").read_text())
        committed = json.loads((REPO_ROOT / "results" / package / "summary.json").read_text())
        assert fresh["verdicts"] == committed["verdicts"], f"run `uv run python -m pyramid.{package}` and commit"
        assert [r["id"] for r in fresh["results"]] == [r["id"] for r in committed["results"]], package
        for new, old in zip(fresh["results"], committed["results"]):
            assert [new[k] for k in ("value", "low", "high")] == pytest.approx(
                [old[k] for k in ("value", "low", "high")], rel=1e-9), new["id"]


def test_the_verdict_table_and_the_viewers_claims_are_the_merge_of_the_committed_results():
    from pyramid.verdicts import merged

    _, decided, source = merged(ledger.load())
    table = json.loads((REPO_ROOT / "results" / "summary" / "verdicts.json").read_text())["verdicts"]
    assert table == {claim: {"status": status, "basis": basis, "source": source[claim]}
                     for claim, (status, basis) in decided.items()}, "run `uv run python -m pyramid.summary` and commit"
    shown = {claim["id"]: (claim["status"], claim["basis"])
             for claim in json.loads((REPO_ROOT / "viewer" / "data" / "claims.json").read_text())["claims"]}
    assert shown == decided, "run `uv run python -m pyramid.viewer_data` and commit"


def test_the_committed_electro_verdicts_and_the_elevation_are_what_the_code_gives_today(tmp_path):
    """electro's verdicts are pure functions of its committed results, and the elevation is drawn from the
    committed model: both regenerate in seconds, so both are compared here (pre-merge review, M1 and R1)."""
    from pyramid import electro, elevation
    from pyramid.simkit import read_results

    results, decided, _ = read_results("electro")
    assert electro.verdicts(ledger.load(), results) == decided, "run `uv run python -m pyramid.electro` and commit"
    elevation.main(tmp_path / "interior-elevation.svg")
    assert (tmp_path / "interior-elevation.svg").read_bytes() == elevation.OUT.read_bytes(), (
        "run `uv run python -m pyramid.elevation` and commit")
