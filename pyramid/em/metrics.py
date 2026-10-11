"""Spectra, chamber and summit metrics, the gates of the foundation spec's section 6, and the rules for E19 and E20.

Every function here takes plain numbers, so the gates and the rules are tested on made-up values.

Readings of the spec, each a judgement call: "the R1 peak extinction" of the convergence gate is the band
maximum; the normalised root-mean-square difference of two spectra is the RMS of their difference over the RMS
of their mean; a free-space peak of the study is matched to the nearest local maximum of the computed spectrum;
E19 has two parts and the spec gives no rule for joining them, so the claim fails when the realism part fails,
passes when both parts pass, and is conditional otherwise.
"""
import numpy as np

BENCHMARK = 0.02       # B0 against Mie, across the band (spec section 6)
CONVERGENCE = 0.03     # change of the R1 peak extinction on halving the cell
PEAK_FREE = 0.05       # free-space peak wavelengths
PEAK_GROUND = 0.10     # the on-ground maximum's wavelength
PEAK_VALUE = 0.20      # peak cross-sections against the values read from the study's figures
AGREEMENT = 0.10       # the two solvers' spectra, normalised RMS difference
FACTOR = 2.0           # "at least twice its control", "at least 2", "at least twice the pointed apex"


def region_stats(intensity: np.ndarray, weights: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Volume mean and maximum of |E|^2 / |E0|^2 over a region, per wavelength.

    intensity is (wavelengths, *box); weights is the fraction of each cell of the box that is the region. The
    maximum is taken over the cells at least half in the region (over the fullest cells if none is).
    """
    flat, w = intensity.reshape(len(intensity), -1), weights.ravel().astype(float)
    inside = w >= min(0.5, w.max()) - 1e-6
    return flat @ w / w.sum(), flat[:, inside].max(axis=1)


def side_intensity(field: np.ndarray, normal: np.ndarray, factor) -> np.ndarray:
    """|E|^2 on one side of the surface in every cell, from the cell's mean field (3, ...).

    In a cell cut by a surface the field along the surface is the same on both sides, and the field across it is
    `factor` times its mean: 1 / (mean inverse permittivity) on the air side, that over the material's permittivity
    on the material's side. In an uncut cell the factor is 1 or the normal is zero, and the field is unchanged.
    """
    across = np.sum(normal * field, axis=0)
    return np.sum(np.abs(field + (factor - 1) * across * normal) ** 2, axis=0)


def peaks(wavelengths, spectrum) -> list[tuple[float, float]]:
    """Local maxima of a spectrum as (wavelength, value), each refined with a parabola through three points."""
    x, y = np.asarray(wavelengths, float), np.asarray(spectrum, float)
    found = []
    for i in range(1, len(y) - 1):
        if y[i] >= y[i - 1] and y[i] > y[i + 1]:
            curve = y[i - 1] - 2 * y[i] + y[i + 1]
            shift = 0.5 * (y[i - 1] - y[i + 1]) / curve
            found.append((x[i] + shift * (x[i + 1] - x[i]), y[i] - 0.25 * (y[i - 1] - y[i + 1]) * shift))
    return found


def band_maximum(wavelengths, spectrum) -> tuple[float, float]:
    """(wavelength, value) of the largest value in the band: the highest local maximum, or an end of the band."""
    i = int(np.argmax(spectrum))
    inner = [p for p in peaks(wavelengths, spectrum) if abs(p[0] - wavelengths[i]) <= abs(wavelengths[1] - wavelengths[0])]
    return inner[0] if inner else (float(wavelengths[i]), float(spectrum[i]))


def nrmsd(a, b) -> float:
    """Normalised root-mean-square difference of two spectra on the same wavelengths."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.sqrt(np.mean((a - b) ** 2)) / np.sqrt(np.mean(((a + b) / 2) ** 2)))


def interpolate_loss(values, losses, target: float) -> np.ndarray:
    """Per wavelength, the value at an imaginary permittivity `target`, linear between the two runs that bracket it.

    values is (runs, wavelengths, ...), losses (runs, wavelengths): the imaginary permittivity each run had there.
    A time-domain run has one conductivity, so its imaginary permittivity grows with the wavelength; runs matched
    at different wavelengths bracket the study's constant value everywhere in the band.
    """
    values, losses = np.asarray(values, float), np.asarray(losses, float)
    out = np.empty(values.shape[1:])
    for j in range(values.shape[1]):
        order = np.argsort(losses[:, j])
        x = losses[order, j]
        if len(x) < 2 or not x[0] - 1e-12 <= target <= x[-1] + 1e-12:
            raise ValueError("the runs do not bracket the target loss")
        k = int(np.clip(np.searchsorted(x, target), 1, len(x) - 1))
        t = (target - x[k - 1]) / (x[k] - x[k - 1])
        out[j] = values[order[k - 1], j] + t * (values[order[k], j] - values[order[k - 1], j])
    return out


# --- the gates ----------------------------------------------------------------------------------------------

def benchmark_gate(exact, by_solver: dict) -> dict:
    """B0 within 2 percent of the Mie extinction at every wavelength of the band, in both solvers."""
    worst = {solver: float(np.max(np.abs(np.asarray(ext) / np.asarray(exact) - 1))) for solver, ext in by_solver.items()}
    return {"gate": "benchmark: B0 against Mie", "passed": all(w <= BENCHMARK for w in worst.values()),
            "numbers": "; ".join(f"{solver} worst deviation {w:.2%}" for solver, w in worst.items())
                       + f" (limit {BENCHMARK:.0%})"}


def convergence_gate(by_solver: dict) -> dict:
    """Halving the cell changes the R1 peak extinction by less than 3 percent. by_solver: {solver: (coarse, half)}."""
    change = {solver: abs(fine / coarse - 1) for solver, (coarse, fine) in by_solver.items()}
    return {"gate": "convergence: R1 peak extinction on halving the cell",
            "passed": all(c < CONVERGENCE for c in change.values()),
            "numbers": "; ".join(f"{solver} {by_solver[solver][0] / 1e6:.4f} to {by_solver[solver][1] / 1e6:.4f} km2 "
                                 f"({change[solver]:.2%})" for solver in by_solver) + f" (limit {CONVERGENCE:.0%})"}


def match_peak(found: list, wavelength: float) -> tuple[float, float] | None:
    """The local maximum nearest a wavelength, or None if the spectrum has none."""
    return min(found, key=lambda p: abs(p[0] - wavelength)) if found else None


def reproduction_gate(free: dict, ground: tuple | None, targets: dict, agreement: dict) -> list[dict]:
    """The spec's reproduction criteria.

    free: {solver: local maxima of the R1 extinction}; ground: the band maximum of R3 (wavelength, value);
    targets: {"peak1": (wavelength, value), "peak2": ..., "ground": ...} read from the study;
    agreement: {case: normalised RMS difference of the two solvers}.
    """
    gates = []
    for key in ("peak1", "peak2"):
        at, value = targets[key]
        ok, parts = True, []
        for solver, found in free.items():
            hit = match_peak(found, at)
            if hit is None:
                ok = False
                parts.append(f"{solver} has no local maximum")
                continue
            ok &= abs(hit[0] / at - 1) <= PEAK_FREE and abs(hit[1] / value - 1) <= PEAK_VALUE
            parts.append(f"{solver} {hit[0]:.0f} m ({hit[0] / at - 1:+.1%}), {hit[1] / 1e6:.3f} km2 ({hit[1] / value - 1:+.1%})")
        gates.append({"gate": f"reproduction: free-space peak near {at:.0f} m, {value / 1e6:.2f} km2", "passed": bool(ok),
                      "numbers": "; ".join(parts) + f" (limits {PEAK_FREE:.0%} and {PEAK_VALUE:.0%})"})
    at, value = targets["ground"]
    if ground is None:
        gates.append({"gate": "reproduction: on-ground maximum", "passed": False, "numbers": "not computed"})
    else:
        ok = abs(ground[0] / at - 1) <= PEAK_GROUND and abs(ground[1] / value - 1) <= PEAK_VALUE
        gates.append({"gate": f"reproduction: on-ground maximum near {at:.0f} m, {value / 1e6:.2f} km2", "passed": bool(ok),
                      "numbers": f"fdtd {ground[0]:.0f} m ({ground[0] / at - 1:+.1%}), {ground[1] / 1e6:.3f} km2 "
                                 f"({ground[1] / value - 1:+.1%}) (limits {PEAK_GROUND:.0%} and {PEAK_VALUE:.0%})"})
    gates.append({"gate": "reproduction: the two solvers' extinction spectra agree",
                  "passed": bool(agreement) and all(v <= AGREEMENT for v in agreement.values()),
                  "numbers": "; ".join(f"{case} {v:.2%}" for case, v in agreement.items()) + f" (limit {AGREEMENT:.0%})"})
    return gates


# --- the rules ----------------------------------------------------------------------------------------------

def _agree(statuses: list[str]) -> str:
    """One status if every cell size gives it; conditional if the cell sizes fall on different sides."""
    return statuses[0] if len(set(statuses)) == 1 else "conditional"


def crossing(rows: list[tuple[float, float]], level: float = FACTOR) -> float | None:
    """The conductivity at which a ratio falls through `level`, log-linear between the runs that bracket it."""
    rows = sorted(rows)
    for (s0, r0), (s1, r1) in zip(rows, rows[1:]):
        if r0 >= level > r1:
            t = (np.log(r0) - np.log(level)) / (np.log(r0) - np.log(r1))
            return float(np.exp(np.log(s0) + t * (np.log(s1) - np.log(s0))))
    return None


def e19(modelled: list[tuple], realism: list[tuple]) -> tuple[str, str]:
    """E19 from the band-maximum volume-mean ratios in the King's Chamber.

    modelled: one (cell, R1, its control) per cell size.
    realism: one (cell, rows) per cell size, rows being (label, conductivity, V4, its control or None).
    """
    part_a = _agree(["pass" if r1 >= FACTOR * c0 else "fail" for _, r1, c0 in modelled])
    part_b = []
    for _, rows in realism:
        lowest = min(sigma for _, sigma, _, _ in rows)
        if all(v4 < FACTOR for _, sigma, v4, _ in rows if sigma == lowest):
            part_b.append("fail")
        elif all(c0 is not None and v4 >= FACTOR and v4 >= FACTOR * c0 for _, _, v4, c0 in rows):
            part_b.append("pass")
        else:
            part_b.append("conditional")
    part_b = _agree(part_b)
    status = "fail" if part_b == "fail" else "pass" if part_a == part_b == "pass" else "conditional"

    said_a = "; ".join(f"{r1:.2f} against {c0:.2f} in its control cube ({r1 / c0:.2f} times) at a {cell:.3g} m cell"
                       for cell, r1, c0 in modelled)
    said_b = "; ".join(
        f"at a {cell:.3g} m cell " + ", ".join(
            f"{v4:.2g} at {sigma:.1e} S/m{'' if not label else ' (' + label + ')'}"
            + ("" if c0 is None else f" against {c0:.2g} in its control") for label, sigma, v4, c0 in rows)
        for cell, rows in realism)
    drop = [crossing([(sigma, v4) for label, sigma, v4, _ in rows if not label]) for _, rows in realism]
    said_drop = "".join(f" It drops below {FACTOR:g} at about {d:.1e} S/m." for d in drop[:1] if d is not None)
    basis = (f"As modelled ({part_a}): the band-maximum volume-mean intensity ratio in the King's Chamber of case R1 is "
             f"{said_a}; the criterion asks for at least {FACTOR:g} times the control. Under realism ({part_b}): in case "
             f"V4 the ratio is {said_b}; the criterion asks for at least {FACTOR:g} and at least {FACTOR:g} times the "
             f"control across the measured conductivity range, and fails the claim if the ratio is below {FACTOR:g} at "
             f"the low end of that range.{said_drop} The spec gives no rule for joining the two parts: the claim fails "
             f"when the realism part fails, passes when both pass, and is conditional otherwise.")
    return status, basis


def e20(summit: list[tuple]) -> tuple[str, str]:
    """E20 from the band-maximum summit metric on ground: one (cell, truncated, pointed, the study's apex) per cell size."""
    status = _agree(["pass" if cut >= FACTOR * whole else "fail" for _, cut, whole, _ in summit])
    said = "; ".join(f"{cut:.2f} for the apex cut at the present top against {whole:.2f} for the pointed apex "
                     f"({cut / whole:.2f} times; {study:.2f} for the study's apex) at a {cell:.3g} m cell"
                     for cell, cut, whole, study in summit)
    basis = (f"On ground, with the wave from above, the band-maximum volume mean of the intensity ratio in the top "
             f"masonry is {said}. The criterion passes the claim only if the truncated apex gives at least {FACTOR:g} "
             f"times the pointed one"
             + (", and the two cell sizes fall on different sides of that." if status == "conditional" else "."))
    return status, basis
