"""Load ledger/species.yaml, and mark each compound by the verdict of the step that produces it."""
import re
from dataclasses import dataclass
from pathlib import Path

from pyramid import REPO_ROOT
# the strict loader's private helpers, shared with ledger.py on purpose: one set of rules and messages
from pyramid.ledger import LedgerError, _entries, _get, _is_text, _known_keys

SPECIES_FILE = REPO_ROOT / "ledger" / "species.yaml"
PHASES: tuple[str, ...] = ("gas", "liquid", "solid")
_COLOUR = re.compile(r"#[0-9a-f]{6}")


@dataclass(frozen=True)
class Species:
    id: str
    formula: str        # Unicode subscripts, for display: "SO₂"
    name: str
    phase: str          # "gas" | "liquid" | "solid"
    colour: str         # "#rrggbb"
    produced_by: str | None   # a step id of ledger/claims.yaml, or None for an input


def _is_step_or_none(value) -> bool:
    return value is None or _is_text(value)


def load_species(path: Path = SPECIES_FILE, step_ids: set[str] | None = None) -> dict[str, Species]:
    """The species by id, in file order. With step_ids, every produced_by must be one of them."""
    species: dict[str, Species] = {}
    for number, entry in enumerate(_entries(path.read_bytes(), "species.yaml"), start=1):
        key = _get(entry, "id", f"species.yaml entry {number}", _is_text, "text")
        if key in species:
            raise LedgerError(f"species.yaml: duplicate id: {key}")
        where = f"species.yaml: {key}"
        _known_keys(entry, where, Species)
        phase = _get(entry, "phase", where, _is_text, "text")
        if phase not in PHASES:
            raise LedgerError(f"{where}: phase must be gas, liquid or solid, not {phase!r}")
        colour = _get(entry, "colour", where, _is_text, "text")
        if not _COLOUR.fullmatch(colour):
            raise LedgerError(f"{where}: colour must be #rrggbb in lower-case hex, not {colour!r}")
        produced_by = _get(entry, "produced_by", where, _is_step_or_none, "a step id or null")
        if produced_by is not None and step_ids is not None and produced_by not in step_ids:
            raise LedgerError(f"{where}: produced_by {produced_by} is not a step id")
        species[key] = Species(
            id=key,
            formula=_get(entry, "formula", where, _is_text, "text"),
            name=_get(entry, "name", where, _is_text, "text"),
            phase=phase,
            colour=colour,
            produced_by=produced_by,
        )
    return species


def species_status(species: Species, verdicts: dict[str, str]) -> str:
    """'claimed' when the producing step fails or is undefined, 'conditional' when it is conditional, else 'plain'.

    The rule looks only at the step that produces the species: an input (produced_by None) is always plain.
    """
    verdict = verdicts.get(species.produced_by) if species.produced_by else None
    if verdict in ("fail", "undefined"):
        return "claimed"
    if verdict == "conditional":
        return "conditional"
    return "plain"


def species_payload(species: Species, verdicts: dict[str, str]) -> dict:
    """One species as cycle.json carries it: the table entry without produced_by, plus its status."""
    return {
        "id": species.id,
        "formula": species.formula,
        "name": species.name,
        "phase": species.phase,
        "colour": species.colour,
        "status": species_status(species, verdicts),
    }
