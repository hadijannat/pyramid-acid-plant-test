"""Tests for the viewer data exporters, checked key by key against the plan header's contracts."""
import json
import math
import re

import pytest
import yaml

from pyramid import REPO_ROOT, screening, viewer_data
from pyramid.ledger import STATUSES, Claim, Ledger, LedgerError, Quantity, load
from pyramid.screening import Result

SURVEY_SPACES = [
    "descending_passage", "subterranean_chamber", "pit", "south_passage", "well_shaft", "grotto",
    "ascending_passage", "queens_passage", "queens_chamber", "qc_shaft_north", "qc_shaft_south",
    "grand_gallery", "antechamber", "kings_chamber", "kc_shaft_north", "kc_shaft_south",
    "relieving_chambers", "big_void", "north_face_corridor",
]
PAPER_SPACES = ["paper_kings_chamber", "paper_queens_chamber", "paper_lower_chamber"]
TABLE_C = "research/01-geometry.md table C"
TABLE_F = "research/01-geometry.md table F"


def tiny_ledger() -> Ledger:
    """Five quantities and two claims, built in memory so that every expected value below is exact."""
    quantities = {
        quantity.id: quantity
        for quantity in (
            Quantity("gg.volume", 573.0, "m3", 527.2, 618.8, TABLE_F, False, "computed"),
            Quantity("dp.volume", 133.1, "m3", 129.1, 137.1, TABLE_F, False, "computed"),
            Quantity("kcs.mouth_height", 0.9144, "m", 0.9144, 0.9144, TABLE_C, True),
            Quantity("kcs.north.width", 0.2299, "m", 0.2261, 0.2337, TABLE_C, True),
            Quantity("kcs.south.width", 0.2159, "m", 0.2121, 0.2197, TABLE_C, True),
        )
    }
    claims = {
        "S12": Claim(
            "S12", "Four activations fill the Grand Gallery.", "hydraulic", "F 00:42:41-00:43:10", 0, 3,
            "Pass if the stroke count is within 25 percent of 4.", "pending",
            ("gg.volume", "dp.volume"), ("grand_gallery", "descending_passage"),
        ),
        "S05": Claim(
            "S05", "Operators wait for a storm.", "electrical", "F 01:09:08-01:10:54", 2, 6,
            "No computed verdict.", "pending", (), (),
        ),
    }
    return Ledger(quantities, claims, "0" * 64)


RESULTS = {
    # reads only quantities that S12 depends on: belongs to S12
    "t0.strokes": Result("t0.strokes", "Strokes to fill the gallery", 4.305, 3.845, 4.793, "1",
                         "gg.volume / dp.volume", ("gg.volume", "dp.volume")),
    # reads a quantity that no claim of the tiny ledger depends on: belongs to no claim
    "t0.shaft_width": Result("t0.shaft_width", "North shaft width", 0.2299, 0.2261, 0.2337, "m",
                             "kcs.north.width", ("kcs.north.width",)),
}
VERDICTS = {"S12": ("conditional", "4.3 strokes if the whole passage is swept and nothing else is filled")}


def test_claims_payload_has_the_three_contract_keys_and_a_viewer_manifest():
    led = tiny_ledger()
    payload = viewer_data.claims_payload(led, RESULTS, VERDICTS)
    assert set(payload) == {"manifest", "claims", "spaces"}
    assert payload["manifest"]["case"] == "viewer"
    assert payload["manifest"]["ledger"] == led.digest
    assert {"commit", "versions"} <= set(payload["manifest"])


def test_a_decided_claim_carries_its_verdict_basis_and_numbers():
    payload = viewer_data.claims_payload(tiny_ledger(), RESULTS, VERDICTS)
    assert payload["claims"][0] == {
        "id": "S12",
        "statement": "Four activations fill the Grand Gallery.",
        "subsystem": "hydraulic",
        "timestamp": "F 00:42:41-00:43:10",
        "tier": 0,
        "piece": 3,
        "criterion": "Pass if the stroke count is within 25 percent of 4.",
        "status": "conditional",
        "basis": "4.3 strokes if the whole passage is swept and nothing else is filled",
        "numbers": [
            {"label": "Strokes to fill the gallery", "value": 4.305, "low": 3.845, "high": 4.793, "unit": "1"},
        ],
        "spaces": ["grand_gallery", "descending_passage"],
    }


def test_an_undecided_claim_keeps_its_ledger_status_and_has_no_numbers():
    payload = viewer_data.claims_payload(tiny_ledger(), RESULTS, VERDICTS)
    waiting = payload["claims"][1]
    assert (waiting["id"], waiting["status"], waiting["basis"], waiting["numbers"]) == ("S05", "pending", "", [])


def test_a_bound_that_is_not_finite_becomes_null():
    open_ended = {
        "t0.lifetime": Result("t0.lifetime", "Lifetime", 2.8e17, 2.8e17, math.inf, "s", "1 / (k n)", ("gg.volume",)),
    }
    payload = viewer_data.claims_payload(tiny_ledger(), open_ended, {})
    assert payload["claims"][0]["numbers"] == [
        {"label": "Lifetime", "value": 2.8e17, "low": 2.8e17, "high": None, "unit": "s"},
    ]
    json.dumps(payload, allow_nan=False)  # raises ValueError if an infinity or a NaN is left


def test_space_index_lists_every_header_space_with_its_quantities_and_claims():
    payload = viewer_data.claims_payload(tiny_ledger(), RESULTS, VERDICTS)
    assert list(payload["spaces"]) == SURVEY_SPACES + PAPER_SPACES
    assert payload["spaces"]["grand_gallery"] == {
        "label": "Grand Gallery",
        "quantities": [{"id": "gg.volume", "value": 573.0, "unit": "m3", "source": TABLE_F}],
        "claims": ["S12"],
    }
    # a shaft gets the quantities both shafts share and its own, never the other shaft's
    north = payload["spaces"]["kc_shaft_north"]
    assert [quantity["id"] for quantity in north["quantities"]] == ["kcs.mouth_height", "kcs.north.width"]
    # "kc." must not match the "kcs." ids of the shafts
    assert payload["spaces"]["kings_chamber"] == {"label": "King's Chamber", "quantities": [], "claims": []}


def test_real_claims_payload_covers_all_71_claims_and_is_strict_json():
    led = load()
    results = screening.all_results(led)
    payload = viewer_data.claims_payload(led, results, screening.verdicts(led, results))
    assert [claim["id"] for claim in payload["claims"]] == list(led.claims)
    assert len(payload["claims"]) == 71
    for claim in payload["claims"]:
        assert claim["status"] in STATUSES, claim["id"]
        assert set(claim["spaces"]) <= set(payload["spaces"]), claim["id"]
    gallery = payload["spaces"]["grand_gallery"]
    assert "S12" in gallery["claims"]
    assert any(quantity["id"] == "gg.volume" for quantity in gallery["quantities"])
    json.dumps(payload, allow_nan=False)


STEP_IDS = [f"S{i:02d}" for i in range(1, 32)]
SUFFIX = "not specified by the hypothesis"
ACTOR_KEYS = {
    "water": {"type", "space", "from", "to"},
    "gas": {"type", "path", "color"},
    "placeholder": {"type", "kind", "at", "label"},
    "lightning": {"type"},
    "field": {"type", "slice"},
}
PLACEHOLDER_KINDS = {"pump", "valve", "reservoir", "drain", "gas_inlet"}


def authored() -> list[dict]:
    """ledger/cycle.yaml as written by hand, in the project frame."""
    return yaml.safe_load((REPO_ROOT / "ledger" / "cycle.yaml").read_text())


def actors(step_id: str, kind: str) -> list[dict]:
    step = next(step for step in authored() if step["id"] == step_id)
    return [actor for actor in step["actors"] if actor["type"] == kind]


def is_point(value) -> bool:
    return isinstance(value, list) and len(value) == 3 and all(isinstance(v, (int, float)) for v in value)


def test_cycle_has_one_entry_per_step_in_order_and_every_id_is_a_claim():
    assert [step["id"] for step in authored()] == STEP_IDS
    assert set(STEP_IDS) <= set(load().claims)


def test_every_step_and_actor_matches_the_contract():
    for step in authored():
        where = step["id"]
        assert set(step) == {"id", "title", "duration", "camera", "actors"}, where
        assert isinstance(step["title"], str) and step["title"], where
        assert isinstance(step["duration"], float) and step["duration"] > 0, where
        assert set(step["camera"]) == {"position", "target"}, where
        assert is_point(step["camera"]["position"]) and is_point(step["camera"]["target"]), where
        for actor in step["actors"]:
            assert set(actor) == ACTOR_KEYS[actor["type"]], (where, actor)
            if actor["type"] == "water":
                assert actor["space"] in SURVEY_SPACES, (where, actor)
                assert 0.0 <= actor["from"] <= 1.0 and 0.0 <= actor["to"] <= 1.0, (where, actor)
            if actor["type"] == "gas":
                assert actor["path"] and set(actor["path"]) <= set(SURVEY_SPACES), (where, actor)
                assert re.fullmatch(r"#[0-9a-f]{6}", actor["color"]), (where, actor)
            if actor["type"] == "placeholder":
                assert actor["kind"] in PLACEHOLDER_KINDS, (where, actor)
                assert is_point(actor["at"]), (where, actor)
                assert actor["label"].endswith(SUFFIX), (where, actor)
            if actor["type"] == "field":
                assert re.fullmatch(r"fields/\w+\.png", actor["slice"]), (where, actor)


def test_each_kind_of_actor_appears_on_the_step_that_claims_it():
    assert actors("S06", "lightning") == [{"type": "lightning"}]
    slices = [actor["slice"] for actor in actors("S04", "field") + actors("S06", "field")]
    assert slices == ["fields/R2_333m.png", "fields/R1_230m.png"]
    kinds = {step_id: {actor["kind"] for actor in actors(step_id, "placeholder")}
             for step_id in ("S03", "S08", "S09", "S10", "S13", "S26")}
    assert kinds == {
        "S03": {"gas_inlet"}, "S08": {"reservoir"}, "S09": {"valve"},
        "S10": {"pump", "valve"}, "S13": {"drain"}, "S26": {"drain"},
    }
    assert {"type": "gas", "path": ["kings_chamber", "antechamber"], "color": "#d9c24a"} in actors("S15", "gas")
    used = {actor["kind"] for step in authored() for actor in step["actors"] if actor["type"] == "placeholder"}
    assert used == PLACEHOLDER_KINDS


def test_the_gallery_fills_in_four_quarters_drains_and_fills_again():
    gallery = {
        step["id"]: (actor["from"], actor["to"])
        for step in authored() for actor in step["actors"]
        if actor["type"] == "water" and actor["space"] == "grand_gallery"
    }
    quarter = 1 / load().q("hydro.claimed_strokes")                  # one of the claimed four activations
    assert gallery["S10"] == (0.0, quarter)                          # the first activation
    assert gallery["S12"] == (quarter, 1.0)                          # the other three
    assert gallery["S13"][0] == 1.0 and gallery["S17"][1] == 0.0     # lowered over S13 to S17
    assert gallery["S18"] == (0.0, quarter)                          # raised again, in four activations,
    assert gallery["S21"][1] == 1.0                                  # over S18 to S21
    assert gallery["S26"] == (1.0, 0.0)                              # withdrawn


def test_water_standing_at_the_reservoir_level_follows_the_ledger():
    """Step S09 leaves the water at pavement level (Z = 0); the two fractions are recomputed from the ledger."""
    led = load()
    reached = {actor["space"]: actor["to"] for actor in actors("S09", "water")}
    below_pavement = (led.q("ws.volume") - led.q("ws.volume_above_base")) / led.q("ws.volume")
    assert reached["well_shaft"] == round(below_pavement, 2)
    # the passage is straight and of one cross-section, so its volume below a level goes with the height
    below_pavement = -led.q("dp.south_end.z") / (led.q("dp.entrance.z") - led.q("dp.south_end.z"))
    assert reached["descending_passage"] == round(below_pavement, 2)


def test_water_levels_join_up_from_one_step_to_the_next():
    previous: dict[str, float] = {}
    for step in authored():
        current = {actor["space"]: actor for actor in step["actors"] if actor["type"] == "water"}
        for space, actor in current.items():
            if space in previous:
                assert actor["from"] == previous[space], (step["id"], space)
        previous = {space: actor["to"] for space, actor in current.items()}


CURVES = {"grand_gallery": [(21.656, 0.0), (51.5, 573.0)]}


def test_cycle_payload_has_the_contract_keys_the_notice_and_the_curves():
    payload = viewer_data.cycle_payload(load(), CURVES)
    assert set(payload) == {"notice", "steps", "curves"}
    assert payload["notice"] == "Animation of the claim. Not a simulation result."
    assert [step["id"] for step in payload["steps"]] == STEP_IDS
    for step in payload["steps"]:
        assert set(step) == {"id", "title", "duration", "camera", "actors"}, step["id"]
        assert set(step["camera"]) == {"position", "target"}, step["id"]
        for actor in step["actors"]:
            assert set(actor) == ACTOR_KEYS[actor["type"]], (step["id"], actor)
    written = json.loads(json.dumps(payload, allow_nan=False))
    assert written["curves"] == {"grand_gallery": [[21.656, 0.0], [51.5, 573.0]]}


def test_cycle_payload_moves_cameras_and_placeholders_into_viewer_coordinates():
    payload = viewer_data.cycle_payload(load(), CURVES)
    step = next(step for step in payload["steps"] if step["id"] == "S08")
    # authored in the project frame as position [200, 40, 15], target [7, 55, -8];
    # project (x east, y north, z up) becomes viewer (x, z, -y)
    assert step["camera"] == {"position": [200, 15, -40], "target": [7, -8, -55]}
    reservoir = next(actor for actor in step["actors"] if actor["type"] == "placeholder")
    assert reservoir["at"] == [7, 0, -125]   # authored as [7, 125, 0]
    assert reservoir["label"] == "Reservoir: not specified by the hypothesis"
    # every other actor passes through untouched
    assert {"type": "water", "space": "subterranean_chamber", "from": 0.0, "to": 1.0} in step["actors"]
    assert (step["title"], step["duration"]) == ("Reservoir water enters the Subterranean Chamber", 6.0)


def test_cycle_payload_rejects_a_step_that_is_not_a_claim():
    # the tiny ledger holds only S12 and S05, so the first step of cycle.yaml is unknown to it
    with pytest.raises(LedgerError, match=re.escape("cycle.yaml: S01 is not a claim id")):
        viewer_data.cycle_payload(tiny_ledger(), CURVES)
