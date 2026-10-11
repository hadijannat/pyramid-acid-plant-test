"""One verdict per claim: Tier 0 where it has a rule, else the simulation package that decides the claim.

Tier 0 verdicts stand. A package may decide only claims Tier 0 leaves pending, and no two packages
may decide the same claim: either case is an error here, so a verdict never changes silently.
"""
from pathlib import Path

from pyramid import screening
from pyramid.ledger import Ledger, LedgerError
from pyramid.screening import Result
from pyramid.simkit import RESULTS, read_results

PACKAGES = ("premises", "evidence", "flow", "chem", "electro", "em")   # in the order they are read


def merged(ledger: Ledger, root: Path = RESULTS):
    """(results, verdicts, source): every Result, {claim: (status, basis)}, {claim: 'tier0' | package | 'none'}."""
    results: dict[str, Result] = dict(screening.all_results(ledger))
    verdicts = screening.verdicts(ledger, results)
    source = {claim: "tier0" if claim in screening.RULES else "none" for claim in verdicts}
    for package in PACKAGES:
        stored = read_results(package, root)
        if stored is None:
            continue
        package_results, package_verdicts, _ = stored
        for id, result in package_results.items():
            if id in results:
                raise LedgerError(f"{package}: result id {id} is already taken")
            results[id] = result
        for claim, verdict in package_verdicts.items():
            if source.get(claim) is None:
                raise LedgerError(f"{package}: {claim} is not a claim id")
            if source[claim] != "none":
                raise LedgerError(f"{package}: {claim} is already decided by {source[claim]}")
            verdicts[claim] = verdict
            source[claim] = package
    return results, verdicts, source


def stale(ledger: Ledger, root: Path = RESULTS) -> list[str]:
    """The packages whose committed results were generated from another ledger than this one."""
    return [package for package in PACKAGES
            if (stored := read_results(package, root)) is not None and stored[2]["ledger"] != ledger.digest]
