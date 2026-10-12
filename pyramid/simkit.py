"""What the simulation packages share: results on disk, draws over the ledger's ranges, the three-way rule.

A package (premises, evidence, flow, chem, electro, em) computes Results and verdicts and writes them with
write_results; pyramid.verdicts reads them back with read_results and merges them with Tier 0.
"""
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from pyramid import REPO_ROOT
from pyramid.ledger import STATUSES, Ledger, LedgerError
from pyramid.provenance import write_manifest
from pyramid.screening import Result, _evaluate, _three_way

RESULTS = REPO_ROOT / "results"
LOG_SPAN = 100.0   # a range wider than this ratio is drawn log-uniformly: its ends are orders of magnitude apart


def three_way(holds_at_worst: bool, holds_at_best: bool) -> str:
    """pass if the test holds even at the unfavourable end, fail if it fails even at the favourable end."""
    return _three_way(holds_at_worst, holds_at_best)


def corners(ledger: Ledger, inputs: tuple[str, ...], fn) -> tuple[float, float, float]:
    """fn at the ledger values, then its least and greatest value over every low/high combination.

    Exact only where fn is monotone in each input; a package says so where it relies on this.
    """
    return _evaluate(ledger, inputs, fn)


def sample(ledger: Ledger, ids: tuple[str, ...], n: int, seed: int) -> list[dict[str, float]]:
    """n draws of {id: value} over the ledger's ranges; the first draw is the ledger's own values."""
    rng = np.random.default_rng(seed)
    draws = [{i: ledger.q(i) for i in ids}]
    for _ in range(n - 1):
        draw = {}
        for i in ids:
            low, high = ledger.rng(i)
            if low > 0 and high / low > LOG_SPAN:
                draw[i] = float(np.exp(rng.uniform(np.log(low), np.log(high))))
            else:
                draw[i] = float(rng.uniform(low, high))
        draws.append(draw)
    return draws


def band(values) -> tuple[float, float, float]:
    """Median, 5th and 95th percentile of a set of draws."""
    median, low, high = np.percentile(np.asarray(values, dtype=float), [50, 5, 95])
    return float(median), float(low), float(high)


def save_figure(fig, path: Path, **kw) -> None:
    """Write a figure with no library version or time stamp in the file, so a regeneration reproduces it byte for byte."""
    stamp = {"Date": None} if str(path).endswith(".svg") else {"Software": None, "Creation Time": None}
    fig.savefig(path, metadata=stamp, **kw)


def write_results(package: str, ledger: Ledger, results: dict[str, Result],
                  verdicts: dict[str, tuple[str, str]], extra: dict | None = None, root: Path = RESULTS) -> Path:
    """results/<package>/summary.json and manifest.json. Verdict words and claim ids are checked here."""
    for claim, (status, basis) in verdicts.items():
        if claim not in ledger.claims:
            raise LedgerError(f"{package}: {claim} is not a claim id")
        if status not in STATUSES:
            raise LedgerError(f"{package}: {claim}: {status!r} is not a verdict word")
        if not basis.strip():
            raise LedgerError(f"{package}: {claim}: a verdict needs a basis sentence")
    out_dir = root / package
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "results": [asdict(result) for result in results.values()],
        "verdicts": {claim: {"status": status, "basis": basis} for claim, (status, basis) in verdicts.items()},
    }
    (out_dir / "summary.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    write_manifest(out_dir, package, ledger, extra)
    return out_dir


def read_results(package: str, root: Path = RESULTS):
    """(results, verdicts, manifest) as write_results stored them, or None if the package has not run."""
    out_dir = root / package
    if not (out_dir / "summary.json").exists():
        return None
    payload = json.loads((out_dir / "summary.json").read_text())
    results = {row["id"]: Result(**{**row, "inputs": tuple(row["inputs"])}) for row in payload["results"]}
    verdicts = {claim: (v["status"], v["basis"]) for claim, v in payload["verdicts"].items()}
    return results, verdicts, json.loads((out_dir / "manifest.json").read_text())
