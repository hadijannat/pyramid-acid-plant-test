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

NOTICE = "Animation of the claim. Not a simulation result."
CYCLE_FILE = REPO_ROOT / "ledger" / "cycle.yaml"
OUT_DIR = REPO_ROOT / "viewer" / "data"

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


def cycle_payload(ledger: Ledger, curves: dict[str, list[tuple[float, float]]]) -> dict:
    steps = yaml.safe_load(CYCLE_FILE.read_text())
    for step in steps:
        if step["id"] not in ledger.claims:
            raise LedgerError(f"cycle.yaml: {step['id']} is not a claim id")
        for key in ("position", "target"):
            step["camera"][key] = list(to_viewer(*step["camera"][key]))
        for actor in step["actors"]:
            if actor["type"] == "placeholder":
                actor["at"] = list(to_viewer(*actor["at"]))
    # a curve's z is the viewer's Y, so the curves need no conversion
    return {"notice": NOTICE, "steps": steps, "curves": curves}


def main() -> None:
    led = load()
    results = screening.all_results(led)
    wet = sorted({
        actor["space"]
        for step in yaml.safe_load(CYCLE_FILE.read_text())
        for actor in step["actors"] if actor["type"] == "water"
    })
    (OUT_DIR / "fields").mkdir(parents=True, exist_ok=True)

    with session():
        model = build(led)
        write_glb(model, OUT_DIR / "interior.glb")
        # the model's volume tags are valid only while this session is open
        curves = {name: level_volume_curve(model, name) for name in wet}
    with session():  # a fresh session, so that nothing of the first model is left in the kernel
        write_glb(build(led, variants=ALTERNATIVE), OUT_DIR / "interior_alt.glb")

    # Field slices come with the solver results of the second plan. The viewer draws only the
    # slices listed here, so it never asks the server for a file that is not there.
    extra = {"fields": sorted(f"fields/{path.name}" for path in (OUT_DIR / "fields").glob("*.png"))}
    claims = claims_payload(led, results, screening.verdicts(led, results))
    claims["manifest"].update(extra)
    for name, payload in (("claims.json", claims), ("cycle.json", cycle_payload(led, curves))):
        (OUT_DIR / name).write_text(json.dumps(payload, indent=1, allow_nan=False) + "\n")
    provenance.write_manifest(OUT_DIR, "viewer", led, extra)
    for path in sorted(OUT_DIR.iterdir()):
        print(path.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
