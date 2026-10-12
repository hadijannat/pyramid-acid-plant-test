"""python -m pyramid.chem: results, verdicts, time series and figures under results/chem/."""
import json
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # no display: the figures go straight to files
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from pyramid import chem  # noqa: E402
from pyramid.chem import aqueous, feed, transfer, walls  # noqa: E402
from pyramid.ledger import Ledger, load  # noqa: E402
from pyramid.screening import DAY  # noqa: E402
from pyramid.simkit import RESULTS, write_results  # noqa: E402

ASSUMPTIONS = [
    "The batch is Tier 0's largest: one King's Chamber of pure sulfur dioxide at one atmosphere per cycle.",
    "The hypothesis states no cycle time; one day is taken, as Tier 0 does for S20, with a range of one hour to one "
    "year.",
    "S19: the Gallery is half full, the mean of the rise, with mixed gas above mixed water and a gas film and a "
    "liquid film in series at the level surface.",
    "S19: the water takes the undissociated gas in proportion to its pressure; dissociation enters the equilibrium "
    "share only, and sulfur dioxide carried out with displaced air is not deducted.",
    "S19: the gas-side coefficient runs from diffusion through still gas to natural convection; no source gives it.",
    "S22: a full stroke draws one Gallery volume of gas, of which the King's Chamber can supply only its own "
    "volume; the rest is the outside air of S14.",
    "S22: the rising water is credited with all the sulfur dioxide, every mole of oxygen the oxidation can use, and "
    "nitrogen and oxygen up to their solubility in water that arrives free of dissolved gas.",
    "S23: each cycle starts with fresh water; bare limestone neutralises acid until gypsum saturates, then a layer "
    "grows only as fast as acid diffuses through it, with the measured diffusivity of the ledger.",
    "S23: the fresh water of the next cycle dissolves gypsum up to its solubility if it comes to saturation, and at "
    "the least what diffusion alone carries into still water in the time it stands, which the hypothesis does not "
    "state; the ledger takes its drain time over its cycle time, with a range from the shortest drain in the "
    "longest cycle to a dwell equal to the acid's.",
    "S23: the acid of the next batch thins a layer and cannot strip it, because the layer grows from beneath as it "
    "dissolves outside; counting all the batch's sulfate as free thins it least, and the share left with the "
    "ledger's bisulfate constant is given beside it.",
    "S01 and E01: one mole of hydrogen sulfide per mole of sulfur dioxide, with no loss in the conversion.",
    "The oxidation follows the ledger's iron law and stops when the dissolved oxygen is used up; concentrations "
    "stand for activities.",
]


def _save(fig, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=150, metadata={"Software": None})  # no version or time stamp in the file
    plt.close(fig)


def _capture(q, ledger: Ledger, out: Path) -> dict:
    low, high = ledger.rng("rx.kg_gas")
    coefficients = sorted({*np.geomspace(low, high, 4).tolist(), q["rx.kg_gas"]})  # the ledger's range and value
    fig, ax = plt.subplots(figsize=(7, 4.2))
    series = {}
    for k in coefficients:
        times, share = transfer.capture_series(q, k)
        series[f"{k:.3g}"] = share.tolist()
        ax.plot(times / chem.HOUR, 100 * share, label=f"{1e3 * k:.2g} mm/s")
    for line, text in ((90, "passes from 90 percent"), (50, "fails below 50 percent")):
        ax.axhline(line, color="0.4", linestyle="--", linewidth=0.8)
        ax.annotate(text, (12.5, line + 1.5), fontsize=8, color="0.3")
    ax.set(xlabel="hours into the cycle", ylabel="sulfur dioxide in the water, percent", ylim=(0, 100),
           title="S19: sulfur captured, half-full Gallery, by gas-side coefficient")
    ax.legend(title="gas-side coefficient", fontsize=8)
    _save(fig, out / "figures" / "capture.png")
    return {"hours": (times / chem.HOUR).tolist(), "share_by_gas_coefficient_m_per_s": series}


def _pushback(q, results, out: Path) -> dict:
    air = np.linspace(0.0, 1.0, 401)
    forced = [aqueous.forced_back(q, a) for a in air]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(100 * air, 100 * np.array(forced), color="C0")
    least = results["chem.least_air"]
    ax.axvspan(100 * least.low, 100 * least.high, color="C1", alpha=0.2)
    marks = ((aqueous.air_without_pushback(q), "nothing pushed back below this"),
             (least.value, "least air of a full stroke"),
             (aqueous.stoichiometric_air(q), "oxygen for all the sulfur"))
    for at, text in marks:
        ax.axvline(100 * at, color="0.4", linestyle="--", linewidth=0.8)
        ax.annotate(text, (100 * at + 1, 92), rotation=90, fontsize=8, color="0.3", va="top")
    ax.set(xlabel="air in the gas over the water, percent", ylabel="gas pushed back, percent of the gas drawn",
           xlim=(0, 100), ylim=(0, 100), title="S22: gas the rising water cannot take up")
    _save(fig, out / "figures" / "pushback.png")
    return {"air_share": air.tolist(), "forced_back_share": forced}


def _layer(q, ledger: Ledger, out: Path) -> dict:
    shortest, longest = ledger.rng("rx.fresh_dwell")
    # The fresh water's dwell at the long end of its range, at the ledger's value and at the short end.
    dwells = {"still_longest_dwell": longest, "still": q["rx.fresh_dwell"], "still_shortest_dwell": shortest}
    runs = {"saturating": walls.cycles(q, "saturating")} | {
        name: walls.cycles(q | {"rx.fresh_dwell": dwell}, "still") for name, dwell in dwells.items()}
    product, within = walls.growth_product(q), np.linspace(0.0, 1.0, 25)
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(7, 5.6), sharex=True)
    for (name, dwell), colour in zip(dwells.items(), ("C1", "C0", "C2")):
        run, steps, layer, left = runs[name], [], [], 0.0
        for k in range(chem.CYCLES):  # the layer grows through each acid dwell and meets the next fill at its end
            steps += list(k + within) + [k + 1.0]
            layer += list(walls.thickness(product, within * q["rx.cycle_time"], left)) + [run["after_fill"][k]]
            left = run["after_fill"][k]
        top.plot(steps, 1e6 * np.array(layer), color=colour, label=f"{dwell:g} times as long as the acid")
        bottom.step(range(0, chem.CYCLES + 1), [0.0] + [1e3 * w for w in run["loss"]], where="pre", color=colour)
    top.set(ylabel="gypsum layer, micrometres", title="S23: gypsum layer and wall loss over ten cycles")
    top.annotate(f"a saturating fill dissolves {1e6 * walls.fill_dissolves(q):.0f} micrometres\na layer that "
                 "survives is drawn as grown undisturbed,\nan upper bound: still acid thins it",
                 (0.98, 0.40), xycoords="axes fraction", ha="right", va="bottom", fontsize=8)
    top.legend(title="a still fill stands", fontsize=8, title_fontsize=8, loc="upper left")
    bottom.set(xlabel="fill and drain cycles", ylabel="limestone lost, mm")
    _save(fig, out / "figures" / "layer.png")
    return runs


def _feed(q, ledger: Ledger, out: Path) -> dict:
    low, high = ledger.rng("rx.cycle_time")
    cycle = np.geomspace(low, high, 121)
    flux = feed.batch_moles(q) / cycle
    air_per_mole = feed.cave_air_per_batch(q) / feed.batch_moles(q)  # m3 of cave air at the analogue's ceiling
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.loglog(cycle / DAY, flux, color="C0")
    ax.plot([q["rx.cycle_time"] / DAY], [feed.flux(q)], "o", color="C0")
    ax.annotate(f"one batch every {q['rx.cycle_time'] / chem.HOUR:.0f} h", (q["rx.cycle_time"] / DAY, feed.flux(q)),
                textcoords="offset points",
                xytext=(8, 6), fontsize=8)
    ax.set(xlabel="cycle time, days", ylabel="hydrogen sulfide needed, mol/s",
           title="S01: required feed; 07 gives no measured seep flux to set against it")
    right = ax.secondary_yaxis("right", functions=(lambda f: f * air_per_mole, lambda v: v / air_per_mole))
    right.set_ylabel(f"the same as cave air at {1e6 * q['rx.h2s_cave_air']:.0f} ppmv, m3/s")
    _save(fig, out / "figures" / "feed.png")
    return {"cycle_time_s": cycle.tolist(), "h2s_mol_per_s": flux.tolist(),
            "cave_air_m3_per_s": (flux * air_per_mole).tolist()}


def main(root: Path = RESULTS) -> Path:
    started = time.perf_counter()
    ledger = load()
    results = chem.results(ledger)
    verdicts = chem.verdicts(ledger, results)
    extra = {"assumptions": ASSUMPTIONS, "depends_on": chem.depends_on(ledger)}
    out = write_results("chem", ledger, results, verdicts, extra, root=root)
    (out / "figures").mkdir(exist_ok=True)

    q = {i: ledger.q(i) for row in chem.QUANTITIES for i in row[4]} | {i: ledger.q(i) for i in aqueous.BATCH}
    oxidation = aqueous.oxidise(q, q["rx.cycle_time"])
    series = {
        "capture": _capture(q, ledger, out),
        "pushback": _pushback(q, results, out),
        "layer": _layer(q, ledger, out),
        "feed": _feed(q, ledger, out),
        "oxidation": {key: values.tolist() for key, values in oxidation.items()},
    }
    for name, data in series.items():
        (out / f"{name}.json").write_text(json.dumps(data, indent=1) + "\n")

    for claim, (status, basis) in verdicts.items():
        print(f"{claim} {status}: {basis}")
    print(f"chem: {len(results)} results, {len(verdicts)} verdicts in {time.perf_counter() - started:.1f} s -> {out}")
    return out


if __name__ == "__main__":
    main()
