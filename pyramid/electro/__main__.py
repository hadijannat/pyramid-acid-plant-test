"""python -m pyramid.electro: results, verdicts and figures into results/electro/."""
import json
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from pyramid import electro, simkit  # noqa: E402
from pyramid.electro import rooms, sources  # noqa: E402
from pyramid.ledger import load  # noqa: E402

H = 1.0  # m, the cells at the chamber in the production run


def _section(scene, phi, strength, scale, title, unit, path):
    """Potential (contours) and field strength (colour) on the north-south section through the King's Chamber."""
    i = scene.section
    _, cy, cz = sources.conduction.centres(scene.edges)
    fig, ax = plt.subplots(figsize=(9, 5))
    shown = np.ma.masked_invalid(np.log10(strength[i].T * scale))
    mesh = ax.pcolormesh(scene.edges[1], scene.edges[2], shown, shading="flat", cmap="viridis")
    ax.contour(cy, cz, np.ma.masked_invalid(phi[i].T * scale), levels=24, colors="white", linewidths=0.4)
    ax.set(xlim=(-260, 260), ylim=(-160, 140), xlabel="south to north, m", ylabel="height above the pavement, m",
           title=title, aspect="equal")
    fig.colorbar(mesh, ax=ax, label=f"log10 of the field strength in {unit}")
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)


def _conductivity_sweep(ledger, results, out_dir):
    """The field in the granite against the masonry's conductivity, from wet stone to the driest dense limestone."""
    q = {i: ledger.q(i) for i in electro.MODEL}
    wet, dense = ledger.rng("em.limestone_resistivity_wet")[0], ledger.rng("em.dense_limestone_resistivity")[1]
    resistivity = np.geomspace(wet, dense, 9)
    rows = [sources.lightning_summary(q | {"em.limestone_resistivity": float(rho)}, H) for rho in resistivity]
    median, largest = ledger.q(electro.STROKES[0]), ledger.rng(electro.STROKES[1])[1]
    needed, breakdown = results["electro.needed_field_gas_solid"], ledger.q("em.air_breakdown_field")
    fig, ax = plt.subplots(figsize=(8, 5))
    for current, colour in ((median, "tab:blue"), (largest, "tab:red")):
        ax.loglog(1 / resistivity, [current * row["granite_peak"] for row in rows], color=colour,
                  label=f"peak, {current / 1e3:.0f} kA")
        ax.loglog(1 / resistivity, [current * row["granite_mean"] for row in rows], color=colour, linestyle="--",
                  label=f"volume mean, {current / 1e3:.0f} kA")
    ax.axhline(needed.low, color="black", label="needed by the chain, most generous")
    ax.axhline(needed.value, color="black", linestyle=":", label="needed by the chain, bulk coefficient")
    ax.axhline(breakdown, color="grey", linestyle="-.", label="air breakdown")
    low, high = ledger.rng("em.limestone_resistivity")
    ax.axvspan(1 / high, 1 / low, color="tab:green", alpha=0.2, label="masonry measured in place")
    ax.set(xlabel="conductivity of the masonry, S/m", ylabel="field in the King's Chamber granite, V/m",
           title="Field in the granite at the stroke's peak current (steady conduction)")
    ax.legend(fontsize=7)
    fig.savefig(out_dir / "figures" / "granite_field_against_conductivity.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    return {"limestone_resistivity_ohm_m": resistivity.tolist(),
            "granite_peak_v_per_m_per_a": [row["granite_peak"] for row in rows],
            "granite_mean_v_per_m_per_a": [row["granite_mean"] for row in rows]}


def _decay_figure(ledger, out_dir):
    """Decay time against frequency for the three rooms, with each room's lowest modes."""
    frequency = np.geomspace(3.0, 20e3, 200)
    fig, ax = plt.subplots(figsize=(8, 5))
    series = {"frequency_hz": frequency.tolist()}
    for room, spec in rooms.ROOMS.items():
        q = {i: ledger.q(i) for i in rooms.inputs(room)}
        times = [rooms.decay_time(q, room, float(f)) for f in frequency]
        line, = ax.loglog(frequency, times, label=spec["label"])
        lowest = rooms.modes([q[i] for i in spec["dims"]], q["ac.sound_speed_air"], 4 * rooms.lowest_mode(q, room))
        ax.plot([f for f, _ in lowest], [rooms.decay_time(q, room, f) for f, _ in lowest], "o", color=line.get_color(),
                markersize=3)
        series[room] = {"decay_time_s": times, "lowest_modes_hz": [f for f, _ in lowest]}
    ax.set(xlabel="frequency, Hz", ylabel="decay time T60, s",
           title="Decay time of the three rooms, passages open (dots: lowest modes)")
    ax.legend()
    fig.savefig(out_dir / "figures" / "room_decay_time.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    return series


def main() -> None:
    started = time.time()
    ledger = load()
    results = electro.all_results(ledger, H)
    decided = electro.verdicts(ledger, results)
    out_dir = simkit.write_results("electro", ledger, results, decided, {
        "assumptions": electro.ASSUMPTIONS, "cell_at_the_chamber_m": H, "half_width_of_the_ground_m": sources.EXTENT,
    })
    (out_dir / "figures").mkdir(exist_ok=True)
    q = {i: ledger.q(i) for i in electro.MODEL}
    storm, median = ledger.q(electro.FAR_FIELDS[0]), ledger.q(electro.STROKES[0])
    _section(*sources.telluric(q, H), storm, f"Telluric far field of {storm:g} V/m, north-south", "V/m",
             out_dir / "figures" / "telluric_section.png")
    _section(*sources.lightning(q, H), median, f"Stroke of {median / 1e3:.0f} kA at the summit, steady conduction",
             "V/m", out_dir / "figures" / "lightning_section.png")
    sweep = _conductivity_sweep(ledger, results, out_dir)
    (out_dir / "conductivity_sweep.json").write_text(json.dumps(sweep, indent=2) + "\n")
    (out_dir / "rooms.json").write_text(json.dumps(_decay_figure(ledger, out_dir), indent=2) + "\n")
    for result in results.values():
        print(f"{result.id:44s} {result.value:11.4g}  ({result.low:.4g} to {result.high:.4g}) {result.unit}")
    for claim, (status, basis) in decided.items():
        print(f"\n{claim}: {status}\n  {basis}")
    print(f"\nrun time {time.time() - started:.0f} s; written to {out_dir}")


if __name__ == "__main__":
    main()
