# Foundation (Ledger, Geometry, Viewer) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the sourced parameter ledger, the Tier 0 screening table, the parametric 3D geometry of the Great Pyramid's interior, and a browser viewer that animates the claimed cycle with a verdict per step.

**Architecture:** A YAML ledger is the only place numbers and claims live. Pure-Python screening functions and a gmsh-based geometry builder read from it. Exporters turn the ledger, screening results and geometry into static data files that a no-build three.js page displays.

**Tech Stack:** Python 3.12, uv, numpy, scipy, pyyaml, gmsh (OpenCASCADE kernel), trimesh, matplotlib, pytest; three.js r170 as an ES module from a pinned URL.

**Spec:** `docs/superpowers/specs/2026-10-10-foundation-em-reply-design.md` (this plan implements milestones M1, M2 and M3; M4 and M5 get a second plan).

## Global Constraints

- Python 3.12, managed with `uv`. Run everything as `uv run ...`.
- Core dependencies are limited to: numpy, scipy, pyyaml, gmsh, trimesh, matplotlib, pytest. Do not add others.
- No physical number is hard-coded outside `ledger/parameters.yaml`. Code reads values through `Ledger.q(id)`. Pure mathematical constants and unit conversions (`IN = 0.0254`, `g = 9.80665`, `R = 8.314462618`) are the only exceptions and live in the module that uses them.
- Evidence base: `research/00` to `research/09`. Where research files disagree, use the resolution in `research/09-recomputation.md` and record the alternatives in the ledger entry's `note`.
- Verdict vocabulary, exactly: `pass`, `fail`, `conditional`, `undefined`, `pending`.
- Coordinate frame: origin at the pyramid's centre on the pavement; X east, Y north, Z up; metres.
- Viewer coordinates are Y-up: `to_viewer(x, y, z) = (x, z, -y)`. Only `pyramid/geometry/export.py` and `pyramid/viewer_data.py` apply this mapping.
- The viewer has no build step. three.js is loaded from `https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js` and add-ons from `https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/` through an import map.
- Nothing the hypothesis leaves unspecified is drawn as a concrete object. The pump, the valves, the reservoir, the gallery drain, the gas inlet and any other unspecified mechanism appear as dashed placeholders labelled "not specified by the hypothesis".
- The claims ledger holds S01 to S31 and E01 to E40. E41 (a Red Pyramid analogy) and E42 (from the radar-scan discussion) in `research/00-hypothesis.md` are outside this project and are not entered.
- The viewer always shows the label: "Animation of the claim. Not a simulation result."
- Every generated result carries a provenance manifest (git commit, ledger hash, library versions).
- Ask the project owner before any download or install that is not a `uv add` of a listed core dependency.
- Commit after every task. End each commit message with the line `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## File Structure

```
pyproject.toml                     project metadata and core dependencies
ledger/parameters.yaml             every physical quantity, sourced
ledger/claims.yaml                 every hypothesis step (S01-S31) and evidence claim (E01-E40)
ledger/cycle.yaml                  authored choreography of the claimed cycle for the viewer
pyramid/__init__.py                REPO_ROOT
pyramid/ledger.py                  load and validate the ledger
pyramid/provenance.py              run manifest
pyramid/screening.py               Tier 0 quantities, verdict rules, table writer
pyramid/geometry/__init__.py       re-exports build, check, Variants, Model, Space
pyramid/geometry/frame.py          unit helpers and the gmsh session context manager
pyramid/geometry/spaces.py         one builder function per interior space
pyramid/geometry/model.py          Variants, Space, Model, build(), check(), level_volume_curve()
pyramid/geometry/export.py         write_step(), write_msh(), write_glb()
pyramid/viewer_data.py             export claims.json and cycle.json for the viewer
viewer/index.html                  page shell and import map
viewer/style.css                   layout and verdict colours
viewer/scene.js                    three.js scene, model loading, toggles, picking
viewer/timeline.js                 cycle player and actors (water, gas, lightning, placeholders)
viewer/panel.js                    side panel, verdict badges, space inspector
viewer/main.js                     boot: fetch data, wire the three modules together
viewer/data/                       generated and committed: interior.glb, interior_alt.glb, claims.json, cycle.json, fields/
results/tier0/                     generated and committed: tier0.md, tier0.json, manifest.json
results/geometry/                  generated, ignored by git: STEP and mesh files
research/petrie-check.md           record of gate G0
tests/test_ledger.py
tests/test_provenance.py
tests/test_screening.py
tests/test_geometry.py
tests/test_export.py
tests/test_viewer_data.py
.claude/launch.json                preview server for the viewer
```

## Shared Interfaces

Every task implements or consumes these exactly. Names, parameters and return types do not change between tasks.

```python
# pyramid/__init__.py
from pathlib import Path
REPO_ROOT: Path                     # the repository root

# pyramid/ledger.py
STATUSES: tuple[str, ...] = ("pass", "fail", "conditional", "undefined", "pending")
UNITS: frozenset[str]               # every unit string allowed in parameters.yaml

class LedgerError(ValueError): ...

@dataclass(frozen=True)
class Quantity:
    id: str                         # dotted lower-case, e.g. "gg.volume"
    value: float
    unit: str
    low: float                      # equals value when no range is known
    high: float
    source: str
    verified: bool
    note: str = ""

@dataclass(frozen=True)
class Claim:
    id: str                         # "S01".."S31", "E01".."E40"
    statement: str
    subsystem: str
    timestamp: str
    tier: int                       # 0, 1 or 2
    piece: int                      # 1..6, the project piece that tests it
    criterion: str
    status: str                     # one of STATUSES
    depends_on: tuple[str, ...]     # quantity ids
    spaces: tuple[str, ...] = ()    # space names this claim involves

@dataclass(frozen=True)
class Ledger:
    quantities: dict[str, Quantity]
    claims: dict[str, Claim]
    digest: str                     # sha256 over the bytes of both YAML files
    def q(self, id: str) -> float: ...                  # value; LedgerError if unknown
    def rng(self, id: str) -> tuple[float, float]: ...  # (low, high)

def load(root: Path | None = None) -> Ledger: ...       # root defaults to REPO_ROOT / "ledger"

# pyramid/provenance.py
def manifest(case: str, ledger: Ledger, extra: dict | None = None) -> dict: ...
def write_manifest(out_dir: Path, case: str, ledger: Ledger, extra: dict | None = None) -> Path: ...

# pyramid/screening.py
@dataclass(frozen=True)
class Result:
    id: str                         # "t0.<name>", e.g. "t0.gallery_fill_pressure"
    label: str
    value: float
    low: float
    high: float
    unit: str
    formula: str                    # plain-text formula a reader can repeat by hand
    inputs: tuple[str, ...]         # quantity ids

def all_results(ledger: Ledger) -> dict[str, Result]: ...
def verdicts(ledger: Ledger, results: dict[str, Result]) -> dict[str, tuple[str, str]]: ...
    # claim id -> (status, one-line basis with the deciding number)
def table_markdown(results: dict[str, Result]) -> str: ...
def main() -> None: ...             # writes results/tier0/{tier0.md,tier0.json,manifest.json}

# pyramid/geometry/frame.py
IN: float = 0.0254
def inch(x: float) -> float: ...    # inches to metres
def session(): ...                  # context manager: gmsh.initialize() ... gmsh.finalize()

# pyramid/geometry/model.py
@dataclass(frozen=True)
class Variants:
    casing: bool = True
    kc_shafts_open: bool = True
    kc_shaft_ends_level: bool = False
    portcullis: bool = True
    grooves_connected: bool = False
    ascending_plugs: bool = True
    pit_excavated: bool = False
    big_void_inclined: bool = False
    apex_truncated: bool = True

@dataclass(frozen=True)
class Space:
    name: str                       # snake_case; becomes the glTF node name
    label: str                      # human-readable
    tag: int                        # gmsh OCC volume tag
    volume: float                   # m3
    volume_id: str | None           # ledger quantity id it is checked against

@dataclass(frozen=True)
class Model:
    level: str                      # "survey" or "paper"
    variants: Variants
    spaces: dict[str, Space]        # interior spaces only
    masonry: int                    # OCC volume tag of pyramid minus spaces
    bedrock: int | None             # OCC volume tag, None at level "paper"

def build(ledger: Ledger, level: str = "survey", variants: Variants = Variants()) -> Model: ...
    # must be called inside frame.session()
def check(model: Model, ledger: Ledger) -> list[str]: ...
    # human-readable failures; empty list means every self-check passed
def level_volume_curve(model: Model, name: str, n: int = 40) -> list[tuple[float, float]]: ...
    # (z in metres, volume of the space below z in m3), z ascending

# pyramid/geometry/export.py
def to_viewer(x: float, y: float, z: float) -> tuple[float, float, float]: ...
def write_step(model: Model, path: Path) -> None: ...
def write_msh(model: Model, path: Path, size: float) -> None: ...
def write_glb(model: Model, path: Path) -> None: ...   # one named node per space, plus "masonry" and "bedrock"

# pyramid/viewer_data.py
def claims_payload(ledger: Ledger, results: dict[str, Result],
                   verdicts: dict[str, tuple[str, str]]) -> dict: ...
def cycle_payload(ledger: Ledger, curves: dict[str, list[tuple[float, float]]]) -> dict: ...
def main() -> None: ...             # writes viewer/data/{interior.glb,interior_alt.glb,claims.json,cycle.json}
```

`interior.glb` is the default `Variants()`. `interior_alt.glb` is the alternative reading of the survey: `Variants(kc_shaft_ends_level=True, grooves_connected=True, pit_excavated=True, big_void_inclined=True, apex_truncated=False)`. The viewer has one toggle that swaps between them.

Space names at level `survey`, in build order:

`descending_passage`, `subterranean_chamber`, `pit`, `south_passage`, `well_shaft`, `grotto`, `ascending_passage`, `queens_passage`, `queens_chamber`, `qc_shaft_north`, `qc_shaft_south`, `grand_gallery`, `antechamber`, `kings_chamber`, `kc_shaft_north`, `kc_shaft_south`, `relieving_chambers`, `big_void`, `north_face_corridor`.

Space names at level `paper`: `paper_kings_chamber`, `paper_queens_chamber`, `paper_lower_chamber`.

Viewer data contracts:

```jsonc
// viewer/data/claims.json
{
  "manifest": { "case": "viewer", "commit": "...", "ledger": "...", "versions": {} },
  "claims": [
    { "id": "S10", "statement": "...", "subsystem": "hydraulic", "timestamp": "F 00:41:15",
      "tier": 0, "piece": 3, "criterion": "...", "status": "fail", "basis": "...",
      "numbers": [ { "label": "...", "value": 0.8e6, "low": 0.7e6, "high": 0.9e6, "unit": "Pa" } ],
      "spaces": ["descending_passage"] }
  ],
  "spaces": {
    "grand_gallery": { "label": "Grand Gallery",
      "quantities": [ { "id": "gg.volume", "value": 573.0, "unit": "m3", "source": "..." } ],
      "claims": ["S12", "S13"] }
  }
}

// viewer/data/cycle.json   (all positions in viewer coordinates)
{
  "notice": "Animation of the claim. Not a simulation result.",
  "steps": [
    { "id": "S10", "title": "...", "duration": 6.0,
      "camera": { "position": [0, 0, 0], "target": [0, 0, 0] },
      "actors": [
        { "type": "water", "space": "grand_gallery", "from": 0.0, "to": 1.0 },
        { "type": "gas", "path": ["kings_chamber", "antechamber", "grand_gallery"], "color": "#d9c24a" },
        { "type": "placeholder", "kind": "pump", "at": [0, 0, 0], "label": "Pump: not specified by the hypothesis" },
        { "type": "lightning" },
        { "type": "field", "slice": "fields/R1_230m.png" }
      ] }
  ],
  "curves": { "grand_gallery": [[0.0, 0.0], [1.0, 12.5]] }   // level_volume_curve, z in viewer Y
}
```

Water actors give the fill fraction of the space's volume (0 to 1) at the start and end of the step; the viewer converts a fraction to a height with the space's curve.

Contract notes that several tasks rely on:

- Both ledger files are YAML lists. `parameters.yaml` has one flow mapping per line; `low` and `high` default to `value` and `note` to an empty string. A claim's `depends_on` holds quantity ids only, never `t0.*` result ids.
- `screening.verdicts()` returns an entry for every claim. A claim that no rule covers keeps its ledger status with the basis "No Tier 0 rule; tested in piece N."
- The viewer shows, for a claim, the results whose `inputs` are all contained in that claim's `depends_on`. A claim must therefore list every quantity its deciding calculation reads.
- In `claims.json` a non-finite `value`, `low` or `high` is written as `null`. `manifest.fields` lists the field-slice files present under `viewer/data/fields/`; the viewer draws a slice only if it is listed.
- `write_step`, `write_msh` and `write_glb` act on everything in the current gmsh session, so each model is built and exported in its own `frame.session()`.
- `write_glb` writes vertices already in viewer coordinates and leaves triangle winding as gmsh gives it, so the viewer renders meshes double-sided.
- Modules are run from the repository root as `uv run python -m pyramid.<module>`. `.python-version` and `uv.lock` are committed.

---
