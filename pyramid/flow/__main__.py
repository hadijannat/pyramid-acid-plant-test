"""python -m pyramid.flow: every flow result and verdict, three figures and their series, to results/flow."""
import json
import math
import time
from dataclasses import asdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from pyramid import simkit  # noqa: E402
from pyramid.flow import ASSUMPTIONS, all_results, gas, hydraulics, network, retention, verdicts  # noqa: E402
from pyramid.ledger import load  # noqa: E402
from pyramid.screening import YEAR  # noqa: E402


def _save(figure, path: Path) -> None:
    figure.savefig(path, dpi=150, metadata={"Software": None})  # no version or date in the file
    plt.close(figure)


def ingress(q) -> dict:
    """S13: depth of water in the King's Chamber against time, the Gallery held full, for three openings."""
    floor, ceiling = q["kc.floor.z"], q["kc.floor.z"] + q["kc.height"]
    cases = {
        "grooves alone": q["ante.groove_connected_area"],
        "grooves and slab clearance": hydraulics.loose_area(q),
        "no slab in the passage": q["ante.low_passage.width"] * q["ante.low_passage.height"],
    }
    series = {}
    for name, area in cases.items():
        link = (0, 1, floor, q["flow.discharge_coefficient"] * area)
        times, levels = hydraulics.simulate([math.inf, hydraulics.flood_area(q)], [q["gg.roof_top.z"], floor], [link],
                                            1e7, until=(1, ceiling))
        # the run stops at the ceiling, long before 1e7 s, so the evenly spaced samples miss it: sample again
        times, levels = hydraulics.simulate([math.inf, hydraulics.flood_area(q)], [q["gg.roof_top.z"], floor], [link],
                                            float(times[-1]))
        series[name] = {"area_m2": area, "time_s": times.tolist(), "depth_m": (levels[:, 1] - floor).tolist()}
    return {"mouth_height_m": q["kcs.mouth_height"], "chamber_height_m": q["kc.height"], "cases": series}


def shares(ledger, q) -> dict:
    """S14, S17: share of the displaced volume by path against the open area of the antechamber path."""
    areas = np.geomspace(1e-4, q["ante.low_passage.width"] * q["ante.low_passage.height"], 60)
    curves = []
    for aperture in (ledger.rng("hydro.joint_aperture")[0], q["hydro.joint_aperture"]):
        for drain in (*ledger.rng("hydro.drain_time"), q["hydro.drain_time"]):
            case = q | {"hydro.joint_aperture": aperture, "hydro.drain_time": drain}
            drawn = [gas.draw(case, area=float(area)) for area in areas]
            curves.append({"joint_aperture_m": aperture, "drain_time_s": drain,
                           "antechamber_share": [d[1] for d in drawn], "joint_share": [d[2] for d in drawn],
                           "pressure_difference_pa": [d[0] for d in drawn]})
    return {"area_m2": areas.tolist(), "grooves_m2": q["ante.groove_connected_area"],
            "grooves_and_clearance_m2": gas.opening_area(q), "curves": curves}


def retained(ledger, q) -> dict:
    """S03: retention half-time against wind speed, for a pure charge and for thinner ones."""
    winds = np.linspace(0.0, 45.0, 181)
    low, high = ledger.rng("flow.wind_pressure_coefficient_difference")
    curves = {f"{fraction:g}": [retention.half_time(q, float(wind), fraction) for wind in winds]
              for fraction in (1.0, 0.3, 0.1, 0.01)}
    band = {name: [retention.half_time(q | {"flow.wind_pressure_coefficient_difference": value}, float(wind))
                   for wind in winds] for name, value in (("low", low), ("high", high))}
    return {"wind_m_s": winds.tolist(), "half_time_s_by_fraction": curves, "half_time_s_pure_by_coefficient": band}


def figures(out: Path, water: dict, gases: dict, kept: dict) -> None:
    (out / "figures").mkdir(exist_ok=True)

    figure, axes = plt.subplots(figsize=(7, 4.2))
    for name, case in water["cases"].items():
        axes.plot(np.array(case["time_s"][1:]) / 60, case["depth_m"][1:], label=f"{name}, {case['area_m2'] * 1e4:.0f} cm2")
    axes.axhline(water["mouth_height_m"], color="grey", linestyle=":", label="shaft mouths")
    axes.axhline(water["chamber_height_m"], color="grey", linestyle="--", label="ceiling")
    axes.set(xscale="log", xlabel="time since the Gallery stood full, minutes", ylabel="water in the King's Chamber, m",
             title="S13: water entering the King's Chamber, the Gallery held full")
    axes.legend(fontsize=8)
    figure.tight_layout()
    _save(figure, out / "figures" / "s13_ingress.png")

    figure, axes = plt.subplots(figsize=(7, 4.2))
    for curve in gases["curves"]:
        style = "-" if curve["joint_aperture_m"] > 1e-4 else "--"
        axes.plot(gases["area_m2"], curve["antechamber_share"], style,
                  label=f"joints {curve['joint_aperture_m'] * 1e3:.2f} mm, drain {curve['drain_time_s'] / 60:.0f} min")
    for area, text in ((gases["grooves_m2"], "grooves"), (gases["grooves_and_clearance_m2"], "with slab clearance")):
        axes.axvline(area, color="grey", linestyle=":")
        axes.text(area, 0.02, f" {text}", fontsize=7, rotation=90, va="bottom")
    for line in (0.5, 0.9):
        axes.axhline(line, color="grey", linewidth=0.6)
    axes.set(xscale="log", xlabel="open area of the antechamber path, m2 (right end: no slab)", ylim=(0, 1.02),
             ylabel="share through the antechamber and shafts",
             title="S14, S17: where the displaced volume comes from")
    axes.legend(fontsize=7)
    figure.tight_layout()
    _save(figure, out / "figures" / "s14_s17_shares.png")

    figure, axes = plt.subplots(figsize=(7, 4.2))
    winds = kept["wind_m_s"]
    axes.fill_between(winds, np.array(kept["half_time_s_pure_by_coefficient"]["high"]) / YEAR,
                      np.array(kept["half_time_s_pure_by_coefficient"]["low"]) / YEAR, alpha=0.2,
                      label="pure, range of the pressure coefficient")
    for fraction, times in kept["half_time_s_by_fraction"].items():
        axes.plot(winds, np.array(times) / YEAR, label=f"sulfur dioxide fraction {fraction}")
    axes.set(yscale="log", xlabel="wind speed at the shaft outlets, m/s", ylabel="retention half-time, years",
             title="S03: how long sulfur dioxide stays with the shafts open")
    axes.legend(fontsize=8)
    figure.tight_layout()
    _save(figure, out / "figures" / "s03_retention.png")


def main(root: Path = simkit.RESULTS) -> Path:
    started = time.perf_counter()
    ledger = load()
    results = all_results(ledger)
    verdict = verdicts(ledger, results)
    out = simkit.write_results("flow", ledger, results, verdict, {"assumptions": ASSUMPTIONS}, root)
    q = {id: quantity.value for id, quantity in ledger.quantities.items()}
    water, gases, kept = ingress(q), shares(ledger, q), retained(ledger, q)
    openings = [asdict(o) | {"at_the_foot": network.at_the_foot(q, o)} for o in network.gallery_openings(q)]
    for name, series in (("ingress", water), ("shares", gases), ("retention", kept), ("openings", openings)):
        (out / f"{name}.json").write_text(json.dumps(series, indent=1) + "\n")
    figures(out, water, gases, kept)
    for claim, (status, basis) in verdict.items():
        print(f"{claim}  {status}\n    {basis}")
    print(f"{len(results)} results, {len(verdict)} verdicts, {time.perf_counter() - started:.1f} s -> {out}")
    return out


if __name__ == "__main__":
    main()
