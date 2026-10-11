"""Geometric premises: the shaft-exit construction against its closed form, then each rule through its statuses."""
import dataclasses
import math

import pytest

from pyramid import ledger, premises, screening, simkit, viewer_data


@pytest.fixture(scope="module")
def led() -> ledger.Ledger:
    return ledger.load()


def altered(led, changes: dict[str, tuple[float, float, float]]):
    """The verdicts after replacing (value, low, high) of some ledger quantities."""
    quantities = dict(led.quantities)
    for id, (value, low, high) in changes.items():
        quantities[id] = dataclasses.replace(quantities[id], value=value, low=low, high=high)
    return premises.verdicts(dataclasses.replace(led, quantities=quantities))


def shaft(side, half, apex, mouth, wall, level, angle, flat=0.0):
    """Inputs of shaft_exit for a made-up pyramid: base side 2 half, apex height, axis at the mouth, runs, slope."""
    return {"pyr.base_side": 2 * half, "pyr.height_original": apex, "kc.floor.z": mouth, "kcs.mouth_height": 0.0,
            f"kcs.{side}.height": 0.0, f"kcs.{side}.angle": angle, "kcs.horizontal_length": level,
            f"kc.{side}_wall.y": wall, "kcs.level_end_length": flat}


# --- Benchmarks ------------------------------------------------------------------------------


def test_a_45_degree_shaft_from_the_centre_meets_a_45_degree_face_half_way_up():
    # z = y on the shaft and z = 100 - y on the face: they meet at y = z = 50, after 50 sqrt(2) along the axis.
    level, length = premises.shaft_exit(shaft("north", 100.0, 100.0, 0.0, 0.0, 0.0, 45.0), "north")
    assert level == pytest.approx(50.0, abs=1e-9)
    assert length == pytest.approx(50.0 * math.sqrt(2), abs=1e-9)


@pytest.mark.parametrize(("side", "wall"), [("north", -8.4), ("south", -13.6)])
def test_shaft_exit_matches_the_line_and_plane_solved_for_the_horizontal_distance(side, wall):
    # Independent closed form, solved for the distance d from the centre instead of the length along the axis:
    # shaft z = z0 + (d - d0) tan(slope) from the end of its level run at d0; face z = apex (1 - d / half).
    half, apex, mouth, level, angle = 115.0, 147.0, 44.0, 1.5, 33.0
    way = 1.0 if side == "north" else -1.0
    start = way * wall + level
    tan = math.tan(math.radians(angle))
    distance = (apex - mouth + start * tan) / (tan + apex / half)
    expected_level = apex * (1 - distance / half)
    expected_length = level + (distance - start) / math.cos(math.radians(angle))
    got_level, got_length = premises.shaft_exit(shaft(side, half, apex, mouth, wall, level, angle), side)
    assert got_level == pytest.approx(expected_level, abs=1e-9)  # tolerance: rounding only, both are closed forms
    assert got_length == pytest.approx(expected_length, abs=1e-9)


def test_a_level_last_stretch_still_ends_on_the_face_and_lowers_the_exit():
    half, apex, mouth, level, angle, flat = 115.0, 147.0, 44.0, 1.5, 33.0, 3.0
    q = shaft("north", half, apex, mouth, 0.0, level, angle, flat)
    inclined, _ = premises.shaft_exit(q, "north")
    exit_level, length = premises.shaft_exit(q, "north", level_end=True)
    rest = length - level - flat
    end = level + rest * math.cos(math.radians(angle)) + flat  # distance of the outer end from the centre
    assert apex * (1 - end / half) == pytest.approx(exit_level, abs=1e-9)  # the end lies on the casing plane
    # The incline is shorter by what the level run covers: flat / (cos + (half / apex) sin) along the axis.
    slope = math.radians(angle)
    drop = flat * math.sin(slope) / (math.cos(slope) + half / apex * math.sin(slope))
    assert inclined - exit_level == pytest.approx(drop, abs=1e-9)


def test_shaft_lengths_agree_with_the_lengths_measured_in_1837(led):
    # 01 check 6: the construction is "consistent with Vyse to about 1 m". Vyse's lengths are in the ledger.
    q = {i: led.q(i) for side in ("north", "south") for i in premises._exit_inputs(side, False)}
    for side in ("north", "south"):
        assert premises.shaft_exit(q, side)[1] == pytest.approx(led.q(f"kcs.{side}.length"), abs=1.0)


@pytest.mark.parametrize(("side", "angle", "level", "sloping", "exit_level"), [
    ("north", 31.55, 1.5, 69.3, 80.2),  # 01 check 6: 68.3 to 69.3 m in the north, 51.9 m in the south,
    ("north", 32.6, 2.6, 68.3, 80.8),   # exits at Z 80.2 to 80.8 m, from mouths at Z 43.95 m
    ("south", 45.23, 1.5, 51.9, 80.8),
])
def test_shaft_exit_reproduces_the_figures_of_01_check_6(led, side, angle, level, sloping, exit_level):
    q = shaft(side, led.q("pyr.base_side") / 2, led.q("pyr.height_original"), 43.95, led.q(f"kc.{side}_wall.y"),
              level, angle)
    got_level, length = premises.shaft_exit(q, side)
    assert length - level == pytest.approx(sloping, abs=0.1)  # 01 prints one decimal
    assert got_level == pytest.approx(exit_level, abs=0.1)


# --- Results ---------------------------------------------------------------------------------


def test_results_are_named_for_the_package_and_read_only_the_ledger(led):
    results = premises.results(led)
    assert len(results) == 11
    for id, result in results.items():
        assert id == result.id and id.startswith("premises.")
        assert result.low <= result.value <= result.high
        assert all(i in led.quantities for i in result.inputs)
    assert not set(results) & set(screening.all_results(led))


def test_reads_lists_what_each_rule_reads_so_the_viewer_can_show_its_numbers(led):
    results = premises.results(led)
    for claim, rule in premises.RULES.items():
        quoted, asked = [], []

        class Results(dict):  # records which results the rule quotes
            def __getitem__(self, key):
                quoted.append(key)
                return super().__getitem__(key)

        class Recording(ledger.Ledger):  # records which quantities the rule reads directly
            def _quantity(self, id):
                asked.append(id)
                return super()._quantity(id)

        rule(Recording(led.quantities, led.claims, led.digest), Results(results))
        read = {i for id in quoted for i in results[id].inputs} | set(asked)
        assert quoted and read == set(premises.READS[claim]), claim
    # Once depends_on holds those ids, every premise carries at least one number in the viewer's payload.
    claims = {id: dataclasses.replace(claim, depends_on=claim.depends_on + premises.READS.get(id, ()))
              for id, claim in led.claims.items()}
    payload = viewer_data.claims_payload(dataclasses.replace(led, claims=claims), results, premises.verdicts(led))
    shown = {claim["id"]: claim["numbers"] for claim in payload["claims"]}
    assert all(shown[claim] for claim in premises.RULES)
    assert len(shown["E11"]) == 4 and len(shown["S15"]) == 3 and len(shown["E25"]) == 1


def test_the_numbers_the_bases_quote(led):
    r = premises.results(led)
    assert r["premises.kcs_north_exit_z"].value == pytest.approx(80.27, abs=0.01)
    assert r["premises.kcs_south_exit_z"].value == pytest.approx(80.85, abs=0.01)
    assert r["premises.kcs_north_exit_z_level"].value == pytest.approx(79.01, abs=0.01)
    assert r["premises.kcs_south_exit_z_level"].value == pytest.approx(79.14, abs=0.01)
    # 01 check 1: four grooves 0.105 m wide at 0.2 in residual depth = 0.002 m2; at the full 2.8 in, 0.030 m2.
    area = r["premises.groove_connected_area"]
    assert (area.low, area.high) == (0.0, pytest.approx(4 * 0.105 * 0.0051))
    assert r["premises.groove_full_area"].value == pytest.approx(0.030, abs=0.0005)
    # 01 claim 2: 1.5 cm of clearance over a 1.2 m slab, of the order of 0.02 m2.
    assert r["premises.slab_clearance_area"].value == pytest.approx(0.015 * 1.21)
    assert r["premises.sp_length_between_ends"].value == pytest.approx(16.41, abs=0.005)
    assert r["premises.void_length_ratio"].value == pytest.approx(30 / 46.7, abs=0.001)
    above = r["premises.void_centre_above_roof"]
    assert (above.low, above.high) == (pytest.approx(61.19 - 51.55), pytest.approx(71.19 - 51.35))


# --- Verdicts --------------------------------------------------------------------------------

# Each case: (claim, status on the real ledger, numbers its basis must print).
VERDICTS = [
    ("E11", "conditional", ("80.3 m in the north (78.8 to 81.3 m", "80.9 m in the south (79.5 to 81.7 m)",
                            "79.0 m (77.6 to 80.0 m) and 79.1 m (77.8 to 79.9 m)", "4 of the 4", "0 of the 4")),
    ("E12", "conditional", ("between 0.0 and 5.1 mm", "0.0021 m2 at most", "0.030 m2", "3 pairs of slots")),
    ("S15", "conditional", ("0.0021 m2 at most", "about 0.002 m2", "0.018 m2", "8 times")),
    ("E15", "pass", ("30.8 m below the pavement", "16.41 m long", "16.41 m (16.28 to 16.54 m")),
    ("E25", "pass", ("127 mm (5.0 in)", "76 to 127 mm", "no source was found for 3 in")),
    ("E32", "pass", ("at least 30 m long", "0.64 of the Gallery's 46.7 m (0.64 to 0.86", "14.7 m above",
                     "(9.6 to 19.8 m)", "factor of 10", "factor of two")),
]


@pytest.mark.parametrize(("claim", "status", "numbers"), VERDICTS)
def test_verdicts_on_the_ledger_as_it_stands(led, claim, status, numbers):
    got, basis = premises.verdicts(led)[claim]
    assert got == status, basis
    for text in numbers:
        assert text in basis, basis
    assert "—" not in basis and "–" not in basis


def test_the_package_decides_its_six_claims_and_none_that_tier_0_decides(led):
    assert set(premises.verdicts(led)) == {"E11", "E12", "E15", "E25", "E32", "S15"}
    assert not set(premises.RULES) & set(screening.RULES)
    assert all(status in ("pass", "fail", "conditional") for status, _ in premises.verdicts(led).values())


def test_e11_fails_without_a_surveyed_level_end_or_with_exits_off_the_band_and_cannot_pass(led):
    status, basis = altered(led, {"kcs.level_end_length": (0.0, 0.0, 0.0)})["E11"]
    assert status == "fail" and "No survey gives either" in basis
    # A northern shaft at 40 degrees would come out far above Z = 81 m in both readings.
    status, basis = altered(led, {"kcs.north.angle": (40.0, 40.0, 40.0)})["E11"]
    assert status == "fail" and "cannot reach it" in basis and "2 of the 4" in basis
    # With every slope and level run known exactly the exits all lie inside the band, and the claim still does
    # not pass: one survey party's level end at one outlet, contradicted in 1881, is not a survey of both.
    exact = {i: (led.q(i),) * 3 for side in ("north", "south") for i in premises._exit_inputs(side, True)}
    status, basis = altered(led, exact)["E11"]
    assert status == "conditional" and "4 of the 4 over the whole" in basis


def test_the_groove_claims_turn_on_the_residual_depth_at_the_door_top(led):
    for claim in ("E12", "S15"):
        status, basis = altered(led, {"ante.groove_residual_depth": (0.0, 0.0, 0.0)})[claim]
        assert status == "fail" and "blind in every reading" in basis, basis
        status, basis = altered(led, {"ante.groove_residual_depth": (0.0051, 0.0051, 0.0051)})[claim]
        assert status == "pass" and "in every reading" in basis, basis
        status, basis = altered(led, {})[claim]
        assert status == "conditional" and "only in the reading" in basis, basis
    # With blind grooves the clearance sentence does not divide by nothing.
    assert "open where they are not" in altered(led, {"ante.groove_residual_depth": (0.0, 0.0, 0.0)})["S15"][1]


def test_e15_needs_the_two_figures_for_the_passage_to_agree(led):
    assert altered(led, {})["E15"][0] == "pass"
    status, basis = altered(led, {"sp.length": (20.0, 20.0, 20.0)})["E15"]
    assert status == "conditional" and "20.00 m long" in basis and "disagree" in basis


def test_e25_compares_the_recorded_stone_with_the_claimed_3_to_5_inches(led):
    assert altered(led, {})["E25"][0] == "pass"
    # A foot of stone is not about 3 to 5 in.
    status, basis = altered(led, {"qcs.stone_left": (0.30, 0.30, 0.30)})["E25"]
    assert status == "fail" and "300 mm (11.8 in)" in basis and "no part of the range" in basis
    # A range that reaches down to an open mouth, or up to twice the claim, holds at one end only.
    assert altered(led, {"qcs.stone_left": (0.127, 0.0, 0.127)})["E25"][0] == "conditional"
    assert altered(led, {"qcs.stone_left": (0.127, 0.127, 0.25)})["E25"][0] == "conditional"
    # "About" is half an inch: 5.4 in passes, 5.6 in does not.
    assert altered(led, {"qcs.stone_left": (5.4 * 0.0254,) * 3})["E25"][0] == "pass"
    assert altered(led, {"qcs.stone_left": (5.6 * 0.0254,) * 3})["E25"][0] == "fail"


def test_e32_needs_the_void_above_the_gallery_over_it_and_of_comparable_length(led):
    assert altered(led, {})["E32"][0] == "pass"
    assert altered(led, {"bv.centre.z": (40.0, 40.0, 40.0)})["E32"][0] == "fail"  # below the Gallery roof
    assert altered(led, {"bv.centre.z": (66.19, 45.0, 71.19)})["E32"][0] == "conditional"
    assert altered(led, {"bv.south_end.y": (60.0, 60.0, 60.0)})["E32"][0] == "fail"  # north of the Gallery
    status, basis = altered(led, {"bv.length": (3.0, 3.0, 3.0)})["E32"]  # a tenth of the least length published
    assert status == "fail" and "0.06 of the Gallery's" in basis and "factor of two" not in basis
    # The assumed section and volume decide nothing: a section a hundred times smaller leaves the verdict alone.
    shrunk = {"bv.section_area": (0.136,) * 3, "bv.volume": (4.0, 4.0, 5.0)}
    assert altered(led, shrunk)["E32"] == altered(led, {})["E32"]


def test_pass_needs_the_unfavourable_end_of_every_range(led):
    # E32 passes on the ledger; widening the void's level down to the Gallery roof must cost it the pass.
    assert altered(led, {"bv.centre.z": (66.19, 51.0, 71.19)})["E32"][0] == "conditional"


def test_main_writes_what_the_merge_reads(tmp_path, led):
    premises.main(root=tmp_path)
    results, verdicts, manifest = simkit.read_results("premises", tmp_path)
    assert results == premises.results(led) and verdicts == premises.verdicts(led)
    assert manifest["ledger"] == led.digest and len(manifest["assumptions"]) == len(premises.ASSUMPTIONS)
    png = (tmp_path / "premises" / "figures" / "kcs_exits.png").read_bytes()
    assert png.startswith(b"\x89PNG") and b"tIME" not in png and b"Software" not in png  # no timestamp in the file
