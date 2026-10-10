"""Load and validate the ledger: ledger/parameters.yaml and ledger/claims.yaml."""
from dataclasses import dataclass
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


def load(root: Path | None = None) -> Ledger:
    root = root or REPO_ROOT / "ledger"
    parameter_bytes = (root / "parameters.yaml").read_bytes()
    claim_bytes = (root / "claims.yaml").read_bytes()

    quantities: dict[str, Quantity] = {}
    for entry in yaml.safe_load(parameter_bytes):
        key = entry["id"]
        if key in quantities:
            raise LedgerError(f"duplicate id: {key}")
        source = str(entry.get("source") or "").strip()
        if not source:
            raise LedgerError(f"{key}: missing source")
        if entry["unit"] not in UNITS:
            raise LedgerError(f"{key}: unknown unit {entry['unit']!r}")
        value = float(entry["value"])
        low = float(entry.get("low", value))
        high = float(entry.get("high", value))
        if not low <= value <= high:
            raise LedgerError(f"{key}: value {value} outside its range {low} to {high}")
        quantities[key] = Quantity(
            id=key,
            value=value,
            unit=entry["unit"],
            low=low,
            high=high,
            source=source,
            verified=bool(entry["verified"]),
            note=entry.get("note", ""),
        )

    claims: dict[str, Claim] = {}
    for entry in yaml.safe_load(claim_bytes):
        key = entry["id"]
        if key in claims:
            raise LedgerError(f"duplicate id: {key}")
        if entry["status"] not in STATUSES:
            raise LedgerError(f"{key}: unknown status {entry['status']!r}")
        if entry["tier"] not in (0, 1, 2):
            raise LedgerError(f"{key}: tier must be 0, 1 or 2")
        if entry["piece"] not in (1, 2, 3, 4, 5, 6):
            raise LedgerError(f"{key}: piece must be 1 to 6")
        for dependency in entry["depends_on"]:
            if dependency not in quantities:
                raise LedgerError(f"{key}: depends on unknown quantity: {dependency}")
        claims[key] = Claim(
            id=key,
            statement=entry["statement"],
            subsystem=entry["subsystem"],
            timestamp=entry["timestamp"],
            tier=entry["tier"],
            piece=entry["piece"],
            criterion=entry["criterion"],
            status=entry["status"],
            depends_on=tuple(entry["depends_on"]),
            spaces=tuple(entry.get("spaces", ())),
        )

    return Ledger(quantities, claims, sha256(parameter_bytes + claim_bytes).hexdigest())
