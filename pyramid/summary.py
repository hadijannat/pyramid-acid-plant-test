"""The verdict on every claim, from Tier 0 and the simulation packages: results/summary/.

verdicts.md and verdicts.json are the table; verdict-map.svg is one tile per claim, decided-by.svg the verdicts
by what decided them, cycle-elevation.svg the process steps on the interior's elevation; and report.md gives the
claims, their deciding numbers, the figures and the assumptions, grouped by what decided them.
"""
import json
from collections import Counter
from pathlib import Path

import matplotlib

from pyramid import screening
from pyramid.ledger import STATUSES, Ledger, LedgerError, load
from pyramid.provenance import write_manifest
from pyramid.simkit import RESULTS, read_results
from pyramid.verdicts import PACKAGES, merged, stale

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT_DIR = RESULTS / "summary"
# The viewer's verdict colours (viewer/style.css) and a mark, so that a tile does not rest on colour alone.
MARKS = {"pass": ("#56b884", "✓"), "fail": ("#e0655f", "✗"), "conditional": ("#e3aa45", "~"),
         "undefined": ("#8f949c", "?"), "pending": ("#7f9db8", "…"), "not_testable": ("#6f6a7c", "–")}
DECIDERS = {
    "tier0": "Tier 0 screening: closed-form bounds computed from the ledger",
    "premises": "Geometric premises: the survey record against each criterion",
    "evidence": "Documentary checks: what the research files found in the sources",
    "flow": "Water and gas movement: reduced hydraulic and gas-network models",
    "chem": "Chemistry and feed: gas transfer, oxidation, wall attack and the feed",
    "electro": "Ground current, lightning, the piezoelectric chain and room acoustics",
    "em": "The 2018 electromagnetic study: two full-wave field solvers",
    "none": "Not yet decided",
}
SHORT = {   # the deciders as the figures name them
    "tier0": "Tier 0 screening\nhand calculations", "premises": "Geometric premises\nthe survey record",
    "evidence": "Documentary register\nthe sources read", "flow": "Water and gas\nreduced models",
    "chem": "Chemistry and feed\nreduced models", "electro": "Conduction and acoustics\nreduced models",
    "em": "The 2018 field study\ntwo full-wave solvers",
}
INK = "#14161a"
WORDS = """\
- `pass`: the criterion holds even at the end of each input's range least favourable to the hypothesis; for a \
documentary claim, a source that was read meets it.
- `fail`: it fails even at the most favourable end; for a documentary claim, a source that would show it was read \
and does not, or contradicts it.
- `conditional`: the outcome differs between the ends of a range the ledger carries, and the basis names the input \
on which it turns; for a documentary claim, it is partly met, or rests on a secondary source or on a measurement \
nobody has made.
- `undefined`: the criterion cannot be evaluated without an input the hypothesis does not state, or the claim names \
no source that could be checked.
- `not testable`: the claim's own criterion says no computation or document can decide it.
- `pending`: not yet decided.
"""


def table(ledger: Ledger, verdicts: dict[str, tuple[str, str]], source: dict[str, str]) -> str:
    rows = "".join(
        f"| {claim.id} | {claim.statement} | {verdicts[claim.id][0]} | {source[claim.id]} | {verdicts[claim.id][1]} |\n"
        for claim in ledger.claims.values()
    )
    return "| Claim | Statement | Status | Decided by | Basis |\n|---|---|---|---|---|\n" + rows


def counts(verdicts: dict[str, tuple[str, str]]) -> dict[str, int]:
    """How many claims carry each verdict word, in the vocabulary's order."""
    tally = Counter(status for status, _ in verdicts.values())
    return {status: tally[status] for status in STATUSES}


def headline(tally: dict[str, int]) -> str:
    return ", ".join(f"{n} {status.replace('_', ' ')}" for status, n in tally.items())


def verdict_map(ledger: Ledger, verdicts: dict[str, tuple[str, str]], path: Path, columns: int = 20) -> None:
    """One tile per claim, coloured and marked by its verdict: the process steps above the evidence claims."""
    plt.rcParams["svg.hashsalt"] = "pyramid"   # the same verdicts give the same file, byte for byte
    fig, ax = plt.subplots(figsize=(11, 4.2))
    y = 0.0

    def tile(x, y, status, size=0.94):
        ax.add_patch(plt.Rectangle((x, y), size, size, color=MARKS[status][0], linewidth=0))

    for title, letter in (("Process steps as claimed", "S"), ("Evidence claims", "E")):
        ids = [claim for claim in ledger.claims if claim.startswith(letter)]
        ax.text(0, y + 0.3, title, fontsize=10, color="#14161a", va="center")
        y += 0.7
        for n, claim in enumerate(ids):
            status = verdicts[claim][0]
            x, row = n % columns, y + n // columns
            ink = "white" if status == "not_testable" else "#14161a"   # the one colour too dark for dark ink
            tile(x, row, status)
            ax.text(x + 0.47, row + 0.34, claim, ha="center", va="center", fontsize=8, color=ink, weight="bold")
            ax.text(x + 0.47, row + 0.70, MARKS[status][1], ha="center", va="center", fontsize=8, color=ink)
        y += -(-len(ids) // columns) + 0.4
    x = 0.0
    for status, n in counts(verdicts).items():
        if n:
            tile(x, y + 0.1, status, 0.5)
            ax.text(x + 0.25, y + 0.36, MARKS[status][1], ha="center", va="center", fontsize=8,
                    color="white" if status == "not_testable" else "#14161a")
            ax.text(x + 0.65, y + 0.36, f"{n} {status.replace('_', ' ')}", fontsize=9, color="#14161a", va="center")
            x += 3.3
    ax.set_xlim(0, columns)
    ax.set_ylim(y + 0.9, -0.1)   # y runs down the page
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(path, metadata={"Date": None}, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _ink(status: str) -> str:
    return "white" if status == "not_testable" else INK   # the one colour too dark for dark ink


def _legend(ax, statuses, **kw) -> None:
    handles = [plt.Rectangle((0, 0), 1, 1, color=MARKS[s][0]) for s in statuses]
    ax.legend(handles, [s.replace("_", " ") for s in statuses], frameon=False, fontsize=8.5, handlelength=1.2, **kw)


def decided_by(verdicts: dict[str, tuple[str, str]], source: dict[str, str], path: Path) -> None:
    """Stacked bars of the verdicts by what decided them, in the order the packages are read."""
    plt.rcParams["svg.hashsalt"] = "pyramid"
    present = [s for s in STATUSES if any(status == s for status, _ in verdicts.values())]
    rows = [(key, SHORT.get(key, about)) for key, about in DECIDERS.items() if key in source.values()]   # none: pending
    totals = Counter(source.values())
    assert sum(totals[key] for key, _ in rows) == len(verdicts), "every claim is decided by one of the deciders"
    fig, ax = plt.subplots(figsize=(9, 0.5 * len(rows) + 0.4))
    for row, (key, label) in enumerate(rows):
        tally = Counter(status for claim, (status, _) in verdicts.items() if source[claim] == key)
        x = 0
        for status in present:
            if n := tally[status]:
                ax.barh(row, n, left=x, color=MARKS[status][0], height=0.72, linewidth=0)
                ax.text(x + n / 2, row, str(n), ha="center", va="center", fontsize=9, weight="bold", color=_ink(status))
                x += n
        ax.text(x + 0.4, row, str(x), va="center", fontsize=9, color="#555")
        ax.text(-0.5, row, label, ha="right", va="center", fontsize=9, color=INK, linespacing=1.15)
    ax.set_xlim(0, max(totals.values()) + 3)   # room for the total at the end of the longest bar
    ax.set_ylim(len(rows) - 0.4, -0.6)
    ax.axis("off")
    _legend(ax, present, loc="lower right", ncol=len(present), bbox_to_anchor=(1.0, -0.02))
    ax.set_title(f"What decided the {len(verdicts)} claims", fontsize=11, loc="left", color=INK)
    fig.savefig(path, metadata={"Date": None}, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# A space with no label of its own on the elevation joins its neighbour's.
GROUPED = {"pit": "subterranean_chamber", "south_passage": "subterranean_chamber", "queens_passage": "queens_chamber",
           "kc_shaft_south": "kc_shaft_north", "qc_shaft_north": "qc_shaft_south"}
# The elevation's labels, spread apart where a row of steps goes under them (display choices).
SPREAD = {"King's Chamber": ("kings_chamber", (-64, 53)), "Antechamber": ("antechamber", (-50, 37)),
          "Queen's Chamber": ("queens_chamber", (-48, 21)), "Queen's Chamber shafts": ("qc_shaft_south", (-78, 5), (-10, 30)),
          "Grand Gallery": ("grand_gallery", (60, 58)), "Big Void (muon image)": ("big_void", (-8, 88)),
          "King's Chamber shafts": ("kc_shaft_north", (64, 90), (45, 75))}


def cycle_elevation(ledger: Ledger, verdicts: dict[str, tuple[str, str]], path: Path) -> None:
    """The process steps on the north-south elevation, each once at the first space its claim names, by verdict."""
    import trimesh

    from pyramid import elevation

    plt.rcParams["svg.hashsalt"] = "pyramid"
    labels = {**elevation.LABELS, **SPREAD}
    steps = [claim for claim in ledger.claims.values() if claim.id.startswith("S")]
    at_space: dict[str, list[str]] = {}
    for claim in steps:
        if claim.spaces:
            at_space.setdefault(GROUPED.get(claim.spaces[0], claim.spaces[0]), []).append(claim.id)
    outside = [claim.id for claim in steps if not claim.spaces]

    def chip(anchor, dx, dy, claim):
        status = verdicts[claim][0]
        ax.annotate(claim, xy=anchor, xytext=(dx, dy), textcoords="offset points", fontsize=7.2, weight="bold",
                    ha="center", va="center", color=_ink(status),
                    bbox=dict(boxstyle="round,pad=0.22,rounding_size=0.3", fc=MARKS[status][0], ec="none"))

    assert set(at_space) <= {space for space, *_ in labels.values()}, "a step's first space has no label"
    fig, ax = plt.subplots(figsize=(13, 9))
    _, targets = elevation.draw(ax, trimesh.load(elevation.GLB), labels)
    for text, (space, (tx, ty), *_) in labels.items():
        ids = at_space.get(space, [])
        side = 11 if targets[text][1] < ty else -11   # the row of chips on the side away from the label's leader
        for i, claim in enumerate(ids):   # 20 pt per chip, centred on the label
            chip((tx, ty), (i - (len(ids) - 1) / 2) * 20, side, claim)
    ax.text(132, 138, "Outside the modelled interior", fontsize=9, color=INK, ha="right", va="center")
    for i, claim in enumerate(outside):
        chip((132, 138), -(len(outside) - 1 - i) * 20 - 6, -12, claim)
    present = [s for s in STATUSES if any(verdicts[c.id][0] == s for c in steps)]
    _legend(ax, present, loc="upper left", ncol=1, alignment="left", title_fontsize=8.5,
            title="Each process step once, at the first\nspace its claim names, by verdict")
    elevation.frame(ax)
    ax.set_title("The claimed cycle on the north-south elevation", fontsize=11, loc="left", color=INK)
    fig.savefig(path, metadata={"Date": None}, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def report(ledger: Ledger, verdicts: dict[str, tuple[str, str]], source: dict[str, str], root: Path = RESULTS) -> str:
    """The claims, deciding numbers, figures and assumptions of each decider, as markdown beside the verdict map."""
    text = ("# Results\n\nGenerated by `uv run python -m pyramid.summary`. Do not edit by hand.\n\n"
            f"{len(ledger.claims)} claims: {headline(counts(verdicts))}.\n\n![One tile per claim, coloured and "
            f"marked by its verdict](verdict-map.svg)\n\n![The verdicts by what decided them](decided-by.svg)\n\n"
            "![The process steps on the north-south elevation, each at the first space its claim names, coloured by "
            f"its verdict](cycle-elevation.svg)\n\n{WORDS}\n")
    for decider, about in DECIDERS.items():
        decided = [claim for claim in ledger.claims.values() if source[claim.id] == decider]
        if not decided:
            continue
        stored = read_results(decider, root) if decider in PACKAGES else None
        results = screening.all_results(ledger) if decider == "tier0" else stored[0] if stored else {}
        assumptions = stored[2].get("assumptions", []) if stored else []
        tally = Counter(verdicts[claim.id][0] for claim in decided)
        text += f"\n## {about}\n\n{len(decided)} claims: {headline({s: tally[s] for s in STATUSES if tally[s]})}.\n\n"
        for figure in sorted((root / decider / "figures").glob("*.png")):
            text += f"![{figure.stem}](../{decider}/figures/{figure.name})\n\n"
        text += "| Claim | Statement | Status | Basis |\n|---|---|---|---|\n" + "".join(
            f"| {claim.id} | {claim.statement} | {verdicts[claim.id][0]} | {verdicts[claim.id][1]} |\n"
            for claim in decided)
        if results:
            text += (f"\n<details><summary>{len(results)} computed quantities. Low and high are the ends over the "
                     "ledger's ranges where the package varied its inputs; they repeat the value where it ran one "
                     f"case</summary>\n\n{screening.table_markdown(results)}\n</details>\n")
        if assumptions:
            text += (f"\n<details><summary>{len(assumptions)} modelling assumptions</summary>\n\n"
                     + "".join(f"- {line}\n" for line in assumptions) + "\n</details>\n")
    return text


def main() -> None:
    ledger = load()
    if old := stale(ledger):   # their verdicts would go out under this ledger's digest
        raise LedgerError(f"results of {', '.join(old)} were generated from other sources: run those packages first")
    _, verdicts, source = merged(ledger)
    tally = counts(verdicts)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "verdicts.md").write_text(
        "# Verdicts\n\nGenerated by `uv run python -m pyramid.summary`. Do not edit by hand.\n\n"
        + headline(tally) + ".\n\n" + table(ledger, verdicts, source)
    )
    payload = {
        "counts": tally,
        "verdicts": {claim: {"status": status, "basis": basis, "source": source[claim]}
                     for claim, (status, basis) in verdicts.items()},
    }
    (OUT_DIR / "verdicts.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    verdict_map(ledger, verdicts, OUT_DIR / "verdict-map.svg")
    decided_by(verdicts, source, OUT_DIR / "decided-by.svg")
    cycle_elevation(ledger, verdicts, OUT_DIR / "cycle-elevation.svg")
    (OUT_DIR / "report.md").write_text(report(ledger, verdicts, source))
    write_manifest(OUT_DIR, "summary", ledger)
    print(", ".join(f"{n} {status}" for status, n in tally.items()))


if __name__ == "__main__":
    main()
