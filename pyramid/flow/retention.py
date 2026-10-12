"""Retention: how long sulfur dioxide stays in the King's Chamber with its two shafts open (S03).

Two ways out by the shafts are modelled. Molecular diffusion up them, with the chamber well mixed. And a through-flow
from one face to the other, driven by the wind's pressure difference between the two outlets against the shafts'
friction; because the shafts rise from the chamber and the gas is denser than air, that flow must first lift the
chamber's gas up the leeward shaft, a head the wind has to exceed before anything moves.

The same weight carries the gas out of any opening at the chamber's floor that is not under water, with air coming
down the shafts in its place. The chamber is closed above the shaft mouths, so the mouths hold the pressure at
their level and only the gas below them presses on the floor opening. drain_half_time() estimates that for the
antechamber path; the floor inlet by which S03 has the gas arrive is taken as closed, which the hypothesis does not
say.
"""
import math

import numpy as np

from pyramid.flow.hydraulics import SO2_IDS, so2_density
from pyramid.flow.network import SHAFT_IDS, quantity
from pyramid.screening import G

_TUBES = ("kcs.north.width", "kcs.north.height", "kcs.north.length", "kcs.south.width", "kcs.south.height",
          "kcs.south.length")


def tube_time_constant(volume: float, tubes, diffusivity: float, cells: int = 100) -> float:
    """Time constant of a well-mixed volume losing a gas by diffusion along tubes to clean air: s.

    tubes: (length, area) each. The chamber concentration and `cells` values along each tube obey
    dc/dt = M c; the slowest decay rate of M is returned as a time. With thin tubes it tends to V / (D sum(A / L)).
    """
    size = 1 + cells * len(tubes)
    matrix = np.zeros((size, size))
    for number, (length, area) in enumerate(tubes):
        dx = length / cells
        first = 1 + number * cells
        chamber_link = diffusivity * area / (dx / 2)  # from the chamber to the middle of the first cell, m3/s
        matrix[0, 0] -= chamber_link / volume
        matrix[0, first] += chamber_link / volume
        matrix[first, 0] += chamber_link / (area * dx)
        matrix[first, first] -= chamber_link / (area * dx)
        for cell in range(first, first + cells):
            # to the next cell, or from the middle of the last cell to the clean air at the outlet
            last = cell == first + cells - 1
            link = diffusivity / dx**2 * (2 if last else 1)
            matrix[cell, cell] -= link
            if not last:
                matrix[cell, cell + 1] += link
                matrix[cell + 1, cell] += link
                matrix[cell + 1, cell + 1] -= link
    return -1 / max(np.linalg.eigvals(matrix).real)


def diffusion_time_constant(q) -> float:
    """V / (D sum(A / L)) for the King's Chamber and its two shafts: s."""
    conductance = sum(q[f"kcs.{side}.width"] * q[f"kcs.{side}.height"] / q[f"kcs.{side}.length"]
                      for side in ("north", "south"))
    return q["kc.volume"] / (q["flow.so2_diffusivity"] * conductance)


_HEAD = ("hydro.air_density", "kcs.exit.z", "kc.floor.z", "kcs.mouth_height") + SO2_IDS


def dense_gas_head(q) -> float:
    """Pressure to lift pure sulfur dioxide from the shaft mouths to the outlets, less the air it displaces: Pa."""
    rise = q["kcs.exit.z"] - q["kc.floor.z"] - q["kcs.mouth_height"]
    return (so2_density(q) - q["hydro.air_density"]) * G * rise


def flush_wind_speed(q, fraction: float = 1.0) -> float:
    """Wind speed above which the wind's pressure difference exceeds the head of a charge of this fraction: m/s."""
    wind_per_speed_squared = q["flow.wind_pressure_coefficient_difference"] * q["hydro.air_density"] / 2
    return math.sqrt(fraction * dense_gas_head(q) / wind_per_speed_squared)


def half_time(q, wind: float | None = None, fraction: float = 1.0) -> float:
    """Time for half of a well-mixed charge to leave the chamber: s.

    With y the share of the charge still there, dy/dt = -y (Q(y) / V + 1 / tau_diffusion), where the through-flow
    obeys S Q^2 = dp_wind - B y: the wind's pressure difference less the head B y of the thinning gas, against
    the friction S of both shafts in series. While B y exceeds dp_wind nothing flows and only diffusion acts.
    """
    wind = q["flow.wind_speed"] if wind is None else wind
    air = q["hydro.air_density"]
    drive = q["flow.wind_pressure_coefficient_difference"] * air * wind**2 / 2
    head = fraction * dense_gas_head(q)
    slow = diffusion_time_constant(q)
    if drive <= head / 2:
        return slow * math.log(2)  # the wind cannot lift even the half-thinned gas
    # ponytail: air density in the friction term, though the leeward shaft carries the denser mixture; this
    # overstates the flow, and so understates the time, by at most sqrt(2.2). Carry the mixture density if needed.
    friction = air / 2 * (q["hydro.kcs_north_loss_coefficient"] / (q["kcs.north.width"] * q["kcs.north.height"]) ** 2
                          + q["hydro.kcs_south_loss_coefficient"] / (q["kcs.south.width"] * q["kcs.south.height"]) ** 2)
    scale = q["kc.volume"] * math.sqrt(friction / drive)  # V / Q with nothing to lift
    if head == 0:
        return math.log(2) / (1 / slow + 1 / scale)
    start = min(1.0, drive / head)  # the share at which the flow starts; diffusion alone thins the gas to it
    # integral of dy / (y sqrt(drive - head y)) from 1/2 to start, times V sqrt(S)
    flushing = 2 * scale * (math.atanh(math.sqrt(1 - head / (2 * drive)))
                            - math.atanh(math.sqrt(max(0.0, 1 - head * start / drive))))
    return min(slow * math.log(2), slow * math.log(1 / start) + flushing)


DRAIN_IDS = ("kc.length", "kc.width", "kc.height", "kcs.mouth_height", "flow.discharge_coefficient",
             "hydro.air_density") + SO2_IDS


def drain_half_time(q, area: float) -> float:
    """Time for half of a chamber of pure sulfur dioxide to run out through an opening at its floor: s.

    The gas leaves by its own weight, air coming down the shafts in its place. The chamber is closed above the
    shaft mouths, where that air comes in, so the head over the floor opening is that of the gas below the mouths,
    (rho_so2 - rho_air) g h_mouth, and stays so while the charge stands above them, as it still does with half of
    it gone: Q = Cd a sqrt(2 head / rho_so2) and t = V / (2 Q). A shut opening lets nothing out.
    """
    # ponytail: an unmixed layer over an opening with air beyond it, an estimate to a factor of about two. The
    # shafts' own loss is left out; it adds about 6 percent (73 minutes for 69). If the incoming air stirs the
    # charge the outflow thins as it goes; model the exchange flow if the minutes matter.
    if area <= 0:
        return math.inf
    dense = so2_density(q)
    head = (dense - q["hydro.air_density"]) * G * q["kcs.mouth_height"]
    rate = q["flow.discharge_coefficient"] * area * math.sqrt(2 * head / dense)
    return q["kc.length"] * q["kc.width"] * q["kc.height"] / 2 / rate


@quantity(
    "so2_density_ratio",
    "Density of sulfur dioxide against air",
    "1",
    "ratio = (p M / (R T)) / rho_air",
    SO2_IDS + ("hydro.air_density",),
)
def so2_density_ratio(q):
    return so2_density(q) / q["hydro.air_density"]


@quantity(
    "dense_gas_head",
    "Pressure difference needed to lift pure sulfur dioxide up a King's Chamber shaft to its outlet",
    "Pa",
    "B = (rho_so2 - rho_air) g (z_outlet - z_kc_floor - h_mouth)",
    _HEAD,
)
def dense_gas_head_result(q):
    return dense_gas_head(q)


@quantity(
    "flush_wind_speed",
    "Wind speed below which no through-flow can lift a chamber of pure sulfur dioxide out",
    "m/s",
    "U = sqrt(2 B / (dCp rho_air))",
    _HEAD + ("flow.wind_pressure_coefficient_difference",),
)
def flush_wind_speed_result(q):
    return flush_wind_speed(q)


@quantity(
    "diffusion_half_time",
    "Time for half the sulfur dioxide to leave the King's Chamber by diffusion up its two shafts",
    "s",
    "t = ln(2) V_kc / (D (A_n / L_n + A_s / L_s))",
    ("kc.volume", "flow.so2_diffusivity") + _TUBES,
)
def diffusion_half_time(q):
    return diffusion_time_constant(q) * math.log(2)


@quantity(
    "retention_half_time",
    "Time for half of a chamber of pure sulfur dioxide to leave by diffusion and wind-driven through-flow",
    "s",
    "dy/dt = -y (Q / V_kc + 1 / tau); S Q^2 = dCp rho_air U^2 / 2 - B y; S = (rho_air / 2) (K_n / A_n^2 + K_s / A_s^2)",
    tuple(dict.fromkeys(("kc.volume", "flow.so2_diffusivity", "flow.wind_speed",
                         "flow.wind_pressure_coefficient_difference") + _TUBES + _HEAD + SHAFT_IDS)),
)
def retention_half_time(q):
    return half_time(q)
