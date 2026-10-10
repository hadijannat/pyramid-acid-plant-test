"""Load and validate the ledger: ledger/parameters.yaml and ledger/claims.yaml."""
import math
from dataclasses import dataclass, fields
from hashlib import sha256
from pathlib import Path

import yaml

from pyramid import REPO_ROOT

STATUSES: tuple[str, ...] = ("pass", "fail", "conditional", "undefined", "pending")

UNITS: frozenset[str] = frozenset({
    # dimensionless, angle, sound level
    "1", "deg", "dB", "dB/m",
    # length, area, volume, time, rates
    "m", "m2", "m3", "s", "Hz", "m/s", "m2/s", "m3/s", "1/m3", "1/m2/yr",
    # mechanics and heat
    "kg", "kg/m3", "kg/mol", "N", "Pa", "Pa s", "Pa s/m", "J", "W", "W/m2", "K", "J/K", "J/kg/K",
    # chemistry
    "mol", "mol/m3", "mol/kg", "J/mol", "J/mol/K", "m3/mol", "m3/mol/s", "m6/s", "m6/s/K",
    "mol/m3/Pa", "mol2/m6/Pa",
    # electricity
    "A", "V", "V/m", "ohm m", "S/m", "F/m", "H/m", "C/N", "C/m2",
})


class LedgerError(ValueError):
    """A ledger file breaks a rule, or code asked for a quantity that is not in it."""


@dataclass(frozen=True)
class Quantity:
    id: str
    value: float
    unit: str
    low: float
    high: float
    source: str
    verified: bool
    note: str = ""


@dataclass(frozen=True)
class Claim:
    id: str
    statement: str
    subsystem: str
    timestamp: str
    tier: int
    piece: int
    criterion: str
    status: str
    depends_on: tuple[str, ...]
    spaces: tuple[str, ...] = ()


@dataclass(frozen=True)
class Ledger:
    quantities: dict[str, Quantity]
    claims: dict[str, Claim]
    digest: str

    def _quantity(self, id: str) -> Quantity:
        if id not in self.quantities:
            raise LedgerError(f"unknown quantity: {id}")
        return self.quantities[id]

    def q(self, id: str) -> float:
        return self._quantity(id).value

    def rng(self, id: str) -> tuple[float, float]:
        quantity = self._quantity(id)
        return quantity.low, quantity.high


_ABSENT = object()


def _is_text(value) -> bool:
    return isinstance(value, str)


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_integer(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_boolean(value) -> bool:
    return isinstance(value, bool)


def _is_text_list(value) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _get(entry: dict, key: str, where: str, check, what: str, default=_ABSENT):
    """entry[key], or default if the key is absent; LedgerError if required and absent, or of the wrong type."""
    if key not in entry:
        if default is _ABSENT:
            raise LedgerError(f"{where}: missing {key}")
        return default
    if not check(entry[key]):
        raise LedgerError(f"{where}: {key} must be {what}")
    return entry[key]


def _known_keys(entry: dict, where: str, kind: type) -> None:
    """LedgerError if the entry has a key that is no field of `kind`: a misspelt key must not read as an absent one."""
    unknown = [repr(key) for key in entry if key not in {field.name for field in fields(kind)}]
    if unknown:
        raise LedgerError(f"{where}: unknown key {', '.join(unknown)}")


def _number(entry: dict, key: str, where: str, default=_ABSENT) -> float:
    """entry[key] as a finite number. Text that Python reads as a number, but YAML does not, gets the form to write."""
    raw = entry.get(key)
    try:
        looks_numeric = isinstance(raw, str) and math.isfinite(float(raw))
    except ValueError:
        looks_numeric = False
    if looks_numeric:  # PyYAML reads 1e-3 and 1.0e5 as text
        mantissa, e, exponent = raw.strip().lower().partition("e")
        mantissa += "" if "." in mantissa else ".0"
        exponent = ("+" if exponent[:1].isdigit() else "") + exponent
        raise LedgerError(
            f"{where}: {key} must be a number; write {mantissa}{e}{exponent}: "
            "YAML needs a decimal point and a signed exponent"
        )
    number = float(_get(entry, key, where, _is_number, "a number", default))
    if not math.isfinite(number):
        raise LedgerError(f"{where}: {key} must be finite")
    return number


def _entries(raw: bytes, name: str) -> list[dict]:
    """The items of one ledger file, which must be a YAML list of mappings."""
    try:
        entries = yaml.safe_load(raw)
    except yaml.YAMLError as error:
        raise LedgerError(f"{name}: not valid YAML: {error}") from error
    if not isinstance(entries, list) or not all(isinstance(entry, dict) for entry in entries):
        raise LedgerError(f"{name}: must be a YAML list of mappings")
    return entries


def _load_quantities(raw: bytes) -> dict[str, Quantity]:
    quantities: dict[str, Quantity] = {}
    for number, entry in enumerate(_entries(raw, "parameters.yaml"), start=1):
        key = _get(entry, "id", f"parameters.yaml entry {number}", _is_text, "text")
        if key in quantities:
            raise LedgerError(f"duplicate id: {key}")
        _known_keys(entry, key, Quantity)
        source = _get(entry, "source", key, _is_text, "text").strip()
        if not source:
            raise LedgerError(f"{key}: missing source")
        unit = _get(entry, "unit", key, _is_text, "text")
        if unit not in UNITS:
            raise LedgerError(f"{key}: unknown unit {unit!r}")
        value = _number(entry, "value", key)
        low = _number(entry, "low", key, value)
        high = _number(entry, "high", key, value)
        if not low <= value <= high:
            raise LedgerError(f"{key}: value {value} outside its range {low} to {high}")
        quantities[key] = Quantity(
            id=key,
            value=value,
            unit=unit,
            low=low,
            high=high,
            source=source,
            verified=_get(entry, "verified", key, _is_boolean, "true or false"),
            note=_get(entry, "note", key, _is_text, "text", ""),
        )
    return quantities


def _load_claims(raw: bytes, quantities: dict[str, Quantity]) -> dict[str, Claim]:
    claims: dict[str, Claim] = {}
    for number, entry in enumerate(_entries(raw, "claims.yaml"), start=1):
        key = _get(entry, "id", f"claims.yaml entry {number}", _is_text, "text")
        if key in claims:
            raise LedgerError(f"duplicate id: {key}")
        _known_keys(entry, key, Claim)
        status = _get(entry, "status", key, _is_text, "text")
        if status not in STATUSES:
            raise LedgerError(f"{key}: unknown status {status!r}")
        tier = _get(entry, "tier", key, _is_integer, "an integer")
        if tier not in (0, 1, 2):
            raise LedgerError(f"{key}: tier must be 0, 1 or 2")
        piece = _get(entry, "piece", key, _is_integer, "an integer")
        if piece not in (1, 2, 3, 4, 5, 6):
            raise LedgerError(f"{key}: piece must be 1 to 6")
        depends_on = _get(entry, "depends_on", key, _is_text_list, "a list of quantity ids")
        for dependency in depends_on:
            if dependency not in quantities:
                raise LedgerError(f"{key}: depends on unknown quantity: {dependency}")
        claims[key] = Claim(
            id=key,
            statement=_get(entry, "statement", key, _is_text, "text"),
            subsystem=_get(entry, "subsystem", key, _is_text, "text"),
            timestamp=_get(entry, "timestamp", key, _is_text, "text"),
            tier=tier,
            piece=piece,
            criterion=_get(entry, "criterion", key, _is_text, "text"),
            status=status,
            depends_on=tuple(depends_on),
            spaces=tuple(_get(entry, "spaces", key, _is_text_list, "a list of space names", [])),
        )
    return claims


def load(root: Path | None = None) -> Ledger:
    root = root or REPO_ROOT / "ledger"
    parameter_bytes = (root / "parameters.yaml").read_bytes()
    claim_bytes = (root / "claims.yaml").read_bytes()
    quantities = _load_quantities(parameter_bytes)
    claims = _load_claims(claim_bytes, quantities)
    return Ledger(quantities, claims, sha256(parameter_bytes + claim_bytes).hexdigest())
