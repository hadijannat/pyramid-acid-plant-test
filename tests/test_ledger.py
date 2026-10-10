"""Tests for the ledger loader and for the ledger files themselves."""
import functools
import hashlib
import math
import re
from pathlib import Path

import pytest

from pyramid import REPO_ROOT, ledger

# A two-quantity, one-claim ledger written into pytest's tmp_path by write_ledger().
PARAMS = """\
- {id: gg.volume, value: 573.0, unit: "m3", low: 527.2, high: 618.8, source: "research/01-geometry.md table F", verified: false, note: "computed"}
- {id: site.base_elevation_asl, value: 60, unit: "m", source: "research/02-hydraulics.md section 2.2", verified: true}
"""
CLAIMS = """\
- id: S12
  statement: "Four pump activations fill the Grand Gallery."
  subsystem: hydraulic
  timestamp: "F 00:42:41-00:43:10"
  tier: 0
  piece: 3
  criterion: "Pass if the stroke count is within 25 percent of 4."
  status: pending
  depends_on: [gg.volume]
  spaces: [grand_gallery]
"""


def write_ledger(root: Path, params: str = PARAMS, claims: str = CLAIMS) -> Path:
    (root / "parameters.yaml").write_text(params)
    (root / "claims.yaml").write_text(claims)
    return root


def test_repo_root_is_the_folder_that_holds_pyproject():
    assert (REPO_ROOT / "pyproject.toml").is_file()
    assert (REPO_ROOT / "research").is_dir()


def test_load_reads_quantities_with_ranges_and_defaults(tmp_path):
    led = ledger.load(write_ledger(tmp_path))
    assert led.q("gg.volume") == 573.0
    assert led.rng("gg.volume") == (527.2, 618.8)
    volume = led.quantities["gg.volume"]
    assert (volume.unit, volume.verified, volume.note) == ("m3", False, "computed")
    assert volume.source == "research/01-geometry.md table F"
    # value written as the integer 60, with no low, high or note
    elevation = led.quantities["site.base_elevation_asl"]
    assert isinstance(elevation.value, float) and elevation.value == 60.0
    assert led.rng("site.base_elevation_asl") == (60.0, 60.0)
    assert (elevation.verified, elevation.note) == (True, "")


def test_load_reads_claims(tmp_path):
    led = ledger.load(write_ledger(tmp_path))
    claim = led.claims["S12"]
    assert claim.statement == "Four pump activations fill the Grand Gallery."
    assert (claim.subsystem, claim.timestamp) == ("hydraulic", "F 00:42:41-00:43:10")
    assert (claim.tier, claim.piece, claim.status) == (0, 3, "pending")
    assert claim.criterion == "Pass if the stroke count is within 25 percent of 4."
    assert claim.depends_on == ("gg.volume",)
    assert claim.spaces == ("grand_gallery",)


def test_digest_is_sha256_of_parameters_then_claims(tmp_path):
    led = ledger.load(write_ledger(tmp_path))
    assert led.digest == hashlib.sha256((PARAMS + CLAIMS).encode()).hexdigest()


def test_unknown_quantity_raises_ledger_error(tmp_path):
    led = ledger.load(write_ledger(tmp_path))
    with pytest.raises(ledger.LedgerError, match=re.escape("unknown quantity: gg.length")):
        led.q("gg.length")
    with pytest.raises(ledger.LedgerError, match=re.escape("unknown quantity: gg.length")):
        led.rng("gg.length")


SITE_SOURCE = '"research/02-hydraulics.md section 2.2"'


def without_line(text: str, key: str) -> str:
    """text with the line that sets `key` at the top level of a claim removed."""
    return re.sub(rf"^  {key}:.*\n", "", text, flags=re.M)

# (case name, parameters.yaml text, claims.yaml text, text the error must contain)
BROKEN_LEDGERS = [
    ("duplicate quantity id", PARAMS + PARAMS.splitlines()[0] + "\n", CLAIMS,
     "duplicate id: gg.volume"),
    ("duplicate claim id", PARAMS, CLAIMS + CLAIMS,
     "duplicate id: S12"),
    ("missing source", PARAMS.replace(", source: " + SITE_SOURCE, ""), CLAIMS,
     "site.base_elevation_asl: missing source"),
    ("empty source", PARAMS.replace(SITE_SOURCE, '"  "'), CLAIMS,
     "site.base_elevation_asl: missing source"),
    ("unit not in UNITS", PARAMS.replace('unit: "m3"', 'unit: "furlong"'), CLAIMS,
     "gg.volume: unknown unit 'furlong'"),
    ("value outside its range", PARAMS.replace("low: 527.2", "low: 600.0"), CLAIMS,
     "gg.volume: value 573.0 outside its range 600.0 to 618.8"),
    ("unknown status", PARAMS, CLAIMS.replace("status: pending", "status: maybe"),
     "S12: unknown status 'maybe'"),
    ("tier out of range", PARAMS, CLAIMS.replace("tier: 0", "tier: 3"),
     "S12: tier must be 0, 1 or 2"),
    ("piece out of range", PARAMS, CLAIMS.replace("piece: 3", "piece: 7"),
     "S12: piece must be 1 to 6"),
    ("unknown dependency", PARAMS, CLAIMS.replace("[gg.volume]", "[gg.length]"),
     "S12: depends on unknown quantity: gg.length"),
    # fix round 1, wrong types: a value of the wrong type must not load silently
    ("verified written as text", PARAMS.replace("verified: false", 'verified: "false"'), CLAIMS,
     "gg.volume: verified must be true or false"),
    ("tier is a boolean", PARAMS, CLAIMS.replace("tier: 0", "tier: true"),
     "S12: tier must be an integer"),
    ("tier is a float", PARAMS, CLAIMS.replace("tier: 0", "tier: 1.0"),
     "S12: tier must be an integer"),
    ("piece is a boolean", PARAMS, CLAIMS.replace("piece: 3", "piece: true"),
     "S12: piece must be an integer"),
    ("piece is a float", PARAMS, CLAIMS.replace("piece: 3", "piece: 3.0"),
     "S12: piece must be an integer"),
    ("depends_on is a scalar", PARAMS, CLAIMS.replace("[gg.volume]", "gg.volume"),
     "S12: depends_on must be a list of quantity ids"),
    ("depends_on holds a non-string", PARAMS, CLAIMS.replace("[gg.volume]", "[gg.volume, 5]"),
     "S12: depends_on must be a list of quantity ids"),
    ("spaces is a scalar", PARAMS, CLAIMS.replace("[grand_gallery]", "grand_gallery"),
     "S12: spaces must be a list of space names"),
    ("spaces holds a non-string", PARAMS, CLAIMS.replace("[grand_gallery]", "[grand_gallery, 5]"),
     "S12: spaces must be a list of space names"),
    # YAML reads an unquoted 10:41:15 as the integer 38475
    ("timestamp unquoted", PARAMS,
     CLAIMS.replace('timestamp: "F 00:42:41-00:43:10"', "timestamp: 10:41:15"),
     "S12: timestamp must be text"),
    ("id is a number", PARAMS.replace("id: gg.volume", "id: 12"), CLAIMS,
     "parameters.yaml entry 1: id must be text"),
    ("unit is a list", PARAMS.replace('unit: "m3"', "unit: [m3]"), CLAIMS,
     "gg.volume: unit must be text"),
    ("source is a number", PARAMS.replace('source: "research/01-geometry.md table F"', "source: 5"), CLAIMS,
     "gg.volume: source must be text"),
    ("note is a number", PARAMS.replace('note: "computed"', "note: 5"), CLAIMS,
     "gg.volume: note must be text"),
    ("value is text", PARAMS.replace("value: 573.0", 'value: "abc"'), CLAIMS,
     "gg.volume: value must be a number"),
    ("value is a boolean", PARAMS.replace("value: 573.0", "value: true"), CLAIMS,
     "gg.volume: value must be a number"),
    ("low is text", PARAMS.replace("low: 527.2", 'low: "abc"'), CLAIMS,
     "gg.volume: low must be a number"),
    # fix round 1, structure: a missing key or a malformed file names what is wrong
    ("quantity without id", PARAMS.replace("id: gg.volume, ", ""), CLAIMS,
     "parameters.yaml entry 1: missing id"),
    ("quantity without value", PARAMS.replace("value: 573.0, ", ""), CLAIMS,
     "gg.volume: missing value"),
    ("quantity without unit", PARAMS.replace('unit: "m3", ', ""), CLAIMS,
     "gg.volume: missing unit"),
    ("quantity without verified", PARAMS.replace("verified: false, ", ""), CLAIMS,
     "gg.volume: missing verified"),
    ("claim without id", PARAMS, CLAIMS.replace("- id: S12\n  statement", "- statement"),
     "claims.yaml entry 1: missing id"),
    ("claim without statement", PARAMS, without_line(CLAIMS, "statement"), "S12: missing statement"),
    ("claim without subsystem", PARAMS, without_line(CLAIMS, "subsystem"), "S12: missing subsystem"),
    ("claim without timestamp", PARAMS, without_line(CLAIMS, "timestamp"), "S12: missing timestamp"),
    ("claim without tier", PARAMS, without_line(CLAIMS, "tier"), "S12: missing tier"),
    ("claim without piece", PARAMS, without_line(CLAIMS, "piece"), "S12: missing piece"),
    ("claim without criterion", PARAMS, without_line(CLAIMS, "criterion"), "S12: missing criterion"),
    ("claim without status", PARAMS, without_line(CLAIMS, "status"), "S12: missing status"),
    ("claim without depends_on", PARAMS, without_line(CLAIMS, "depends_on"), "S12: missing depends_on"),
    ("empty parameters file", "", CLAIMS,
     "parameters.yaml: must be a YAML list of mappings"),
    ("parameters file is a mapping", "gg.volume: 573.0\n", CLAIMS,
     "parameters.yaml: must be a YAML list of mappings"),
    ("parameters file is a list of scalars", "- 5\n", CLAIMS,
     "parameters.yaml: must be a YAML list of mappings"),
    ("empty claims file", PARAMS, "",
     "claims.yaml: must be a YAML list of mappings"),
    ("claims file is a mapping", PARAMS, "S12: pending\n",
     "claims.yaml: must be a YAML list of mappings"),
    ("parameters file is not YAML", "- {id: gg.volume\n", CLAIMS,
     "parameters.yaml: not valid YAML"),
    ("claims file is not YAML", PARAMS, "- id: [S12\n",
     "claims.yaml: not valid YAML"),
]


@pytest.mark.parametrize(
    "params, claims, message",
    [case[1:] for case in BROKEN_LEDGERS],
    ids=[case[0] for case in BROKEN_LEDGERS],
)
def test_load_rejects_a_broken_ledger(tmp_path, params, claims, message):
    assert (params, claims) != (PARAMS, CLAIMS)  # the edit above really changed the text
    with pytest.raises(ledger.LedgerError, match=re.escape(message)):
        ledger.load(write_ledger(tmp_path, params, claims))


def test_omitted_spaces_default_to_an_empty_tuple(tmp_path):
    led = ledger.load(write_ledger(tmp_path, claims=without_line(CLAIMS, "spaces")))
    assert led.claims["S12"].spaces == ()


@functools.cache
def real() -> ledger.Ledger:
    """The ledger kept in the repository, loaded once per test run."""
    return ledger.load()


def test_real_ledger_has_site_and_exterior():
    led = real()
    assert led.q("pyr.base_side") == pytest.approx(230.3475)
    assert led.quantities["pyr.base_side"].unit == "m"
    assert led.quantities["pyr.base_side"].note.startswith("9068.8 in")
    assert led.q("pyr.face_slope") == pytest.approx(51.8667)
    assert led.q("pyr.height_original") == pytest.approx(146.7104)
    assert led.q("pyr.height_present") == pytest.approx(137.3759)
    assert led.rng("pyr.height_present") == (137.3607, 137.3937)
    assert round(led.q("pyr.height_present"), 1) == 137.4  # the rounded figure the spec uses
    assert led.q("pyr.passage_plane_x") == pytest.approx(7.2898)
    assert led.rng("site.base_elevation_asl") == (58.0, 62.0)
    assert led.q("site.atm_pressure") == 101325.0


def test_real_ledger_has_the_lower_system():
    led = real()
    assert led.q("dp.entrance.z") == pytest.approx(16.9723)
    assert led.q("dp.south_end.z") == pytest.approx(-29.9974)
    assert led.q("dp.width") * led.q("dp.height") == pytest.approx(1.2658, abs=2e-4)
    # the two surveyed ends of the passage reproduce its stated length and slope
    run = led.q("dp.entrance.y") - led.q("dp.south_end.y")
    drop = led.q("dp.entrance.z") - led.q("dp.south_end.z")
    assert math.hypot(run, drop) == pytest.approx(led.q("dp.length"), abs=0.01)
    assert math.degrees(math.atan2(drop, run)) == pytest.approx(led.q("dp.angle"), abs=0.02)
    assert led.q("sub.roof_centre.z") == pytest.approx(-26.8224)
    assert led.rng("sub.volume") == (200.0, 450.0)
    assert led.q("pit.original_bottom.z") == pytest.approx(-34.57)
    assert led.rng("pit.excavated_bottom.z") == (-43.4, -41.0)
    assert led.q("sp.length") == pytest.approx(16.4084)
    # Haase's seven well-shaft segments sum to the stated length
    segments = sum(led.q(f"ws.seg{i}.length") for i in range(7))
    assert segments == pytest.approx(led.q("ws.length"), abs=0.005)


def test_real_ledger_has_the_upper_system():
    led = real()
    assert led.q("ap.end.z") == pytest.approx(21.656)
    # the Ascending Passage ends where the Grand Gallery floor begins
    for axis in "xyz":
        assert led.q(f"gg.north_end.{axis}") == led.q(f"ap.end.{axis}")
    assert led.q("gg.south_end.z") + led.q("gg.height") == pytest.approx(led.q("gg.roof_top.z"), abs=0.01)
    assert led.rng("gg.volume") == (527.2, 618.8)
    # the Queen's passage, run south from the Gallery's north wall, closes on the chamber's north wall
    assert led.q("gg.north_end.y") - led.q("qp.length") == pytest.approx(led.q("qc.north_wall.y"), abs=0.05)
    # the King's Chamber box reproduces its stated volume, and its walls its stated width
    box = led.q("kc.length") * led.q("kc.width") * led.q("kc.height")
    assert box == pytest.approx(led.q("kc.volume"), abs=0.1)
    low, high = led.rng("kc.volume")
    assert low < box < high
    assert led.q("kc.north_wall.y") - led.q("kc.south_wall.y") == pytest.approx(led.q("kc.width"), abs=0.01)
    assert led.q("qcs.stone_left") == pytest.approx(0.127)
    assert led.rng("ante.groove_connected_area") == (0.0, 0.002)
    assert led.rng("bv.length") == (30.0, 40.0)
    assert led.q("nfc.length") == pytest.approx(9.06)


def test_real_ledger_has_the_2018_model():
    led = real()
    assert (led.q("paper.height"), led.q("paper.base_side")) == (138.75, 230.0)
    assert (led.q("paper.eps_real"), led.q("paper.eps_imag")) == (5.0, 0.1)
    assert (led.q("paper.wavelength_min"), led.q("paper.wavelength_max")) == (200.0, 600.0)
    keys = ("length", "width", "height", "axis_offset", "centre.z")
    assert [led.q(f"paper.kc.{k}") for k in keys] == [11.0, 5.0, 11.0, 5.0, 40.5]
    assert [led.q(f"paper.qc.{k}") for k in keys] == [5.0, 5.0, 6.0, 2.5, 20.8]
    assert [led.q(f"paper.lower.{k}") for k in keys] == [5.2, 5.6, 4.6, 2.4, -29.8]


PREFIXES = {
    "site", "pyr", "dp", "sub", "pit", "sp", "ws", "grotto", "ap", "qp", "qc", "qcs", "gg", "ante",
    "kc", "kcs", "rc", "bv", "nfc", "paper", "hydro", "chem", "em", "ac", "plateau",
}


def test_real_ledger_has_the_physical_inputs():
    led = real()
    assert led.q("hydro.water_density") == pytest.approx(998.2)
    assert led.q("hydro.claimed_strokes") == 4.0
    assert led.rng("hydro.modern_water_table_asl") == (14.5, 17.0)
    assert led.q("chem.dh_so2_to_sulfate") == pytest.approx(-326700.0)
    # the stored reaction enthalpy follows from the stored formation enthalpies
    derived = led.q("chem.dfh_sulfate_aq") - led.q("chem.dfh_so2") - led.q("chem.dfh_h2o_liquid")
    assert derived == pytest.approx(led.q("chem.dh_so2_to_sulfate"), abs=50.0)
    # so does the barrier of the direct gas reaction SO2 + O2 -> SO3 + O; its low end is 05's illustrative 100 kJ/mol
    barrier = led.q("chem.dfh_so3") + led.q("chem.dfh_o_atom") - led.q("chem.dfh_so2")
    assert barrier == pytest.approx(150220.0)
    assert led.q("ac.arrhenius_barrier") == pytest.approx(barrier)
    assert led.rng("ac.arrhenius_barrier") == pytest.approx((100000.0, barrier))
    assert led.rng("em.granite_piezo_d") == (1.4e-15, 7.0e-13)
    assert led.q("em.flash_density") == pytest.approx(2.0e-7)
    assert led.quantities["em.flash_density"].unit == "1/m2/yr"
    assert led.q("ac.absorption_40khz") == pytest.approx(1.318)
    assert led.q("plateau.vein_area") == pytest.approx(0.03)


def test_real_ledger_is_complete_and_annotated():
    led = real()
    assert {key.split(".")[0] for key in led.quantities} >= PREFIXES
    for quantity in led.quantities.values():
        assert re.fullmatch(r"[a-z][a-z0-9_]*(\.[a-z0-9_]+)+", quantity.id), quantity.id
        assert "research/" in quantity.source, quantity.id
        if not quantity.verified:
            assert quantity.note.strip(), f"{quantity.id}: an unverified figure must say why in its note"


STEP_IDS = [f"S{i:02d}" for i in range(1, 32)]
EVIDENCE_IDS = [f"E{i:02d}" for i in range(1, 41)]


def test_claims_hold_the_steps_s01_to_s31_in_order():
    led = real()
    assert [key for key in led.claims if key.startswith("S")] == STEP_IDS
    pump = led.claims["S10"]
    assert (pump.subsystem, pump.tier, pump.piece) == ("hydraulic", 0, 3)
    assert "descending_passage" in pump.spaces and "grand_gallery" in pump.spaces
    assert "gg.roof_top.z" in pump.depends_on


SPACES = {
    "descending_passage", "subterranean_chamber", "pit", "south_passage", "well_shaft", "grotto",
    "ascending_passage", "queens_passage", "queens_chamber", "qc_shaft_north", "qc_shaft_south",
    "grand_gallery", "antechamber", "kings_chamber", "kc_shaft_north", "kc_shaft_south",
    "relieving_chambers", "big_void", "north_face_corridor",
    "paper_kings_chamber", "paper_queens_chamber", "paper_lower_chamber",
}


def test_claims_hold_all_71_ids_once_and_in_order():
    assert list(real().claims) == STEP_IDS + EVIDENCE_IDS


def test_every_claim_is_pending_complete_and_names_known_spaces():
    led = real()
    assert len(led.claims) == 71
    for claim in led.claims.values():
        assert claim.status == "pending", claim.id
        assert claim.statement.strip() and claim.criterion.strip(), claim.id
        assert re.fullmatch(r"F \d\d:\d\d:\d\d-\d\d:\d\d:\d\d", claim.timestamp), claim.id
        assert claim.subsystem in {"gas", "electrical", "hydraulic", "reaction", "auxiliary", "output", "all"}, claim.id
        assert set(claim.spaces) <= SPACES, claim.id


def test_tier_0_claims_name_their_inputs_and_the_field_claims_wait_for_a_solver():
    led = real()
    tier_0 = [claim for claim in led.claims.values() if claim.tier == 0]
    assert tier_0
    for claim in tier_0:
        assert claim.depends_on, f"{claim.id}: a tier 0 claim must name the quantities its calculation reads"
    for key in ("E19", "E20"):
        assert (led.claims[key].tier, led.claims[key].piece) == (1, 1)
    assert "paper_kings_chamber" in led.claims["E19"].spaces
    assert "pyr.height_present" in led.claims["E20"].depends_on
