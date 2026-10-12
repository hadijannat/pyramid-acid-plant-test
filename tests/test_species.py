"""Tests for the species table and the marking rule, checked against the plan header's contract."""
import re
from pathlib import Path

import pytest
import yaml

from pyramid import REPO_ROOT, verdicts
from pyramid.ledger import STATUSES, LedgerError, load
from pyramid.species import SPECIES_FILE, Species, load_species, species_payload, species_status

IDS = ["h2s", "so2", "air", "so3", "water", "sulfurous_acid", "sulfuric_acid", "calcium_sulfate", "hydrogen_chloride"]


def test_the_real_table_has_the_nine_compounds_the_video_names_in_order():
    claims = load().claims
    species = load_species(step_ids=set(claims))
    assert SPECIES_FILE == REPO_ROOT / "ledger" / "species.yaml"
    assert list(species) == IDS
    assert species["so2"] == Species("so2", "SO₂", "sulfur dioxide", "gas", "#d9c24a", "S02")
    # what each step makes in the claimed cycle; the marking rule reads nothing else
    assert {key: entry.produced_by for key, entry in species.items()} == {
        "h2s": None, "so2": "S02", "air": None, "so3": "S16", "water": None,
        "sulfurous_acid": "S19", "sulfuric_acid": "S20", "calcium_sulfate": "S23", "hydrogen_chloride": "S27",
    }
    for entry in species.values():
        assert entry.produced_by is None or entry.produced_by in claims, entry.id
        assert not re.search(r"[0-9]", entry.formula), entry.id   # subscripts are Unicode, never ASCII digits


SO2 = {"id": "so2", "formula": "SO₂", "name": "sulfur dioxide", "phase": "gas", "colour": "#d9c24a", "produced_by": "S02"}


def write(tmp_path: Path, entries) -> Path:
    path = tmp_path / "species.yaml"
    path.write_text(yaml.safe_dump(entries, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def without(entry: dict, key: str) -> dict:
    return {name: value for name, value in entry.items() if name != key}


@pytest.mark.parametrize("entries, message", [
    ([{**SO2, "color": "#d9c24a"}], "species.yaml: so2: unknown key 'color'"),
    ([without(SO2, "name")], "species.yaml: so2: missing name"),
    ([without(SO2, "produced_by")], "species.yaml: so2: missing produced_by"),
    ([without(SO2, "id")], "species.yaml entry 1: missing id"),
    ([{**SO2, "formula": 2}], "species.yaml: so2: formula must be text"),
    ([{**SO2, "phase": "plasma"}], "species.yaml: so2: phase must be gas, liquid or solid, not 'plasma'"),
    ([{**SO2, "colour": "yellow"}], "species.yaml: so2: colour must be #rrggbb in lower-case hex, not 'yellow'"),
    ([{**SO2, "colour": "#D9C24A"}], "species.yaml: so2: colour must be #rrggbb in lower-case hex, not '#D9C24A'"),
    ([SO2, SO2], "species.yaml: duplicate id: so2"),
    ([{**SO2, "produced_by": "S99"}], "species.yaml: so2: produced_by S99 is not a step id"),
    ({"so2": SO2}, "species.yaml: must be a YAML list of mappings"),
])
def test_a_broken_table_is_rejected_naming_the_entry(tmp_path, entries, message):
    with pytest.raises(LedgerError, match=re.escape(message)):
        load_species(write(tmp_path, entries), step_ids={"S02"})


def test_produced_by_is_checked_against_the_steps_only_when_they_are_given(tmp_path):
    loaded = load_species(write(tmp_path, [{**SO2, "produced_by": "S99"}]))
    assert loaded["so2"].produced_by == "S99"


MARKING = [("fail", "claimed"), ("undefined", "claimed"), ("conditional", "conditional"),
           ("pass", "plain"), ("pending", "plain"), ("not_testable", "plain")]


def test_the_marking_cases_cover_every_verdict_word():
    assert sorted(verdict for verdict, _ in MARKING) == sorted(STATUSES)


@pytest.mark.parametrize("verdict, status", MARKING)
def test_a_species_takes_its_status_from_the_verdict_of_the_step_that_produces_it(verdict, status):
    so3 = load_species()["so3"]   # produced by S16
    assert species_status(so3, {"S16": verdict}) == status
    # another step's verdict does not touch it
    assert species_status(so3, {"S16": "pass", "S20": verdict}) == "plain"


def test_an_input_is_plain_whatever_the_verdicts():
    water = load_species()["water"]   # produced_by None
    assert species_status(water, dict.fromkeys(load().claims, "fail")) == "plain"


def test_the_payload_is_the_table_entry_without_produced_by_plus_the_status():
    assert species_payload(load_species()["so3"], {"S16": "fail"}) == {
        "id": "so3", "formula": "SO₃", "name": "sulfur trioxide", "phase": "gas", "colour": "#e08a3c",
        "status": "claimed",
    }


def test_with_the_verdicts_as_they_stand_the_products_of_failed_and_undefined_steps_are_marked_claimed():
    """The marking the viewer ships, from Tier 0 and the packages: S02 is undefined, S16, S20 and S27 fail, S19 and
    S23 are conditional. Update these sets when a verdict changes."""
    led = load()
    statuses = {claim: status for claim, (status, _) in verdicts.merged(led)[1].items()}
    marked = {key: species_status(entry, statuses) for key, entry in load_species(step_ids=set(led.claims)).items()}
    assert {key for key, status in marked.items() if status == "claimed"} == {
        "so2", "so3", "sulfuric_acid", "hydrogen_chloride"}
    assert {key for key, status in marked.items() if status == "conditional"} == {"sulfurous_acid", "calcium_sulfate"}
    assert {key for key, status in marked.items() if status == "plain"} == {"h2s", "air", "water"}
