"""One verdict per claim: Tier 0 where it has a rule, else the simulation package that decides the claim.

Tier 0 verdicts stand. A package may decide only claims Tier 0 leaves pending, and no two packages
may decide the same claim: either case is an error here, so a verdict never changes silently.
"""
from hashlib import sha256
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
    """The packages whose committed results were generated from other sources than the ones in the tree.

    Two packages have a source of their own. The documentary register is not part of the ledger digest, so
    evidence is also compared by the register's hash. The field runs take hours, so em stays fresh while the ledger
    lines it can read are the ones its runs were made for, whatever else in the ledger has changed.
    """
    from pyramid.em.runs import inputs_digest   # here, not at the top: the solvers are a heavy import
    from pyramid.evidence import EVIDENCE_FILE

    def fresh(package: str, manifest: dict) -> bool:
        if package == "em" and manifest.get("cache_inputs") == inputs_digest(ledger):
            return True
        if package == "evidence" and manifest.get("register_sha256") != sha256(EVIDENCE_FILE.read_bytes()).hexdigest():
            return False
        return manifest["ledger"] == ledger.digest

    return [package for package in PACKAGES
            if (stored := read_results(package, root)) is not None and not fresh(package, stored[2])]
