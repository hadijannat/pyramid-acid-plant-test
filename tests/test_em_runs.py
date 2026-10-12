"""The task plan, the cache and the path from cached runs to gates and verdicts, on made-up spectra."""
import numpy as np
import pytest

from pyramid.em import cases, mie, runs
from pyramid.ledger import load

LEDGER = load()
Q = LEDGER.q
TABLE = cases.table(LEDGER)
BAND = cases.wavelengths(Q)


@pytest.fixture
def cache(tmp_path, monkeypatch):
    monkeypatch.setattr(runs, "CACHE", tmp_path)
    return tmp_path


def study(wavelengths):
    """A spectrum with the study's two free-space maxima."""
    return 9e4 * np.exp(-((wavelengths - 333.0) / 45) ** 2) + 13e4 * np.exp(-((wavelengths - 230.0) / 22) ** 2)


def fake(task, spectrum, kings=1.0, summit=1.0):
    """Write a cache file as a solver would, with a given spectrum and flat region metrics."""
    name, solver, cell, part = task
    case, wavelengths = TABLE[name], BAND
    if solver == "dda":
        wavelengths = np.array_split(BAND, runs.CHUNKS)[part]
    flat = np.ones(len(wavelengths))
    out = {"wavelengths": wavelengths, "extinction": spectrum(wavelengths), "scattering": spectrum(wavelengths),
           "absorption": 0 * flat, "section": np.zeros((len(wavelengths), 2, 2)), "section_extent": np.zeros(4),
           "seconds": np.array(1.0)}
    for region, value in (("kings", kings), ("queens", 1.0), ("summit", summit)):
        out[f"mean.{region}"], out[f"max.{region}"] = value * flat, 2 * value * flat
    if solver == "fdtd":
        matched = (BAND.min(), np.sqrt(BAND.min() * BAND.max()), BAND.max())[part]
        out["sigma"] = np.array(case.sigma if case.eps_imag is None else cases.conductivity(case.eps_imag, matched, Q))
    np.savez(runs.path(task), **out)


def exact(wavelengths):
    return mie.cross_sections(Q("emx.sphere_radius"), 5 + 0.1j, wavelengths)[0]


def fill_gates(b0_fdtd=1.01):
    for task in runs.plan(LEDGER, "gates"):
        name, solver = task[0], task[1]
        if name == "B0":
            fake(task, lambda w: exact(w) * (b0_fdtd if solver == "fdtd" else 0.99))
        elif name == "R3":
            fake(task, lambda w: 12e4 * np.exp(-((w - 255.0) / 60) ** 2))
        else:
            fake(task, study, kings=9.0 if name == "R1" else 1.0)


def test_the_plan_keeps_ground_out_of_the_dipole_solver_and_orders_the_stages():
    gates, variants = runs.plan(LEDGER, "gates"), runs.plan(LEDGER, "variants")
    assert all(not TABLE[name].ground for name, solver, _, _ in gates + variants if solver == "dda")
    assert {t[0] for t in gates} == {"B0", "R1", "R2", "R3"}
    assert ("R1", "fdtd", 2.5, 2) in gates and ("R3", "fdtd", 2.5, 0) in gates and ("B0", "dda", 5 / 3, 8) in gates
    assert ("B0", "fdtd", 1.0, 0) in gates                      # the sphere's sharp lines need the finest cell
    names = {t[0] for t in variants}
    assert len([n for n in names if n.startswith("V1.")]) == 30 and {"C0.R1", "C0.R3", "V2.R3", "V3.pointed.up"} <= names
    fine = {t[0] for t in variants if t[2] < runs.FLUX_LIMIT}
    assert fine == {"R1", "C0.R1", "R3", "V3.truncated.ground", "V3.pointed.ground", "V4.sig6.7e-04", "C0.V4.sig6.7e-04",
                    "V4.sig3.3e-03", "C0.V4.sig3.3e-03"}
    assert [t for t in variants if t[0] == "V4.sig6.7e-04" and t[2] == 2.5] == [("V4.sig6.7e-04", "fdtd", 2.5, 0)]


def test_a_failed_benchmark_stops_everything(cache):
    fill_gates(b0_fdtd=1.03)
    summary = runs.evaluate(LEDGER)
    assert [g["passed"] for g in summary["gates"]] == [False] * 6
    assert "fdtd at 1 m: worst +3.00%" in summary["gates"][0]["numbers"]
    assert "not judged" in summary["gates"][1]["numbers"] and "for information" in summary["gates"][1]["numbers"]
    assert summary["verdicts"] == {} and "undecided" in summary["notes"][0]
    assert summary["results"]["b0_deviation_fdtd"].value == pytest.approx(0.03)
    assert summary["results"]["r1_peak1_wavelength_dda"].value == pytest.approx(230.0, abs=1.0)   # still reported


def test_gates_pass_and_the_claims_wait_for_their_runs(cache):
    fill_gates()
    summary = runs.evaluate(LEDGER)
    assert [g["passed"] for g in summary["gates"]] == [True] * 6
    assert summary["verdicts"] == {} and len(summary["notes"]) == 2      # nothing decided without the variants


def test_verdicts_come_from_the_cached_variants(cache):
    fill_gates()
    for task in runs.plan(LEDGER, "variants"):
        name = task[0]
        kings = 9.0 if name == "R1" else 3.0 if name == "C0.R1" else 0.2 if "V4" in name else 1.0
        fake(task, study, kings=kings, summit=1.3 if name == "V3.truncated.ground" else 1.0)
    summary = runs.evaluate(LEDGER)
    status, basis = summary["verdicts"]["E19"]
    assert status == "fail" and "As modelled (pass)" in basis and "Under realism (fail)" in basis
    assert summary["verdicts"]["E20"][0] == "fail" and "1.30 times" in summary["verdicts"]["E20"][1]
    assert summary["results"]["e19_r1_over_control_2p5"].value == pytest.approx(3.0)
    assert {r.id for r in summary["results"].values()} == {f"em.{key}" for key in summary["results"]}
    for result in summary["results"].values():                  # every number names ledger entries that exist
        assert result.inputs and all(i in LEDGER.quantities for i in result.inputs), result.id
    assert set(summary["results"]["e20_summit_ratio_2p5"].inputs) == set(runs.E20_SUMMIT)


def test_one_task_of_each_solver_runs_to_its_cache_file(cache):
    for task in (("B0", "dda", 20.0, 8), ("V1.R1.eps5.sig3.3e-03", "fdtd", 20.0, 0)):
        done, finished, _ = runs.work((task, np.inf))
        assert finished and done == task and runs.path(task).exists()
    sphere = dict(np.load(runs.path(("B0", "dda", 20.0, 8))))
    assert sphere["wavelengths"].tolist() == BAND[-9:].tolist() and np.all(sphere["extinction"] > 0)
    lossy = runs.collect(LEDGER, "V1.R1.eps5.sig3.3e-03", "fdtd", 20.0)
    assert lossy["extinction"].shape == BAND.shape and np.all(lossy["mean.kings"] < 1.0)   # the rock shields the chamber
