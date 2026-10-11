"""Tests for the viewer data exporters, checked key by key against the plan header's contracts."""
import json
import math
import re

import pytest
import yaml

from pyramid import REPO_ROOT, screening, viewer_data
from pyramid.geometry.export import to_viewer
from pyramid.ledger import STATUSES, Claim, Ledger, LedgerError, Quantity, load
from pyramid.screening import Result
from pyramid.species import load_species

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
        "quantities": [
            {"id": "gg.volume", "value": 573.0, "unit": "m3", "source": TABLE_F, "verified": False, "note": "computed"},
        ],
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
    # the inspector must be able to tell an assumed figure from a sourced one
    for space in payload["spaces"].values():
        for quantity in space["quantities"]:
            assert set(quantity) == {"id", "value", "unit", "source", "verified", "note"}, quantity["id"]
            assert isinstance(quantity["verified"], bool) and isinstance(quantity["note"], str), quantity["id"]
    grotto = {quantity["id"]: quantity for quantity in payload["spaces"]["grotto"]["quantities"]}
    side = grotto["grotto.plan_side"]
    assert side["verified"] is False and side["note"].startswith("assumed for the model")
    # a claim with a verdict shows the figure the verdict was reached on
    for claim in payload["claims"]:
        assert claim["status"] == "pending" or claim["numbers"], claim["id"]


STEP_IDS = [f"S{i:02d}" for i in range(1, 32)]
SUFFIX = "not specified by the hypothesis"
STEP_KEYS = {"id", "title", "duration", "path", "scene", "species", "actors"}
ACTOR_KEYS = {
    "water": {"type", "space", "from", "to", "species"},
    "gas": {"type", "path", "species"},
    "placeholder": {"type", "kind", "at", "label"},
    "lightning": {"type"},
    "field": {"type", "slice"},
    "coat": {"type", "space"},
}
PLACEHOLDER_KINDS = {"pump", "valve", "reservoir", "drain", "gas_inlet"}
STATED = "as stated in the video"
# docs/superpowers/specs/2026-10-10-chemistry-display-kings-chamber-design.md section 3.2
REACTIONS = {
    "S02": ("not stated by the hypothesis", "the video names a conversion without giving it"),
    "S16": ("2 SO₂ + O₂ → 2 SO₃", STATED),
    "S19": ("SO₂ + H₂O → H₂SO₃", STATED),
    "S20": ("2 H₂SO₃ + O₂ → 2 H₂SO₄", STATED),
    "S21": ("SO₃ + H₂O → H₂SO₄ (into dilute acid)", STATED),
    "S23": ("CaCO₃ + H₂SO₄ → CaSO₄ + H₂O + CO₂", STATED),
    "S27": ("H₂SO₄ + 2 NaCl → Na₂SO₄ + 2 HCl", STATED),
}


def authored() -> dict:
    """ledger/cycle.yaml as written by hand, in the project frame."""
    return yaml.safe_load((REPO_ROOT / "ledger" / "cycle.yaml").read_bytes())


def step_of(cycle: dict, step_id: str) -> dict:
    return next(step for step in cycle["steps"] if step["id"] == step_id)


def actors(step_id: str, kind: str) -> list[dict]:
    return [actor for actor in step_of(authored(), step_id)["actors"] if actor["type"] == kind]


def is_point(value) -> bool:
    return isinstance(value, list) and len(value) == 3 and all(isinstance(v, (int, float)) for v in value)


def is_keyframe(value) -> bool:
    return isinstance(value, dict) and set(value) == {"position", "target"} and \
        is_point(value["position"]) and is_point(value["target"])


def test_cycle_has_a_prologue_then_one_entry_per_step_in_order_and_every_id_is_a_claim():
    cycle = authored()
    assert set(cycle) == {"prologue", "steps"}
    assert [step["id"] for step in cycle["steps"]] == STEP_IDS
    assert set(STEP_IDS) <= set(load().claims)


def test_the_prologue_is_a_six_second_flight_with_no_claim():
    prologue = authored()["prologue"]
    assert set(prologue) == {"duration", "path"}
    assert prologue["duration"] == 6.0
    assert len(prologue["path"]) == 3 and all(is_keyframe(keyframe) for keyframe in prologue["path"])


def test_every_step_and_actor_matches_the_contract():
    species = load_species()
    for step in authored()["steps"]:
        where = step["id"]
        assert set(step) == STEP_KEYS | ({"reaction"} if where in REACTIONS else set()), where
        assert isinstance(step["title"], str) and step["title"], where
        assert isinstance(step["duration"], float) and step["duration"] > 0, where
        assert 2 <= len(step["path"]) <= 4, where
        assert all(is_keyframe(keyframe) for keyframe in step["path"]), where
        assert set(step["scene"]) == {"interior", "weather"} and isinstance(step["scene"]["interior"], bool), where
        assert step["scene"]["weather"] in ("clear", "storm"), where
        assert set(step["species"]) <= set(species), where
        for actor in step["actors"]:
            assert set(actor) == ACTOR_KEYS[actor["type"]], (where, actor)
            if actor["type"] in ("water", "gas"):
                assert actor["species"] and set(actor["species"]) <= set(species), (where, actor)
            if actor["type"] in ("water", "coat"):
                assert actor["space"] in SURVEY_SPACES, (where, actor)
            if actor["type"] == "water":
                assert 0.0 <= actor["from"] <= 1.0 and 0.0 <= actor["to"] <= 1.0, (where, actor)
            if actor["type"] == "gas":
                assert actor["path"] and set(actor["path"]) <= set(SURVEY_SPACES), (where, actor)
            if actor["type"] == "placeholder":
                assert actor["kind"] in PLACEHOLDER_KINDS, (where, actor)
                assert is_point(actor["at"]), (where, actor)
                assert actor["label"].endswith(SUFFIX), (where, actor)
            if actor["type"] == "field":
                assert re.fullmatch(r"fields/\w+\.png", actor["slice"]), (where, actor)


INSIDE = {"water", "placeholder", "coat"}   # actors drawn inside the stone


def test_a_step_is_interior_exactly_when_it_draws_inside_the_stone_where_its_claim_acts():
    # the camera may stand outside looking in; the flag follows the actors and the claim, never the camera.
    # A gas counts only when its path starts in a space the claim names: a tint that merely persists
    # elsewhere (the King's Chamber through S04 and S05, whose claims name no space) does not.
    claims = load().claims
    for step in authored()["steps"]:
        spaces = claims[step["id"]].spaces
        inside = any(actor["type"] in INSIDE or (actor["type"] == "gas" and actor["path"][0] in spaces)
                     for actor in step["actors"])
        assert step["scene"]["interior"] is inside, step["id"]


def test_only_the_two_storm_steps_carry_the_storm():
    assert [step["id"] for step in authored()["steps"] if step["scene"]["weather"] == "storm"] == ["S05", "S06"]


def test_the_reaction_steps_carry_the_equation_as_stated_and_the_claims_timestamp():
    claims = load().claims
    cycle = authored()
    assert [step["id"] for step in cycle["steps"] if "reaction" in step] == list(REACTIONS)
    for step_id, (equation, note) in REACTIONS.items():
        assert step_of(cycle, step_id)["reaction"] == {
            "equation": equation, "timestamp": claims[step_id].timestamp, "note": note,
        }, step_id


def test_the_gallery_liquid_turns_to_acid_where_the_claims_put_it():
    liquid = {
        (step["id"], actor["space"]): actor["species"]
        for step in authored()["steps"] for actor in step["actors"] if actor["type"] == "water"
    }
    acid = {("S19", "grand_gallery"): ["sulfurous_acid", "water"]}
    acid |= {(f"S{i}", "grand_gallery"): ["sulfuric_acid", "water"] for i in range(20, 27)}
    for key, species in liquid.items():
        assert species == acid.get(key, ["water"]), key
    assert set(acid) <= set(liquid)


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
    assert {"type": "gas", "path": ["kings_chamber", "antechamber"], "species": ["so2"]} in actors("S15", "gas")
    assert {"type": "gas", "path": ["antechamber"], "species": ["so3"]} in actors("S16", "gas")
    used = {actor["kind"] for step in authored()["steps"] for actor in step["actors"] if actor["type"] == "placeholder"}
    assert used == PLACEHOLDER_KINDS
    # the calcium sulfate layer of S23, on the two spaces the claim names, and nowhere else
    assert actors("S23", "coat") == [{"type": "coat", "space": "grand_gallery"}, {"type": "coat", "space": "queens_chamber"}]
    coated = [step["id"] for step in authored()["steps"] for actor in step["actors"] if actor["type"] == "coat"]
    assert coated == ["S23", "S23"]


def test_the_gallery_fills_in_four_quarters_drains_and_fills_again():
    gallery = {
        step["id"]: (actor["from"], actor["to"])
        for step in authored()["steps"] for actor in step["actors"]
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
    for step in authored()["steps"]:
        current = {actor["space"]: actor for actor in step["actors"] if actor["type"] == "water"}
        for space, actor in current.items():
            if space in previous:
                assert actor["from"] == previous[space], (step["id"], space)
        previous = {space: actor["to"] for space, actor in current.items()}


CURVES = {"grand_gallery": [(21.656, 0.0), (51.5, 573.0)]}
# a fixed verdict per producing step, so each marking below is known exactly
MARKS = {"S16": "fail", "S20": "conditional"}
PAYLOAD_KEYS = {"id", "formula", "name", "phase", "colour", "status"}
WATER = {"id": "water", "formula": "H₂O", "name": "water", "phase": "liquid", "colour": "#2f86d6", "status": "plain"}


def payload() -> dict:
    return viewer_data.cycle_payload(load(), CURVES, load_species(), MARKS)


def test_cycle_payload_has_the_contract_keys_the_notice_and_the_curves():
    cycle = payload()
    assert set(cycle) == {"notice", "prologue", "steps", "curves"}
    assert cycle["notice"] == "Animation of the claim. Not a simulation result."
    assert [step["id"] for step in cycle["steps"]] == STEP_IDS
    for step in cycle["steps"]:
        assert set(step) == STEP_KEYS | ({"reaction"} if step["id"] in REACTIONS else set()), step["id"]
        assert all(is_keyframe(keyframe) for keyframe in step["path"]), step["id"]
        for species in step["species"]:
            assert set(species) == PAYLOAD_KEYS, step["id"]
        for actor in step["actors"]:
            assert set(actor) == ACTOR_KEYS[actor["type"]], (step["id"], actor)
            for species in actor.get("species", []):
                assert set(species) == PAYLOAD_KEYS, (step["id"], actor)
    written = json.loads(json.dumps(cycle, allow_nan=False))
    assert written["curves"] == {"grand_gallery": [[21.656, 0.0], [51.5, 573.0]]}


def test_cycle_payload_moves_keyframes_and_placeholders_into_viewer_coordinates():
    cycle = payload()
    # project (x east, y north, z up) becomes viewer (x, z, -y)
    # the prologue's first keyframe, authored as position [620, 520, 150], target [0, 60, 70]
    assert cycle["prologue"]["duration"] == 6.0
    assert cycle["prologue"]["path"][0] == {"position": [620, 150, -520], "target": [0, 70, -60]}
    step = step_of(cycle, "S08")
    # S08's first keyframe, plan A's camera, authored as position [200, 40, 15], target [7, 55, -8]
    assert step["path"][0] == {"position": [200, 15, -40], "target": [7, -8, -55]}
    second = step_of(authored(), "S08")["path"][1]
    assert step["path"][1] == {"position": list(to_viewer(*second["position"])),
                               "target": list(to_viewer(*second["target"]))}
    reservoir = next(actor for actor in step["actors"] if actor["type"] == "placeholder")
    assert reservoir["at"] == [7, 0, -125]   # authored as [7, 125, 0]
    assert reservoir["label"] == "Reservoir: not specified by the hypothesis"
    # a water actor keeps its keys; its species id becomes the species' payload
    assert {"type": "water", "space": "subterranean_chamber", "from": 0.0, "to": 1.0, "species": [WATER]} in step["actors"]
    assert (step["title"], step["duration"]) == ("Reservoir water enters the Subterranean Chamber", 6.0)
    assert step["scene"] == {"interior": True, "weather": "clear"}   # S08 draws water and a placeholder


def test_cycle_payload_marks_each_species_by_the_verdict_of_its_producing_step():
    step = step_of(payload(), "S21")   # species [so3, water, sulfuric_acid]
    assert [(species["id"], species["status"]) for species in step["species"]] == [
        ("so3", "claimed"),                # S16 fail
        ("water", "plain"),                # an input
        ("sulfuric_acid", "conditional"),  # S20 conditional
    ]
    gallery = next(actor for actor in step["actors"] if actor["type"] == "water" and actor["space"] == "grand_gallery")
    assert [(species["id"], species["status"]) for species in gallery["species"]] == [
        ("sulfuric_acid", "conditional"), ("water", "plain"),
    ]
    assert gallery["species"][0]["colour"] == "#c25b5b"   # the liquid's colour comes from the species table


def test_cycle_payload_rejects_a_step_that_is_not_a_claim():
    # the tiny ledger holds only S12 and S05, so the first step of cycle.yaml is unknown to it
    with pytest.raises(LedgerError, match=re.escape("cycle.yaml: S01 is not a claim id")):
        viewer_data.cycle_payload(tiny_ledger(), CURVES, load_species(), {})


def drop_gas_species(step: dict) -> None:
    next(actor for actor in step["actors"] if actor["type"] == "gas").pop("species")


@pytest.mark.parametrize("change, message", [
    (lambda step: step.update(path=step["path"][:1]), "cycle.yaml: S03: path needs 2 to 4 keyframes"),
    (lambda step: step.update(path=step["path"] * 3), "cycle.yaml: S03: path needs 2 to 4 keyframes"),
    (lambda step: step.update(species=["xyz"]), "cycle.yaml: S03: unknown species xyz"),
    (drop_gas_species, "cycle.yaml: S03: gas actor needs species"),
    (lambda step: step["scene"].update(weather="fog"), "cycle.yaml: S03: weather must be clear or storm"),
])
def test_cycle_payload_rejects_a_broken_step_naming_it(tmp_path, monkeypatch, change, message):
    cycle = authored()
    change(step_of(cycle, "S03"))   # one thing broken on one step; everything else as authored
    broken = tmp_path / "cycle.yaml"
    broken.write_text(yaml.safe_dump(cycle, allow_unicode=True, sort_keys=False), encoding="utf-8")
    monkeypatch.setattr(viewer_data, "CYCLE_FILE", broken)
    with pytest.raises(LedgerError, match=re.escape(message)):
        viewer_data.cycle_payload(load(), CURVES, load_species(), {})
