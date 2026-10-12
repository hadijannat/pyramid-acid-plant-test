"""Load ledger/evidence.yaml, the register of what the research files found for each documentary claim.

A claim in this register is decided by a document, by the hypothesis's own silence or by nothing at all, never
by a computation here: the status and its basis sentence are authored in the register, by the ruling of
docs/superpowers/specs/2026-10-11-simulations-design.md section 2, and this module only checks and reports them.

Assumptions:
- The research files in research/ are the evidence base; no source outside them was consulted.
- A basis asserts only what a research file states, and opens with that file's own standing.
"""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from pyramid import REPO_ROOT, simkit
# the strict loader's private helpers, shared with ledger.py on purpose: one set of rules and messages
from pyramid.ledger import (Ledger, LedgerError, _entries, _get, _is_boolean, _is_text, _is_text_list, _known_keys,
                            load)

EVIDENCE_FILE = REPO_ROOT / "ledger" / "evidence.yaml"

# The claims this register decides, by what decides them (the design's section 1).
DOCUMENTARY = ("E02", "E03", "E04", "E06", "E07", "E08", "E09", "E10", "E16", "E26", "E27", "E28", "E30", "E31",
               "E33", "E34", "E35", "E36", "E37", "E39")
UNDEFINED = ("S02", "S26")  # their criteria say "undefined until the hypothesis names ..."
NOT_TESTABLE = ("S05", "E05", "E23", "E24", "E40")  # their criteria say "cannot be simulated" or "analogy only"
CLAIMS = DOCUMENTARY + UNDEFINED + NOT_TESTABLE

STATUSES = ("pass", "fail", "conditional", "undefined", "not_testable")  # "pending" would leave a claim undecided
STANDINGS = ("Supported:", "No evidence found:", "Contradicted:", "Partly supported:",
             "Not specified by the hypothesis:", "No test exists:")

ASSUMPTIONS = [
    "The research files in research/ are the evidence base; no source outside them was consulted.",
    "A documentary status follows the ruling of the simulations design, section 2: pass when a source the research "
    "files read meets the criterion, fail when a source that would show it was read and does not or contradicts it, "
    "conditional when it is partly met or rests on a secondary source or on a measurement nobody has made, undefined "
    "when the claim names no source that could be checked or the hypothesis leaves the matter unspecified.",
    "Where a criterion joins two conditions with 'and', both must hold for a pass.",
    "A claim whose own criterion says that nothing can decide it is not_testable; its basis records what was found.",
]


@dataclass(frozen=True)
class Entry:
    id: str
    status: str
    basis: str  # opens with the research file's own standing
    sources: tuple[str, ...]  # sections of the research files
    verified: bool  # the research files read the deciding document at source


def load_evidence(path: Path = EVIDENCE_FILE, claim_ids: set[str] | None = None) -> dict[str, Entry]:
    """The register by claim id, in file order: exactly one entry for each of CLAIMS.

    With claim_ids (the ids of ledger/claims.yaml), an id that is no claim at all is told apart from a claim
    that some other package decides.
    """
    register: dict[str, Entry] = {}
    for number, entry in enumerate(_entries(path.read_bytes(), "evidence.yaml"), start=1):
        key = _get(entry, "id", f"evidence.yaml entry {number}", _is_text, "text")
        where = f"evidence.yaml: {key}"
        if key in register:
            raise LedgerError(f"evidence.yaml: duplicate id: {key}")
        if claim_ids is not None and key not in claim_ids:
            raise LedgerError(f"{where}: not a claim id")
        if key not in CLAIMS:
            raise LedgerError(f"{where}: not a claim this register decides")
        _known_keys(entry, where, Entry)
        status = _get(entry, "status", where, _is_text, "text")
        if status not in STATUSES:
            raise LedgerError(f"{where}: status must be one of {', '.join(STATUSES)}, not {status!r}")
        if (status == "not_testable") != (key in NOT_TESTABLE):
            raise LedgerError(f"{where}: not_testable is for the claims whose criterion says no test exists, and "
                              "only for them")
        if key in UNDEFINED and status != "undefined":
            raise LedgerError(f"{where}: the criterion holds this claim undefined, not {status!r}")
        basis = _get(entry, "basis", where, _is_text, "text").strip()
        if not basis.startswith(STANDINGS):
            raise LedgerError(f"{where}: basis must open with one of: {' '.join(STANDINGS)}")
        if "—" in basis or "–" in basis:
            raise LedgerError(f"{where}: basis must be plain prose without dashes")
        sources = _get(entry, "sources", where, _is_text_list, "a list of research file sections")
        if not sources or not all(source.startswith("research/") for source in sources):
            raise LedgerError(f"{where}: sources must name at least one section of a research file")
        register[key] = Entry(key, status, basis, tuple(sources),
                              _get(entry, "verified", where, _is_boolean, "true or false"))
    missing = [claim for claim in CLAIMS if claim not in register]
    if missing:
        raise LedgerError(f"evidence.yaml: missing {', '.join(missing)}")
    return register


def verdicts(ledger: Ledger, path: Path = EVIDENCE_FILE) -> dict[str, tuple[str, str]]:
    """{claim: (status, basis)} for the claims of the register."""
    return {key: (entry.status, entry.basis) for key, entry in load_evidence(path, set(ledger.claims)).items()}


def main(root=simkit.RESULTS) -> None:
    ledger = load()
    register = load_evidence(claim_ids=set(ledger.claims))
    extra = {
        "assumptions": ASSUMPTIONS,
        "register_sha256": sha256(EVIDENCE_FILE.read_bytes()).hexdigest(),  # the ledger digest does not cover it
        "register": {key: {"sources": list(entry.sources), "verified": entry.verified}
                     for key, entry in register.items()},
    }
    simkit.write_results("evidence", ledger, {}, verdicts(ledger), extra, root)


if __name__ == "__main__":
    main()
