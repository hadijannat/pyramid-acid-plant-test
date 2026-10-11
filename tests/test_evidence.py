"""The evidence register: what it covers, what its loader refuses, and how it joins the other verdicts."""
import copy

import pytest
import yaml

from pyramid import REPO_ROOT, evidence, ledger, premises, screening, simkit, verdicts
from pyramid.ledger import LedgerError


@pytest.fixture(scope="module")
def led() -> ledger.Ledger:
    return ledger.load()


@pytest.fixture(scope="module")
def register() -> dict[str, evidence.Entry]:
    return evidence.load_evidence()


# The status of every claim, pinned so that a change to the register is a deliberate change here too.
STATUS = {
    "S02": "undefined", "S26": "undefined",
    "S05": "not_testable", "E05": "not_testable", "E23": "not_testable", "E24": "not_testable", "E40": "not_testable",
    "E02": "fail", "E03": "fail", "E04": "conditional", "E06": "undefined", "E07": "fail", "E08": "fail",
    "E09": "fail", "E10": "pass", "E16": "fail", "E26": "pass", "E27": "fail", "E28": "conditional",
    "E30": "conditional", "E31": "undefined", "E33": "conditional", "E34": "undefined", "E35": "conditional",
    "E36": "fail", "E37": "conditional", "E39": "conditional",
}


def test_the_register_covers_exactly_the_27_evidence_claims(led, register):
    assert len(evidence.CLAIMS) == 27 == len(set(evidence.CLAIMS))
    assert set(register) == set(evidence.CLAIMS) == set(STATUS)
    assert all(claim in led.claims for claim in register)
    assert evidence.EVIDENCE_FILE == REPO_ROOT / "ledger" / "evidence.yaml"


def test_every_status_is_in_the_vocabulary_and_as_pinned(register):
    assert {key: entry.status for key, entry in register.items()} == STATUS
    assert all(entry.status in evidence.STATUSES for entry in register.values())
    assert "pending" not in evidence.STATUSES and set(evidence.STATUSES) < set(ledger.STATUSES)


def test_not_testable_and_undefined_follow_the_criteria_own_words(led, register):
    assert {key for key, entry in register.items() if entry.status == "not_testable"} == {
        "S05", "E05", "E23", "E24", "E40"}
    for claim in evidence.NOT_TESTABLE:
        assert led.claims[claim].criterion.startswith(("Cannot be simulated", "Analogy only")), claim
    for claim in evidence.UNDEFINED:
        assert register[claim].status == "undefined"
        assert led.claims[claim].criterion.startswith("Undefined until the hypothesis names"), claim


def test_every_basis_opens_with_a_standing_and_is_plain_prose(register):
    for key, entry in register.items():
        assert entry.basis.startswith(evidence.STANDINGS), key
        assert "\n" not in entry.basis and "  " not in entry.basis, key
    raw = evidence.EVIDENCE_FILE.read_text()
    assert "—" not in raw and "–" not in raw
    # The standing goes with the status: a pass is supported, no test means not_testable, and so on.
    opening = {"pass": ("Supported:",), "not_testable": ("No test exists:",),
               "fail": ("Contradicted:", "No evidence found:"),
               "conditional": ("Partly supported:", "No evidence found:"),
               "undefined": ("Not specified by the hypothesis:", "No evidence found:")}
    for key, entry in register.items():
        assert entry.basis.startswith(opening[entry.status]), key


def test_every_source_is_a_research_file_that_exists(register):
    for key, entry in register.items():
        assert entry.sources, key
        for source in entry.sources:
            name = source.split(" ")[0].rstrip(",")
            assert name.startswith("research/") and (REPO_ROOT / name).is_file(), (key, source)


def test_a_basis_that_rests_on_a_copy_says_so(register):
    assert "OCR text" in register["E26"].basis and "OCR" in register["E10"].basis
    assert "secondary pages" in register["E35"].basis and "not peer-reviewed" in register["E36"].basis
    assert not register["E35"].verified and not register["E05"].verified and register["E07"].verified


def test_verdicts_are_the_register(led, register):
    decided = evidence.verdicts(led)
    assert decided == {key: (entry.status, entry.basis) for key, entry in register.items()}
    assert not set(decided) & set(screening.RULES) and not set(decided) & set(premises.RULES)


# --- What the loader refuses -----------------------------------------------------------------


def entries() -> list[dict]:
    return yaml.safe_load(evidence.EVIDENCE_FILE.read_text())


def write(tmp_path, rows):
    path = tmp_path / "evidence.yaml"
    path.write_text(yaml.safe_dump(rows, allow_unicode=True, sort_keys=False))
    return path


def changed(key, **fields) -> list[dict]:
    rows = copy.deepcopy(entries())
    next(row for row in rows if row["id"] == key).update(fields)
    return rows


def test_a_written_copy_of_the_register_loads_back(tmp_path, register):
    assert evidence.load_evidence(write(tmp_path, entries())) == register


def without_key(key, field):
    rows = copy.deepcopy(entries())
    del next(row for row in rows if row["id"] == key)[field]
    return rows


REFUSED = [
    (lambda: changed("E26", note="x"), "evidence.yaml: E26: unknown key 'note'"),
    (lambda: changed("E26", id="E99"), "evidence.yaml: E99: not a claim id"),
    (lambda: changed("E26", id="S20"), "evidence.yaml: S20: not a claim this register decides"),
    (lambda: changed("E26", id="E11"), "evidence.yaml: E11: not a claim this register decides"),
    (lambda: changed("E26", status="pending"), "evidence.yaml: E26: status must be one of"),
    (lambda: changed("E26", status="supported"), "evidence.yaml: E26: status must be one of"),
    (lambda: changed("E26", status="not_testable"), "evidence.yaml: E26: not_testable is for the claims"),
    (lambda: changed("E40", status="fail"), "evidence.yaml: E40: not_testable is for the claims"),
    (lambda: changed("S26", status="fail"), "evidence.yaml: S26: the criterion holds this claim undefined"),
    (lambda: changed("E26", basis="The letter lists them."), "evidence.yaml: E26: basis must open with one of"),
    (lambda: changed("E26", basis="Supported: 1978 — yes."), "evidence.yaml: E26: basis must be plain prose"),
    (lambda: changed("E26", sources=[]), "evidence.yaml: E26: sources must name at least one section"),
    (lambda: changed("E26", sources=["Dunn 1998"]), "evidence.yaml: E26: sources must name at least one section"),
    (lambda: changed("E26", sources="research/06"), "evidence.yaml: E26: sources must be a list"),
    (lambda: changed("E26", verified="yes"), "evidence.yaml: E26: verified must be true or false"),
    (lambda: without_key("E26", "verified"), "evidence.yaml: E26: missing verified"),
    (lambda: without_key("E26", "basis"), "evidence.yaml: E26: missing basis"),
    (lambda: [row for row in entries() if row["id"] not in ("E26", "E40")], "evidence.yaml: missing E26, E40"),
    (lambda: entries() + [entries()[0]], "evidence.yaml: duplicate id: S02"),
    (lambda: {"E26": "pass"}, "evidence.yaml: must be a YAML list of mappings"),
]


@pytest.mark.parametrize(("rows", "message"), REFUSED)
def test_the_loader_names_the_entry_it_refuses(tmp_path, led, rows, message):
    with pytest.raises(LedgerError) as error:
        evidence.load_evidence(write(tmp_path, rows()), set(led.claims))
    assert message in str(error.value)


# --- The command and the merge ---------------------------------------------------------------


def test_main_writes_the_verdicts_and_where_each_was_read(tmp_path, led, register):
    evidence.main(root=tmp_path)
    results, decided, manifest = simkit.read_results("evidence", tmp_path)
    assert results == {} and decided == evidence.verdicts(led)
    assert manifest["ledger"] == led.digest and manifest["assumptions"] == evidence.ASSUMPTIONS
    assert manifest["register"]["E26"] == {"sources": list(register["E26"].sources), "verified": True}
    assert len(manifest["register_sha256"]) == 64


def test_premises_and_evidence_merge_with_tier_0_without_overruling_it(tmp_path, led):
    premises.main(root=tmp_path)
    evidence.main(root=tmp_path)
    results, decided, source = verdicts.merged(led, tmp_path)
    assert {claim for claim, package in source.items() if package == "premises"} == set(premises.RULES)
    assert {claim for claim, package in source.items() if package == "evidence"} == set(evidence.CLAIMS)
    tier0 = screening.verdicts(led, screening.all_results(led))
    assert all(decided[claim] == tier0[claim] for claim in screening.RULES)
    # 49 claims were pending after Tier 0; these two packages decide 33 of them and leave no word "pending" behind.
    assert sum(status == "pending" for status, _ in tier0.values()) == 49
    assert sum(status == "pending" for status, _ in decided.values()) == 49 - 33
    assert all(decided[claim][0] != "pending" for claim in (*premises.RULES, *evidence.CLAIMS))
    assert set(premises.results(led)) <= set(results)
