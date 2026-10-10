"""Tests for the ledger loader and for the ledger files themselves."""
import hashlib
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
