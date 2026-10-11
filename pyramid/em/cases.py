"""The case table of the foundation spec's section 6, as data built from the ledger.

The wave travels along the axis and is polarised along x (east), as in the study's Fig. 1; "down" is from the
apex side. Field ratios are |E|^2 over the incident |E|^2 (paper.incident_field), also over ground, where the
undisturbed field is a standing wave: the study normalises to the incident amplitude and so do we.

Assumptions (readings of the spec where it leaves a choice): V2 keeps the study's outer pyramid and changes
only the chambers; the pointed and truncated apexes of V3 are the surveyed pyramid (pyr.base_side,
pyr.height_original) whole and cut at pyr.height_present, with the study's chambers, so that only the apex
differs; V4 is that truncated pyramid with the surveyed chambers, a real permittivity of em.limestone_eps and
bedrock of the same material as the masonry; a control cube stands on the base plane, centred on the axis.
"""
from dataclasses import dataclass, replace

import numpy as np

from pyramid.em.shapes import body_volume

DOWN, UP = -1, +1
SOLVERS = ("dda", "fdtd")
STEP = 5.0     # m between the wavelengths of a spectrum: the 5 percent peak criterion at 230 m is 11.5 m


@dataclass(frozen=True)
class Case:
    name: str
    body: str                 # "sphere", "pyramid" or "cube"
    base: float               # sphere: radius; pyramid: base side; cube: side (m)
    height: float             # pyramid: where its faces meet (m)
    top: float                # pyramid: the level it is cut at; equal to height when pointed (m)
    chambers: str             # "none", "paper" or "survey"
    eps: float                # real relative permittivity of the masonry
    eps_imag: float | None    # the study's constant imaginary part; None when a conductivity is given
    sigma: float | None       # conductivity, S/m
    ground: bool              # a half-space of the masonry's material below z = 0
    direction: int            # DOWN or UP


def constants(q) -> tuple[float, float]:
    """(speed of light, impedance of free space) from the ledger's eps0 and mu0, so that they are consistent."""
    return 1 / np.sqrt(q("em.eps0") * q("em.mu0")), np.sqrt(q("em.mu0") / q("em.eps0"))


def wavelengths(q) -> np.ndarray:
    return np.arange(q("paper.wavelength_min"), q("paper.wavelength_max") + STEP / 2, STEP)


def loss(sigma: float, wavelength, q):
    """The imaginary permittivity a conductivity gives at a vacuum wavelength: sigma / (omega eps0)."""
    return sigma * np.asarray(wavelength) * constants(q)[1] / (2 * np.pi)


def conductivity(eps_imag: float, wavelength: float, q) -> float:
    """The conductivity that gives an imaginary permittivity at one wavelength."""
    return eps_imag * 2 * np.pi / (wavelength * constants(q)[1])


def measured_conductivities(ledger) -> tuple[float, float, float]:
    """The range measured in the pyramid's masonry (1 / em.limestone_resistivity) and its geometric middle."""
    resistivity_low, resistivity_high = ledger.rng("em.limestone_resistivity")
    low, high = 1 / resistivity_high, 1 / resistivity_low
    return low, float(np.sqrt(low * high)), high


def control(case: Case) -> Case:
    """C0: the case's chambers at the same heights in a cube of the body's volume."""
    return replace(case, name=f"C0.{case.name}", body="cube", base=body_volume(case) ** (1 / 3))


def table(ledger) -> dict[str, Case]:
    q = ledger.q
    study = dict(eps=q("paper.eps_real"), eps_imag=q("paper.eps_imag"), sigma=None)
    r1 = Case("R1", "pyramid", q("paper.base_side"), q("paper.height"), q("paper.height"), "paper",
              ground=False, direction=DOWN, **study)
    r3 = replace(r1, name="R3", ground=True)
    cases = [
        Case("B0", "sphere", q("emx.sphere_radius"), 0.0, 0.0, "none", ground=False, direction=DOWN, **study),
        r1, replace(r1, name="R2", direction=UP), r3, control(r1), control(r3),
        replace(r1, name="V2.R1", chambers="survey"), replace(r3, name="V2.R3", chambers="survey"),
    ]
    sweep = (q("emx.v1_conductivity_low"), q("emx.v1_conductivity_mid"), *measured_conductivities(ledger)[::2],
             q("emx.v1_conductivity_high"))
    for base in (r1, r3):
        for eps in (q("paper.eps_real"), q("em.limestone_eps"), q("em.limestone_eps_insitu")):
            for sigma in sweep:
                cases.append(replace(base, name=f"V1.{base.name}.eps{eps:g}.sig{sigma:.1e}", eps=eps, eps_imag=None,
                                     sigma=sigma))
    pointed = replace(r1, base=q("pyr.base_side"), height=q("pyr.height_original"), top=q("pyr.height_original"))
    truncated = replace(pointed, top=q("pyr.height_present"))
    for label, apex in (("pointed", pointed), ("truncated", truncated)):   # the study's own apex is R1, R2 and R3
        cases += [replace(apex, name=f"V3.{label}.down"), replace(apex, name=f"V3.{label}.up", direction=UP),
                  replace(apex, name=f"V3.{label}.ground", ground=True)]
    real = replace(truncated, chambers="survey", ground=True, eps_imag=None)
    for sigma in measured_conductivities(ledger):
        v4 = replace(real, name=f"V4.sig{sigma:.1e}", eps=q("em.limestone_eps"), sigma=sigma)
        cases += [v4, control(v4)]
    low = measured_conductivities(ledger)[0]
    for eps in ledger.rng("em.limestone_eps"):       # the ends of the permittivity range, at the favourable loss
        cases.append(replace(real, name=f"V4.eps{eps:g}.sig{low:.1e}", eps=eps, sigma=low))
    return {case.name: case for case in cases}
