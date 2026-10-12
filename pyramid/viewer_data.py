"""Export what the viewer reads: claims.json, cycle.json, the two glb files and a manifest."""
import json
import math

import yaml

from pyramid import REPO_ROOT, provenance, screening
from pyramid.geometry import Variants, build
from pyramid.geometry.export import to_viewer, write_glb
from pyramid.geometry.frame import session
from pyramid.geometry.model import level_volume_curve
from pyramid.ledger import Ledger, LedgerError, load
from pyramid.screening import Result
from pyramid.species import Species, load_species, species_payload

NOTICE = "Animation of the claim. Not a simulation result."
CYCLE_FILE = REPO_ROOT / "ledger" / "cycle.yaml"
OUT_DIR = REPO_ROOT / "viewer" / "data"
WEATHER = ("clear", "storm")

# The alternative reading of the survey (plan header): what interior_alt.glb shows.
ALTERNATIVE = Variants(
    kc_shaft_ends_level=True, grooves_connected=True, pit_excavated=True,
    big_void_inclined=True, apex_truncated=False,
)

# space name -> (label, ledger id prefix, prefix to leave out).
# The two shafts of a pair share one prefix, so each leaves out the other's ids.
SPACES: dict[str, tuple[str, str, str | None]] = {
    "descending_passage": ("Descending Passage", "dp.", None),
    "subterranean_chamber": ("Subterranean Chamber", "sub.", None),
    "pit": ("Pit", "pit.", None),
    "south_passage": ("South passage", "sp.", None),
    "well_shaft": ("Well shaft", "ws.", None),
    "grotto": ("Grotto", "grotto.", None),
    "ascending_passage": ("Ascending Passage", "ap.", None),
    "queens_passage": ("Queen's Chamber passage", "qp.", None),
    "queens_chamber": ("Queen's Chamber", "qc.", None),
    "qc_shaft_north": ("Queen's Chamber north shaft", "qcs.", "qcs.south."),
    "qc_shaft_south": ("Queen's Chamber south shaft", "qcs.", "qcs.north."),
    "grand_gallery": ("Grand Gallery", "gg.", None),
    "antechamber": ("Antechamber", "ante.", None),
    "kings_chamber": ("King's Chamber", "kc.", None),
    "kc_shaft_north": ("King's Chamber north shaft", "kcs.", "kcs.south."),
    "kc_shaft_south": ("King's Chamber south shaft", "kcs.", "kcs.north."),
    "relieving_chambers": ("Relieving chambers", "rc.", None),
    "big_void": ("Big Void", "bv.", None),
    "north_face_corridor": ("North Face Corridor", "nfc.", None),
    "paper_kings_chamber": ("King's Chamber (2018 study's model)", "paper.kc.", None),
    "paper_queens_chamber": ("Queen's Chamber (2018 study's model)", "paper.qc.", None),
    "paper_lower_chamber": ("Lower chamber (2018 study's model)", "paper.lower.", None),
}


def _finite(x: float) -> float | None:
    """JSON has no infinity and no NaN; the viewer prints null as 'no bound'."""
    return x if math.isfinite(x) else None


def claims_payload(ledger: Ledger, results: dict[str, Result],
                   verdicts: dict[str, tuple[str, str]]) -> dict:
    claims = []
    for claim in ledger.claims.values():
        status, basis = verdicts.get(claim.id, (claim.status, ""))
        depends = set(claim.depends_on)
        claims.append({
            "id": claim.id,
            "statement": claim.statement,
            "subsystem": claim.subsystem,
            "timestamp": claim.timestamp,
            "tier": claim.tier,
            "piece": claim.piece,
            "criterion": claim.criterion,
            "status": status,
            "basis": basis,
            # a result belongs to a claim when the claim depends on every quantity the result reads
            "numbers": [
                {"label": result.label, "value": _finite(result.value), "low": _finite(result.low),
                 "high": _finite(result.high), "unit": result.unit}
                for result in results.values()
                if result.inputs and set(result.inputs) <= depends
            ],
            "spaces": list(claim.spaces),
        })
    spaces = {
        name: {
            "label": label,
            "quantities": [
                {"id": quantity.id, "value": quantity.value, "unit": quantity.unit, "source": quantity.source,
                 "verified": quantity.verified, "note": quantity.note}
                for quantity in ledger.quantities.values()
                if quantity.id.startswith(prefix) and not (skip and quantity.id.startswith(skip))
            ],
            "claims": [claim.id for claim in ledger.claims.values() if name in claim.spaces],
        }
        for name, (label, prefix, skip) in SPACES.items()
    }
    return {"manifest": provenance.manifest("viewer", ledger), "claims": claims, "spaces": spaces}


def _viewer_path(path: list[dict]) -> list[dict]:
    """Camera keyframes from the project frame to the viewer's."""
    return [{key: list(to_viewer(*keyframe[key])) for key in ("position", "target")} for keyframe in path]


def cycle_payload(ledger: Ledger, curves: dict[str, list[tuple[float, float]]],
                  species: dict[str, Species], verdicts: dict[str, str]) -> dict:
    """cycle.yaml in viewer coordinates, each species id replaced by its payload with the marking status."""
    cycle = yaml.safe_load(CYCLE_FILE.read_bytes())

    def payloads(ids: list[str], where: str) -> list[dict]:
        for key in ids:
            if key not in species:
                raise LedgerError(f"cycle.yaml: {where}: unknown species {key}")
        return [species_payload(species[key], verdicts) for key in ids]

    prologue = {"duration": cycle["prologue"]["duration"], "path": _viewer_path(cycle["prologue"]["path"])}
    steps = cycle["steps"]
    for step in steps:
        where = step["id"]
        if where not in ledger.claims:
            raise LedgerError(f"cycle.yaml: {where} is not a claim id")
        if not 1 <= len(step["path"]) <= 4:
            raise LedgerError(f"cycle.yaml: {where}: path needs 1 to 4 keyframes")
        if step["scene"]["weather"] not in WEATHER:
            raise LedgerError(f"cycle.yaml: {where}: weather must be clear or storm")
        step["path"] = _viewer_path(step["path"])
        step["species"] = payloads(step["species"], where)
        for actor in step["actors"]:
            if actor["type"] in ("water", "gas"):
                if not actor.get("species"):
                    raise LedgerError(f"cycle.yaml: {where}: {actor['type']} actor needs species")
                actor["species"] = payloads(actor["species"], where)
            elif actor["type"] == "placeholder":
                actor["at"] = list(to_viewer(*actor["at"]))
    # a curve's z is the viewer's Y, so the curves need no conversion
    return {"notice": NOTICE, "prologue": prologue, "steps": steps, "curves": curves}


def main() -> None:
    led = load()
    results = screening.all_results(led)
    decided = screening.verdicts(led, results)
    species = load_species(step_ids=set(led.claims))
    wet = sorted({
        actor["space"]
        for step in yaml.safe_load(CYCLE_FILE.read_bytes())["steps"]
        for actor in step["actors"] if actor["type"] == "water"
    })
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    with session():
        model = build(led)
        write_glb(model, OUT_DIR / "interior.glb")
        # the model's volume tags are valid only while this session is open
        curves = {name: level_volume_curve(model, name) for name in wet}
    with session():  # a fresh session, so that nothing of the first model is left in the kernel
        write_glb(build(led, variants=ALTERNATIVE), OUT_DIR / "interior_alt.glb")

    # the marking rule reads the verdict word alone; the basis sentence goes to claims.json
    statuses = {claim: status for claim, (status, _) in decided.items()}
    for name, payload in (("claims.json", claims_payload(led, results, decided)),
                          ("cycle.json", cycle_payload(led, curves, species, statuses))):
        (OUT_DIR / name).write_text(json.dumps(payload, indent=1, allow_nan=False) + "\n")
    provenance.write_manifest(OUT_DIR, "viewer", led)
    for path in sorted(OUT_DIR.iterdir()):
        print(path.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
