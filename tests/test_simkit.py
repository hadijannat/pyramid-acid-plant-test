"""The shared pieces of the simulation packages, and the merge of their verdicts with Tier 0."""
import pytest

from pyramid import screening, simkit, verdicts
from pyramid.ledger import LedgerError, load
from pyramid.screening import Result

LEDGER = load()
ROW = Result("flow.demo", "A demonstration", 1.0, 0.5, 2.0, "m", "x", ("dp.width",))


def test_three_way_is_the_tier0_rule():
    assert [simkit.three_way(True, True), simkit.three_way(False, True), simkit.three_way(False, False)] == [
        "pass", "conditional", "fail"]


def test_corners_brackets_the_ledger_value():
    value, low, high = simkit.corners(LEDGER, ("gg.volume",), lambda q: 2 * q["gg.volume"])
    low_volume, high_volume = LEDGER.rng("gg.volume")
    assert (value, low, high) == (2 * LEDGER.q("gg.volume"), 2 * low_volume, 2 * high_volume)


def test_sample_starts_at_the_ledger_values_stays_in_range_and_repeats_with_its_seed():
    ids = ("gg.volume", "chem.kl_surface", "em.granite_conductivity")
    draws = simkit.sample(LEDGER, ids, 200, seed=7)
    assert draws[0] == {i: LEDGER.q(i) for i in ids}
    for draw in draws:
        for i in ids:
            low, high = LEDGER.rng(i)
            assert low <= draw[i] <= high, i
    assert draws == simkit.sample(LEDGER, ids, 200, seed=7)
    assert draws != simkit.sample(LEDGER, ids, 200, seed=8)


def test_a_wide_range_is_drawn_log_uniformly():
    low, high = LEDGER.rng("em.granite_conductivity")
    assert high / low > simkit.LOG_SPAN   # the entry this test relies on spans orders of magnitude
    values = [draw["em.granite_conductivity"] for draw in simkit.sample(LEDGER, ("em.granite_conductivity",), 2000, 1)]
    geometric_middle = (low * high) ** 0.5
    below = sum(value < geometric_middle for value in values[1:]) / (len(values) - 1)
    assert 0.45 < below < 0.55   # half the draws fall below the geometric middle, as a log-uniform draw gives


def test_band_is_the_median_and_the_5th_and_95th_percentiles():
    assert simkit.band(range(101)) == (50.0, 5.0, 95.0)


def test_results_round_trip_with_their_manifest(tmp_path):
    simkit.write_results("flow", LEDGER, {ROW.id: ROW}, {"S08": ("conditional", "A basis.")}, root=tmp_path)
    results, decided, manifest = simkit.read_results("flow", tmp_path)
    assert results == {ROW.id: ROW}
    assert decided == {"S08": ("conditional", "A basis.")}
    assert manifest["ledger"] == LEDGER.digest and manifest["case"] == "flow"
    assert simkit.read_results("chem", tmp_path) is None


@pytest.mark.parametrize("decided, message", [
    ({"S99": ("pass", "A basis.")}, "flow: S99 is not a claim id"),
    ({"S08": ("maybe", "A basis.")}, "flow: S08: 'maybe' is not a verdict word"),
    ({"S08": ("pass", " ")}, "flow: S08: a verdict needs a basis sentence"),
])
def test_write_results_rejects_a_bad_verdict(tmp_path, decided, message):
    with pytest.raises(LedgerError, match=message):
        simkit.write_results("flow", LEDGER, {}, decided, root=tmp_path)


def test_with_no_package_results_the_merge_is_tier0(tmp_path):
    results, decided, source = verdicts.merged(LEDGER, tmp_path)
    assert results == screening.all_results(LEDGER)
    assert decided == screening.verdicts(LEDGER, results)
    assert source["S07"] == "tier0" and source["S08"] == "none"
    assert sorted(set(source.values())) == ["none", "tier0"]


def test_a_package_decides_a_pending_claim_and_adds_its_results(tmp_path):
    simkit.write_results("flow", LEDGER, {ROW.id: ROW}, {"S08": ("conditional", "A basis.")}, root=tmp_path)
    results, decided, source = verdicts.merged(LEDGER, tmp_path)
    assert results[ROW.id] == ROW
    assert decided["S08"] == ("conditional", "A basis.") and source["S08"] == "flow"
    assert decided["S07"] == screening.verdicts(LEDGER, screening.all_results(LEDGER))["S07"]


def test_a_package_may_not_overrule_tier0_or_another_package(tmp_path):
    simkit.write_results("flow", LEDGER, {}, {"S07": ("pass", "A basis.")}, root=tmp_path)
    with pytest.raises(LedgerError, match="flow: S07 is already decided by tier0"):
        verdicts.merged(LEDGER, tmp_path)
    simkit.write_results("flow", LEDGER, {}, {"S08": ("pass", "A basis.")}, root=tmp_path)
    simkit.write_results("chem", LEDGER, {}, {"S08": ("fail", "Another basis.")}, root=tmp_path)
    with pytest.raises(LedgerError, match="chem: S08 is already decided by flow"):
        verdicts.merged(LEDGER, tmp_path)


def test_a_result_id_may_not_be_taken_twice(tmp_path):
    taken = Result("t0.kc_volume", "A clash", 1.0, 1.0, 1.0, "m3", "x", ())
    simkit.write_results("flow", LEDGER, {taken.id: taken}, {}, root=tmp_path)
    with pytest.raises(LedgerError, match="flow: result id t0.kc_volume is already taken"):
        verdicts.merged(LEDGER, tmp_path)


def test_the_summary_counts_every_claim_once_and_its_table_has_a_row_for_each():
    from pyramid import summary
    _, decided, source = verdicts.merged(LEDGER)
    tally = summary.counts(decided)
    assert sum(tally.values()) == len(LEDGER.claims) and list(tally) == list(simkit.STATUSES)
    rows = [line for line in summary.table(LEDGER, decided, source).splitlines() if line[2:3] in ("S", "E")]
    assert [row.split(" | ")[0].lstrip("| ") for row in rows] == list(LEDGER.claims)


def test_the_report_gives_every_claim_one_row_and_embeds_only_files_that_exist(tmp_path):
    import re

    from pyramid import summary
    _, decided, source = verdicts.merged(LEDGER)
    text = summary.report(LEDGER, decided, source)
    assert sorted(re.findall(r"^\| ([SE]\d\d) \|", text, re.M)) == sorted(LEDGER.claims)
    embedded = re.findall(r"\]\((\.\./[^)]+)\)", text)
    assert embedded and all((summary.OUT_DIR / link).exists() for link in embedded)
    for name in ("a.svg", "b.svg"):
        summary.verdict_map(LEDGER, decided, tmp_path / name)
    assert (tmp_path / "a.svg").read_bytes() == (tmp_path / "b.svg").read_bytes() != b""  # no date, no random ids


def test_stale_names_the_packages_generated_from_another_ledger(tmp_path):
    simkit.write_results("flow", LEDGER, {}, {}, root=tmp_path)
    assert verdicts.stale(LEDGER, tmp_path) == []
    manifest = tmp_path / "flow" / "manifest.json"
    manifest.write_text(manifest.read_text().replace(LEDGER.digest, "0" * 40))
    assert verdicts.stale(LEDGER, tmp_path) == ["flow"]
