"""The task plan, the cache and the path from cached runs to gates and verdicts, on made-up spectra."""
import os

import numpy as np
import pytest

from pyramid.em import __main__ as entry
from pyramid.em import cases, mie, runs
from pyramid.ledger import load

LEDGER = load()
Q = LEDGER.q
TABLE = cases.table(LEDGER)
BAND = cases.wavelengths(Q)
SIZE = runs.cells(Q)
ONE, THIRD, HALF = SIZE["benchmark"], SIZE["fine"], SIZE["production"]     # 1 m, 1.667 m, 2.5 m


@pytest.fixture
def cache(tmp_path, monkeypatch):
    monkeypatch.setattr(runs, "CACHE", tmp_path)
    return tmp_path


def test_the_cache_is_refused_once_a_ledger_value_the_runs_read_has_changed(cache):
    import dataclasses
    import re
    from pathlib import Path

    from pyramid.ledger import LedgerError

    source = "".join(f.read_text() for f in Path(runs.__file__).parent.glob("*.py"))
    read = set(re.findall(r'(?:q|rng)\(f?"([a-z]+\.|\{key\})', source))
    assert read - {"{key}"} == {p for p in runs.READS} and "{key}" in read   # {key} is one of the study's chambers, paper.kc and so on
    digest = runs.stamp(LEDGER)
    assert runs.stamp(LEDGER) == digest == (cache / "inputs.sha256").read_text().strip()
    other = dataclasses.replace(LEDGER.quantities["dp.width"], value=LEDGER.q("dp.width") * 1.01)
    assert runs.stamp(dataclasses.replace(LEDGER, quantities={**LEDGER.quantities, "dp.width": other})) == digest
    edited = dataclasses.replace(LEDGER.quantities["em.limestone_eps"], value=LEDGER.q("em.limestone_eps") * 1.01)
    with pytest.raises(LedgerError, match="runs made for other ledger values"):
        runs.stamp(dataclasses.replace(LEDGER, quantities={**LEDGER.quantities, "em.limestone_eps": edited}))


def test_the_cache_is_refused_after_a_change_of_the_solvers_or_without_its_mark(cache, monkeypatch):
    from pyramid.ledger import LedgerError

    digest = runs.stamp(LEDGER)
    monkeypatch.setattr(runs, "RUNS_VERSION", runs.RUNS_VERSION + 1)
    assert runs.inputs_digest(LEDGER) != digest
    with pytest.raises(LedgerError, match="by other solver code"):
        runs.stamp(LEDGER)
    monkeypatch.undo()
    monkeypatch.setattr(runs, "CACHE", cache)
    (cache / "inputs.sha256").unlink()
    assert runs.stamp(LEDGER) == digest                      # an empty cache is marked again
    (cache / "inputs.sha256").unlink()
    (cache / "R1_dda_5.0000_0.npz").write_bytes(b"")
    with pytest.raises(LedgerError, match="no inputs.sha256 beside them"):   # nothing says what these runs were made for
        runs.stamp(LEDGER)


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


def fill(stage, sphere=None, r1=None, truncated=None):
    """Fake every task of a stage. Each argument maps (solver, cell) to a value for the tasks at that cell:
    sphere: the factor on the exact sphere spectrum (default: 1 percent off);
    r1: the King's Chamber ratio in R1 (default 9, three times its control's 3);
    truncated: the summit metric of the truncated apex (default 1.3 times the pointed one's 1)."""
    for task in runs.plan(LEDGER, stage):
        name, at = task[0], (task[1], task[2])
        if name == "B0":
            factor = (sphere or {}).get(at, 0.99 if task[1] == "dda" else 1.01)
            fake(task, lambda w, factor=factor: exact(w) * factor)
        elif name == "R3":
            fake(task, lambda w: 12e4 * np.exp(-((w - 255.0) / 60) ** 2))
        else:
            kings = (r1 or {}).get(at, 9.0) if name == "R1" else 3.0 if name == "C0.R1" else 0.2 if "V4" in name else 1.0
            fake(task, study, kings=kings, summit=(truncated or {}).get(at, 1.3) if name == "V3.truncated.ground" else 1.0)


def test_the_plan_keeps_ground_out_of_the_dipole_solver_and_orders_the_stages():
    gates, variants = runs.plan(LEDGER, "gates"), runs.plan(LEDGER, "variants")
    assert all(not TABLE[name].ground for name, solver, _, _ in gates + variants if solver == "dda")
    assert {t[0] for t in gates} == {"B0", "R1", "R2", "R3"}
    assert ("R1", "fdtd", 2.5, 2) in gates and ("R3", "fdtd", 2.5, 0) in gates and ("B0", "dda", 5 / 3, 8) in gates
    assert ("B0", "fdtd", 1.0, 0) in gates                      # the sphere at the time-domain solver's deciding cell
    names = {t[0] for t in variants}
    assert len([n for n in names if n.startswith("V1.")]) == 30 and {"C0.R1", "C0.R3", "V2.R3", "V3.pointed.up"} <= names
    fine = {t[0] for t in variants if t[2] < runs.FLUX_LIMIT}
    assert fine == {"R1", "C0.R1", "R3", "V3.truncated.ground", "V3.pointed.ground", "V4.sig6.7e-04", "C0.V4.sig6.7e-04",
                    "V4.sig3.3e-03", "C0.V4.sig3.3e-03"}
    assert [t for t in variants if t[0] == "V4.sig6.7e-04" and t[2] == 2.5] == [("V4.sig6.7e-04", "fdtd", 2.5, 0)]


def test_the_certified_stage_is_the_deciding_runs_at_the_cells_where_the_sphere_passes():
    certified = runs.plan(LEDGER, "certified")
    assert {t[:3] for t in certified if t[1] == "dda"} == {("R1", "dda", THIRD), ("C0.R1", "dda", THIRD)}
    v4 = {"V4.sig6.7e-04", "V4.sig1.5e-03", "V4.sig3.3e-03"}
    assert {t[0] for t in certified if t[1:3] == ("fdtd", ONE)} == {
        "R1", "C0.R1", "V3.truncated.ground", "V3.pointed.ground", "V4.eps5.sig6.7e-04", "V4.eps9.sig6.7e-04"} | v4 | {
        f"C0.{name}" for name in v4}
    assert {t[:3] for t in certified if t[2] not in (ONE,) and t[1] == "fdtd"} == {("B0", "fdtd", THIRD)}   # the sphere, compared
    assert len(certified) == 2 * 9 + 4 * 3 + 8 + 3 and not set(certified) & set(runs.plan(LEDGER, "gates") + runs.plan(LEDGER, "variants"))


def test_a_sphere_outside_the_limit_at_a_deciding_cell_stops_everything(cache):
    for stage in ("gates", "variants", "certified"):             # every run is there: the sphere alone stops the verdicts
        fill(stage, sphere={("fdtd", ONE): 1.03})
    summary = runs.evaluate(LEDGER)
    assert [g["passed"] for g in summary["gates"]] == [False] * 6
    assert "fdtd at 1 m: worst +3.00%" in summary["gates"][0]["numbers"]
    assert "not judged" in summary["gates"][1]["numbers"] and "for information" in summary["gates"][1]["numbers"]
    assert summary["verdicts"] == {} and "undecided" in summary["notes"][0]
    assert summary["results"]["b0_deviation_fdtd_1"].value == pytest.approx(0.03)
    assert summary["results"]["r1_peak1_wavelength_dda"].value == pytest.approx(230.0, abs=1.0)   # still reported
    assert not any(key.startswith(("e19", "e20")) for key in summary["results"])                 # no variant is read


def test_a_sphere_within_the_limit_only_at_a_finer_cell_than_the_runs_writes_no_verdict(cache):
    # What happened: the sphere is outside 2 percent at 2.5 m and inside at each solver's finest cell, and the
    # runs behind the two claims are at 2.5 m and 1.667 m. This is also the state before --certified has run.
    off = {("dda", HALF): 1.028, ("fdtd", HALF): 1.03}
    fill("gates", sphere=off)
    fill("variants")
    summary = runs.evaluate(LEDGER)
    benchmark = summary["gates"][0]
    judged = {(c["solver"], c["cell_m"]): c["passed"] for c in benchmark["cells"]}
    assert judged[("fdtd", HALF)] is False and judged[("dda", HALF)] is False and judged[("fdtd", ONE)] and judged[("dda", THIRD)]
    assert "fdtd at 2.5 m: worst +3.00%" in benchmark["numbers"] and "decide nothing" in benchmark["numbers"]
    assert "fdtd at 1.67 m: not run" in benchmark["numbers"]
    assert [g["passed"] for g in summary["gates"]] == [True] * 6          # judged where the deciding runs will be
    assert summary["verdicts"] == {}
    e19, e20 = summary["notes"]
    assert e19.startswith("E19 is undecided") and "R1 fdtd 1 m (3 of 3 parts)" in e19 and "C0.R1 dda 1.67 m (9 of 9 parts)" in e19
    assert "V4.eps9.sig6.7e-04 fdtd 1 m (1 of 1 parts)" in e19 and "B0 fdtd 1.67 m (3 of 3 parts)" in e19 and "--certified" in e19
    assert e20.startswith("E20 is undecided") and "V3.truncated.ground fdtd 1 m (3 of 3 parts)" in e20 and "R1" not in e20
    shown = summary["results"]["e19_r1_over_control_fdtd_2p5"]            # the coarser cells' numbers, with what they are
    assert shown.value == pytest.approx(3.0) and "for information, decides nothing" in shown.label
    assert "resolution check, decides nothing" in summary["results"]["e20_summit_ratio_fdtd_1p67"].label
    fill("certified")                                            # the deciding runs alone are not enough: the sphere
    for part in range(3):                                        # has to be judged at the compared cell as well
        runs.path(("B0", "fdtd", THIRD, part)).unlink()
    summary = runs.evaluate(LEDGER)
    assert summary["verdicts"] == {} and all("B0 fdtd 1.67 m (3 of 3 parts)" in note and "R1" not in note for note in summary["notes"])


def test_verdicts_rest_on_the_runs_at_the_certified_cells(cache):
    off = {("dda", HALF): 1.028, ("fdtd", HALF): 1.03, ("fdtd", THIRD): 1.025}
    for stage in ("gates", "variants", "certified"):             # 2.5 m in the time domain is two cells away: there R1
        fill(stage, sphere=off, r1={("fdtd", HALF): 4.0})        # is "not twice the control", and that must not matter
    summary = runs.evaluate(LEDGER)
    assert [g["passed"] for g in summary["gates"]] == [True] * 6 and summary["notes"] == []
    status, basis = summary["verdicts"]["E19"]
    assert status == "fail" and "As modelled (met)" in basis and "Under realism (fail)" in basis
    assert "in the time-domain solver at a 1 m cell; 9.00 against 3.00 in its control cube (3.00 times) in the dipole solver at a 1.67 m cell" in basis
    assert "decides nothing: 9.00 against 3.00 in its control cube (3.00 times) in the time-domain solver at a 1.67 m cell" in basis
    assert "4.00 against" not in basis and "(permittivity 9)" in basis
    assert "Not varied" in basis and "permittivity of 5 (its range is 4 to 6)" in basis and "skin depth of 24 to 32 m" in basis
    status, basis = summary["verdicts"]["E20"]
    assert status == "fail" and "(1.30 times) in the time-domain solver at a 1 m cell" in basis
    assert "(1.30 times; 1.00 for the study's apex) in the time-domain solver at a 1.67 m cell" in basis
    results = summary["results"]
    assert results["e19_r1_over_control_fdtd_1"].value == pytest.approx(3.0) and "(decides)" in results["e19_r1_over_control_fdtd_1"].label
    assert results["e19_r1_over_control_dda_1p67"].value == pytest.approx(3.0)
    assert results["e19_r1_over_control_fdtd_2p5"].value == pytest.approx(4 / 3)
    assert results["e19_v4_eps7_6p7em04_fdtd_1"].value == pytest.approx(0.2) and "e19_v4_permittivity_9_6p7em04_fdtd_1" in results
    assert results["r1_peak1_wavelength_dda_1p67"].value == pytest.approx(230.0, abs=1.0)
    assert {r.id for r in results.values()} == {f"em.{key}" for key in results}
    for result in results.values():                             # every number names ledger entries that exist
        assert result.inputs and all(i in LEDGER.quantities for i in result.inputs), result.id
    assert set(results["e20_summit_ratio_fdtd_1"].inputs) == set(runs.E20_SUMMIT)


def test_the_next_coarser_cell_on_the_other_side_makes_a_claim_conditional(cache):
    for stage in ("gates", "variants"):
        fill(stage, r1={("dda", HALF): 5.0}, truncated={("fdtd", THIRD): 1.3, ("fdtd", HALF): 1.3})
    fill("certified", truncated={("fdtd", ONE): 2.4})
    verdicts = runs.evaluate(LEDGER)["verdicts"]
    assert verdicts["E20"][0] == "conditional" and "different sides" in verdicts["E20"][1]     # 2.4 at 1 m, 1.3 at 1.667 m
    assert "As modelled (conditional)" in verdicts["E19"][1]     # the dipole solver's 2.5 m cell says 5 against 3


def test_a_killed_task_goes_on_from_its_last_state_and_ends_as_an_uninterrupted_one(cache, monkeypatch, tmp_path_factory):
    tasks = (("B0", "dda", 20.0, 8), ("V1.R1.eps5.sig3.3e-03", "fdtd", 30.0, 0))
    for task in tasks:
        done, finished, _ = runs.work((task, np.inf))
        assert finished and done == task and runs.path(task).exists()
    whole = {task: dict(np.load(runs.path(task))) for task in tasks}
    assert whole[tasks[0]]["wavelengths"].tolist() == BAND[-9:].tolist() and np.all(whole[tasks[0]]["extinction"] > 0)
    lossy = runs.collect(LEDGER, tasks[1][0], "fdtd", 30.0)
    assert lossy["extinction"].shape == BAND.shape and np.all(lossy["mean.kings"] < 1.0)   # the rock shields the chamber
    assert runs.work((tasks[0], np.inf))[1:] == (True, 0.0)      # a task that is cached is not run again

    monkeypatch.setattr(runs, "CACHE", tmp_path_factory.mktemp("killed"))
    monkeypatch.setattr(runs, "CHECKPOINT", 0.0)                 # the time-domain run leaves a state at every check
    real, states = runs.keep, []

    def dying(path, write):                                      # the process dies just after its second state
        real(path, write)
        states.append(path)
        if len(states) == 2:
            raise KeyboardInterrupt

    for task in tasks:
        states.clear()
        monkeypatch.setattr(runs, "keep", dying)
        with pytest.raises(KeyboardInterrupt):
            runs.work((task, np.inf))
        target = runs.path(task)
        assert not target.exists() and target.with_suffix(".state.npz").exists() and target.with_suffix(".time.npy").exists()
        assert runs.work((task, 0.0)) == (task, False, 0.0)      # past its deadline a task does not start
        monkeypatch.setattr(runs, "keep", real)
        assert runs.work((task, np.inf))[1]
        again = dict(np.load(target))
        assert set(again) == set(whole[task])
        assert all(np.array_equal(again[key], whole[task][key]) for key in again if key != "seconds"), task
        assert [f.name for f in target.parent.iterdir() if f.name.startswith(target.stem)] == [target.name]   # no state left


def test_certified_runs_only_what_is_missing_and_says_when_all_is_cached(cache, monkeypatch, capsys):
    runs.stamp(LEDGER)   # as the first call on an empty cache marks it
    plan = runs.plan(LEDGER, "certified")
    for task in plan[:5]:
        fake(task, study)
    ran, limit = [], [3]

    def worker(job):                                             # a stand-in for runs.work: the first few finish
        task, _ = job
        ran.append(task)
        if len(ran) <= limit[0]:
            fake(task, study)
        return task, len(ran) <= limit[0], 0.0

    monkeypatch.setattr(runs, "work", worker)
    monkeypatch.setattr(entry, "write_results", lambda *a, **k: pytest.fail("--certified writes no summary"))
    monkeypatch.delenv("MallocLargeCache", raising=False)
    assert entry.main(["--certified", "--workers", "1"]) == 1    # interrupted: 3 of the 36 missing ones are done
    assert os.environ["MallocLargeCache"] == "0"                 # what the workers inherit: no 5 GB each at a 1 m cell
    assert set(ran) == set(plan[5:]) and len(ran) == len(plan) - 5
    out = capsys.readouterr().out
    assert f"[1/{len(plan) - 5}] done" in out and f"{len(plan) - 8} of {len(plan)} tasks are not cached" in out
    assert ran[0][2] == ONE                                      # the longest runs start first
    done, limit[0] = set(ran[:3]) | set(plan[:5]), 10**6
    ran.clear()
    assert entry.main(["--certified", "--workers", "1"]) == 0    # called again: the rest, and only the rest
    assert set(ran) == set(plan) - done and all(runs.path(task).exists() for task in plan)
    ran.clear()
    assert entry.main(["--certified", "--workers", "1"]) == 0 and ran == []
    assert "0 of 41 tasks are not cached" in capsys.readouterr().out


def test_the_plain_call_evaluates_and_never_starts_the_certified_runs(cache, monkeypatch, capsys):
    runs.stamp(LEDGER)   # as the first call on an empty cache marks it
    fill("gates")
    fill("variants")
    written = {}
    monkeypatch.setattr(runs, "work", lambda job: pytest.fail(f"{job[0]} was started"))
    monkeypatch.setattr(entry, "write_results", lambda *a, **k: written.update(called=True))
    monkeypatch.setattr(entry, "figures", lambda *a: None)
    assert entry.main([]) == 1 and written == {}             # a summary with no verdict would replace the committed one
    out = capsys.readouterr().out
    assert "E19 is undecided" in out and "E20 is undecided" in out and "PASS benchmark" in out
    assert "results/em is left as it is" in out
