"""Time domain: Maxwell's equations on a Yee grid, with absorbing layers and a plane wave over air and ground.

One run sends a short pulse that covers the whole band and keeps running Fourier sums at the band's wavelengths:
on two closed boxes (the scattered power outside the surface where the plane wave is injected, the absorbed
power inside it), in the chambers and the summit, and on the axial section. The incident field on the injection
surface is the exact solution of the same difference equations for the air and ground layers alone, stepped on a
one-dimensional grid beside the main one, so the region outside holds the scattered field only.

Units: E in V/m for a unit incident wave and H times the impedance of free space, so both are of order one.
Time dependence of the Fourier sums: exp(-i w t), as in the frequency-domain solver.

Assumptions: the wave travels along z and is polarised along x; a run has one conductivity, so its imaginary
permittivity grows with the wavelength (the study's constant value is recovered from three runs, see
metrics.interpolate_loss); a field component at a cut cell uses the mean permittivity for the part along the
surface and the mean inverse for the part across it, and the off-diagonal part of that tensor is dropped; the
conductivity across a surface is taken to first order in the loss tangent; the absorbing layers are graded for
air, also where they hold ground; the ground is the masonry's material and fills everything below z = 0.

Extinction is the scattered power through the outer box plus the power absorbed inside the inner box, over the
incident intensity in air. On ground the inner box is closed at z = 0, so it counts the loss in the body above
the ground, and the outer box runs through the ground, where a lossy ground weakens the scattered wave before it
is counted (a few percent at the study's loss).
"""
import time
from pathlib import Path

import numpy as np

from pyramid.em import metrics
from pyramid.em.cases import constants

COURANT = 0.99 / np.sqrt(3)          # time step over the cell's light-crossing time
LAYERS, GRADE = 10, 3                # cells of absorbing layer on each face, and the grading of its conductivity
ABSORB, INJECT, SCATTER, GAP = 2, 4, 6, 9   # cells from the body's grid to the two boxes, the injection surface, the layers
SAMPLES = 12                         # Fourier samples per period of the shortest wavelength
DECAY, PERIODS = 1e-3, 40            # stop when the field has fallen to this of its peak; never later than this many periods


def _sl(**kw):
    return tuple(kw.get(a, slice(None)) for a in "xyz")


def _range(axis: int, lo, hi):
    return {"xyz"[axis]: slice(lo, hi)}


class Run:
    """One broadband run. Build it, call advance() until it returns True, then results()."""

    def __init__(self, model, eps: float, sigma: float, eps_granite: float, sigma_granite: float, ground: bool,
                 direction: int, wavelengths, speed: float, impedance: float, dtype=np.float32, flux: bool = True,
                 layers: int = LAYERS):
        self.cell, self.direction, self.ground, self.dtype = model.cell, direction, ground, dtype
        self.wavelengths = np.asarray(wavelengths, float)
        self.materials = (eps, sigma, eps_granite, sigma_granite, impedance)
        pad = GAP + layers
        self.model = big = model.padded((pad,) * 3, (pad,) * 3, ground)
        self.n = n = big.masonry.shape
        d, s = self.cell, dtype(COURANT)
        self.dt = COURANT * d / speed
        self.omega = 2 * np.pi * speed / self.wavelengths
        inner = [(pad, pad + m) for m in model.masonry.shape]
        box = lambda out: [(lo - out, hi + out) for lo, hi in inner]            # noqa: E731
        self.inject, self.scatter, self.absorb = box(INJECT), box(SCATTER), box(ABSORB)
        self.k0 = int(round(-big.origin[2] / d))                               # the node plane z = 0
        if ground:
            self.absorb[2] = (self.k0, self.absorb[2][1])

        # --- materials at the field components ---
        fm = big.masonry.astype(float)
        fg = np.zeros_like(fm) if big.granite is None else big.granite.astype(float)
        mean = 1 - fm - fg + fm * eps + fg * eps_granite
        inverse = 1 - fm - fg + fm / eps + fg / eps_granite
        loss, loss_across = fm * sigma + fg * sigma_granite, fm * sigma / eps**2 + fg * sigma_granite / eps_granite**2
        gradient = np.gradient(mean)
        self.normal = big.mixing(eps, eps_granite)[2].astype(np.float32)
        self.ca, self.cb = [], []
        for c in range(3):
            a, b = (c + 1) % 3, (c + 2) % 3

            def edge(field):                 # the mean over the four cells that share an edge along c
                lo, hi = slice(None, -1), slice(1, None)
                return 0.25 * sum(field[_sl(**_range(a, p.start, p.stop), **_range(b, r.start, r.stop))]
                                  for p in (lo, hi) for r in (lo, hi))

            g = [edge(part) for part in gradient]
            size = g[0] ** 2 + g[1] ** 2 + g[2] ** 2
            across = np.where(size > 1e-18, g[c] ** 2 / np.where(size > 1e-18, size, 1.0), 0.0)
            m, inv = edge(mean), edge(inverse)
            stiff = across * inv + (1 - across) / m                              # 1 / permittivity of this component
            sig = (across * edge(loss_across) + (1 - across) * edge(loss) / m**2) / stiff**2
            x = sig * impedance * COURANT * d * stiff / 2
            self.ca.append(((1 - x) / (1 + x)).astype(dtype))
            self.cb.append((COURANT * stiff / (1 + x)).astype(dtype))
        del fm, fg, mean, inverse, loss, loss_across, gradient

        # --- fields: E_c has cells along c and nodes along the other two; H_c the other way round ---
        shape = lambda c, e: tuple(n[a] + (0 if (a == c) == e else 1) for a in range(3))   # noqa: E731
        self.e = [np.zeros(shape(c, True), dtype) for c in range(3)]
        self.h = [np.zeros(shape(c, False), dtype) for c in range(3)]
        self.work_e = [np.empty(tuple(m - 2 if a != c else m for a, m in enumerate(self.e[c].shape)), dtype) for c in range(3)]
        self.work_h = [np.empty(self.h[c].shape, dtype) for c in range(3)]

        # --- absorbing layers: one memory variable per derivative, face and component ---
        alpha = 0.1 * 2 * np.pi * d / self.wavelengths.max()        # shifts the layer's pole below the band
        self.layers = []
        for c in range(3):
            a, b = (c + 1) % 3, (c + 2) % 3
            for axis, other, src, sign in ((a, b, b, +1), (b, a, a, -1)):       # E_c += cb (d_a H_b - d_b H_a)
                for low in (True, False):
                    depth = (layers - 1 - np.arange(layers) if low else np.arange(layers)) / layers
                    node = slice(1, layers + 1) if low else slice(n[axis] - layers, n[axis])
                    self.layers.append(self._layer(
                        self.e[c], _sl(**_range(axis, node.start, node.stop), **_range(other, 1, -1)),
                        self.cb[c][_sl(**_range(axis, node.start - 1, node.stop - 1))], sign,
                        self.h[src], _sl(**_range(axis, node.start, node.stop), **_range(other, 1, -1)),
                        _sl(**_range(axis, node.start - 1, node.stop - 1), **_range(other, 1, -1)), axis, depth, alpha))
            for axis, src, sign in ((a, b, -1), (b, a, +1)):                    # H_c -= s (d_a E_b - d_b E_a)
                for low in (True, False):
                    depth = ((layers - 0.5 - np.arange(layers)) if low else (np.arange(layers) + 0.5)) / layers
                    half = slice(0, layers) if low else slice(n[axis] - layers, n[axis])
                    self.layers.append(self._layer(
                        self.h[c], _sl(**_range(axis, half.start, half.stop)), s, sign,
                        self.e[src], _sl(**_range(axis, half.start + 1, half.stop + 1)),
                        _sl(**_range(axis, half.start, half.stop)), axis, depth, alpha))
        self.layers_e = [layer for layer in self.layers if any(layer["target"] is f for f in self.e)]
        self.layers_h = [layer for layer in self.layers if any(layer["target"] is f for f in self.h)]

        # --- the plane wave: two one-dimensional grids along z, one with the ground and one without ---
        periods = self.wavelengths.max() / (COURANT * d)                       # steps in the longest period
        centre = speed * (1 / self.wavelengths.min() + 1 / self.wavelengths.max()) / 2
        self.tau = 1 / (2 * np.pi * 0.4 * centre)                              # edges of the band at 0.46 of the peak
        self.f0, self.t0 = centre, 5 * self.tau
        self.first = int((self.t0 + 5 * self.tau) / self.dt + n[2] / COURANT)  # the pulse has come and gone
        self.last = self.first + int(PERIODS * periods)
        self.extra = extra = int(self.last * COURANT / 2) + 20                 # no echo from the ends within the run
        nodes = n[2] + 1 + 2 * extra
        below = (np.arange(nodes + 1) - 0.5 - extra - self.k0) < 0             # cells around each node: is it ground?
        self.lines = []
        for with_ground in ((True, False) if ground else (False,)):
            eps_cell = np.where(below & with_ground, eps, 1.0)
            sig_cell = np.where(below & with_ground, sigma, 0.0)
            m, sig = (eps_cell[:-1] + eps_cell[1:]) / 2, (sig_cell[:-1] + sig_cell[1:]) / 2
            x = sig * impedance * COURANT * d / (2 * m)
            self.lines.append({"e": np.zeros(nodes), "h": np.zeros(nodes - 1), "ca": (1 - x) / (1 + x),
                               "cb": COURANT / m / (1 + x)})
        self.source = extra + (self.inject[2][1] + 3 if direction < 0 else self.inject[2][0] - 3)

        # --- Fourier sums ---
        self.stride = max(1, int(self.wavelengths.min() / (COURANT * d) / SAMPLES))
        self.step, self.peak, self.quiet = 0, 0.0, 0
        nw = len(self.wavelengths)
        self.sums = {"incident": np.zeros(nw, complex), "line_e": np.zeros((nw, n[2] + 1), complex),
                     "line_h": np.zeros((nw, n[2]), complex)}
        self.taps = []                                       # (key, field list, component, slices or a pair of them)
        self.boxes = {"scatter": self.scatter, "absorb": self.absorb} if flux else {}
        for name, limits in self.boxes.items():
            for u in range(3):
                a, b = (u + 1) % 3, (u + 2) % 3
                (a0, a1), (b0, b1) = limits[a], limits[b]
                for side, m in enumerate(limits[u]):
                    key = f"{name}.{u}.{side}"
                    plane = lambda lo, hi, p, q: _sl(**_range(u, lo, hi), **_range(a, *p), **_range(b, *q))   # noqa: E731
                    self._tap(key + ".ea", self.e, a, plane(m, m + 1, (a0, a1), (b0, b1 + 1)))
                    self._tap(key + ".eb", self.e, b, plane(m, m + 1, (a0, a1 + 1), (b0, b1)))
                    self._tap(key + ".hb", self.h, b, (plane(m - 1, m, (a0, a1), (b0, b1 + 1)), plane(m, m + 1, (a0, a1), (b0, b1 + 1))))
                    self._tap(key + ".ha", self.h, a, (plane(m - 1, m, (a0, a1 + 1), (b0, b1)), plane(m, m + 1, (a0, a1 + 1), (b0, b1))))
        middle = int(round(-big.origin[0] / d))
        (j0, j1), (k0, k1) = (self.inject[1][0] + 1, self.inject[1][1] - 1), (self.inject[2][0] + 1, self.inject[2][1] - 1)
        self.volumes = {"section": (slice(middle - 1, middle + 1), slice(j0, j1), slice(k0, k1))}
        self.volumes.update({name: slices for name, (slices, _) in big.regions.items()})
        for name, (si, sj, sk) in self.volumes.items():
            grow = lambda r: slice(r.start, r.stop + 1)                         # noqa: E731
            self._tap(f"{name}.x", self.e, 0, (si, grow(sj), grow(sk)))
            self._tap(f"{name}.y", self.e, 1, (grow(si), sj, grow(sk)))
            self._tap(f"{name}.z", self.e, 2, (grow(si), grow(sj), sk))

    def _layer(self, target, where, factor, sign, source, high, low, axis, depth, alpha):
        sigma = 0.8 * (GRADE + 1) * depth**GRADE                # conductivity times impedance times cell, graded
        decay = np.exp(-(sigma + alpha) * COURANT)
        gain = sigma / (sigma + alpha) * (decay - 1)
        shape = [1, 1, 1]
        shape[axis] = len(depth)
        return {"target": target, "where": where, "factor": factor, "sign": self.dtype(sign), "source": source,
                "high": high, "low": low, "decay": decay.reshape(shape).astype(self.dtype),
                "gain": gain.reshape(shape).astype(self.dtype), "memory": np.zeros(target[where].shape, self.dtype)}

    def _tap(self, key, fields, component, where):
        shape = fields[component][where[0] if isinstance(where[0], tuple) else where].shape
        self.sums[key] = np.zeros((len(self.wavelengths), *shape), np.complex64)
        self.taps.append((key, fields is self.h, component, where))

    def pulse(self, t: float) -> float:
        return float(np.exp(-0.5 * ((t - self.t0) / self.tau) ** 2) * np.sin(2 * np.pi * self.f0 * (t - self.t0)))

    def _advance_layers(self, layers):
        for layer in layers:
            memory = layer["memory"]
            memory *= layer["decay"]
            memory += layer["gain"] * (layer["source"][layer["high"]] - layer["source"][layer["low"]])
            layer["target"][layer["where"]] += layer["sign"] * layer["factor"] * memory

    def one_step(self):
        e, h, s = self.e, self.h, self.dtype(COURANT)
        hi, lo = slice(1, None), slice(None, -1)
        (ia, ib), (ja, jb), (ka, kb) = self.inject
        line = self.lines[0]
        # H to step + 1/2
        for c in range(3):
            a, b = "xyz"[(c + 1) % 3], "xyz"[(c + 2) % 3]
            w = self.work_h[c]
            np.subtract(e[(c + 2) % 3][_sl(**{a: hi})], e[(c + 2) % 3][_sl(**{a: lo})], out=w)
            w -= e[(c + 1) % 3][_sl(**{b: hi})]
            w += e[(c + 1) % 3][_sl(**{b: lo})]
            w *= s
            h[c] -= w
        self._advance_layers(self.layers_h)
        off = self.extra
        e1 = line["e"]
        h[1][ia:ib, ja:jb + 1, ka - 1] += s * self.dtype(e1[off + ka])
        h[1][ia:ib, ja:jb + 1, kb] -= s * self.dtype(e1[off + kb])
        row = (s * e1[off + ka:off + kb + 1]).astype(self.dtype)
        h[2][ia:ib, ja - 1, ka:kb + 1] -= row
        h[2][ia:ib, jb, ka:kb + 1] += row
        for each in self.lines:
            each["h"] -= COURANT * (each["e"][1:] - each["e"][:-1])
        # E to step + 1
        for c in range(3):
            a, b = "xyz"[(c + 1) % 3], "xyz"[(c + 2) % 3]
            inner, w = e[c][_sl(**{a: slice(1, -1), b: slice(1, -1)})], self.work_e[c]
            np.subtract(h[(c + 2) % 3][_sl(**{a: hi, b: slice(1, -1)})], h[(c + 2) % 3][_sl(**{a: lo, b: slice(1, -1)})], out=w)
            w -= h[(c + 1) % 3][_sl(**{b: hi, a: slice(1, -1)})]
            w += h[(c + 1) % 3][_sl(**{b: lo, a: slice(1, -1)})]
            w *= self.cb[c]
            inner *= self.ca[c]
            inner += w
        self._advance_layers(self.layers_e)
        h1 = line["h"]
        e[0][ia:ib, ja:jb + 1, ka] += self.cb[0][ia:ib, ja - 1:jb, ka - 1] * self.dtype(h1[off + ka - 1])
        e[0][ia:ib, ja:jb + 1, kb] -= self.cb[0][ia:ib, ja - 1:jb, kb - 1] * self.dtype(h1[off + kb])
        row = h1[off + ka:off + kb].astype(self.dtype)
        e[2][ia, ja:jb + 1, ka:kb] -= self.cb[2][ia - 1, ja - 1:jb, ka:kb] * row
        e[2][ib, ja:jb + 1, ka:kb] += self.cb[2][ib - 1, ja - 1:jb, ka:kb] * row
        self.step += 1
        value = self.pulse(self.step * self.dt)
        for each in self.lines:
            each["e"][1:-1] = each["ca"][1:-1] * each["e"][1:-1] - each["cb"][1:-1] * (each["h"][1:] - each["h"][:-1])
            each["e"][self.source] += value

    def _accumulate(self):
        t = self.step * self.dt
        phase_e = np.exp(1j * self.omega * t) * self.dt * self.stride
        phase_h = np.exp(1j * self.omega * (t - self.dt / 2)) * self.dt * self.stride
        off, nz = self.extra, self.n[2]
        self.sums["incident"] += phase_e * self.lines[-1]["e"][off + self.k0]
        self.sums["line_e"] += np.multiply.outer(phase_e, self.lines[0]["e"][off:off + nz + 1])
        self.sums["line_h"] += np.multiply.outer(phase_h, self.lines[0]["h"][off:off + nz])
        pe, ph = phase_e.astype(np.complex64), phase_h.astype(np.complex64)
        for key, magnetic, component, where in self.taps:
            fields = self.h if magnetic else self.e
            if isinstance(where[0], tuple):
                sample = 0.5 * (fields[component][where[0]] + fields[component][where[1]])
            else:
                sample = fields[component][where]
            self.sums[key] += np.multiply.outer(ph if magnetic else pe, sample)

    def advance(self, seconds: float = np.inf) -> bool:
        """Step until the ring-down is over (True) or the time allowed is used up (False)."""
        deadline, check = time.time() + seconds, 50
        hold = int(self.wavelengths.max() / (COURANT * self.cell) / check) + 1
        section = self.volumes["section"]
        while self.step < self.last:
            self.one_step()
            if self.step % self.stride == 0:
                self._accumulate()
            if self.step % check == 0:
                now = max(float(np.abs(f[section]).max()) for f in self.e)
                if not np.isfinite(now):
                    raise FloatingPointError("the fields blew up")
                self.peak = max(self.peak, now)
                self.quiet = self.quiet + 1 if now < DECAY * self.peak else 0
                if self.step > self.first and self.quiet >= hold:
                    return True
                if time.time() > deadline:
                    return False
        return True

    # --- checkpoints ---
    def save(self, path: Path):
        state = {f"e{c}": self.e[c] for c in range(3)} | {f"h{c}": self.h[c] for c in range(3)}
        state |= {f"memory{i}": layer["memory"] for i, layer in enumerate(self.layers)}
        state |= {f"sum.{key}": value for key, value in self.sums.items()}
        for i, line in enumerate(self.lines):
            state |= {f"line{i}.e": line["e"], f"line{i}.h": line["h"]}
        np.savez(path, counters=np.array([self.step, self.peak, self.quiet]), **state)

    def load(self, path: Path):
        with np.load(path) as state:
            for c in range(3):
                self.e[c][...], self.h[c][...] = state[f"e{c}"], state[f"h{c}"]
            for i, layer in enumerate(self.layers):
                layer["memory"][...] = state[f"memory{i}"]
            for key in self.sums:
                self.sums[key][...] = state[f"sum.{key}"]
            for i, line in enumerate(self.lines):
                line["e"][...], line["h"][...] = state[f"line{i}.e"], state[f"line{i}.h"]
            step, self.peak, quiet = state["counters"]
            self.step, self.quiet = int(step), int(quiet)

    # --- what the sums say ---
    def _face(self, name, u, side, e_extra=None, h_extra=None):
        """Sum over one face of E_a conj(H_b) - E_b conj(H_a), trapezoid weights; extras replace the stored fields."""
        key = f"{name}.{u}.{side}"
        ea, eb, hb, ha = (self.sums[f"{key}.{part}"] for part in ("ea", "eb", "hb", "ha"))
        if e_extra is not None:
            ea, eb = e_extra
        if h_extra is not None:
            hb, ha = h_extra
        a, b = (u + 1) % 3, (u + 2) % 3

        def weighted(values, axis):                              # half weight on the two edge lines of the face
            w = np.ones(values.shape[axis + 1])
            w[0] = w[-1] = 0.5
            shape = [1, 1, 1, 1]
            shape[axis + 1] = w.size
            return values * w.reshape(shape)

        total = np.sum(weighted(ea * np.conj(hb), b), axis=(1, 2, 3)) - np.sum(weighted(eb * np.conj(ha), a), axis=(1, 2, 3))
        return (1 if side else -1) * total * self.cell**2

    def results(self) -> dict:
        """Cross-sections (m2), region means and maxima and the axial section, per wavelength."""
        norm = np.abs(self.sums["incident"]) ** 2
        out = {"wavelengths": self.wavelengths, "steps": np.array(self.step)}
        if self.boxes:
            flow = {name: sum(self._face(name, u, side) for u in range(3) for side in range(2)).real / norm
                    for name in self.boxes}
            out["scattering"], out["absorption"] = flow["scatter"], -flow["absorb"]
            out["extinction"] = out["scattering"] + out["absorption"]
            if not self.ground:
                out["cross"] = self._cross() / norm
        eps, sigma, eps_granite, sigma_granite, impedance = self.materials
        big = self.model
        for name, slices in self.volumes.items():
            ex, ey, ez = (self.sums[f"{name}.{c}"] for c in "xyz")
            field = np.stack([0.25 * (ex[:, :, :-1, :-1] + ex[:, :, 1:, :-1] + ex[:, :, :-1, 1:] + ex[:, :, 1:, 1:]),
                              0.25 * (ey[:, :-1, :, :-1] + ey[:, 1:, :, :-1] + ey[:, :-1, :, 1:] + ey[:, 1:, :, 1:]),
                              0.25 * (ez[:, :-1, :-1, :] + ez[:, 1:, :-1, :] + ez[:, :-1, 1:, :] + ez[:, 1:, 1:, :])], axis=1)
            field = field / self.sums["incident"][:, None, None, None, None]
            if name == "section":
                out["section"] = np.sum(np.abs(field) ** 2, axis=1).mean(axis=1).astype(np.float32)
                out["section_extent"] = np.array([big.origin[1] + self.cell * slices[1].start, big.origin[1] + self.cell * slices[1].stop,
                                                  big.origin[2] + self.cell * slices[2].start, big.origin[2] + self.cell * slices[2].stop])
                continue
            weights, normal = big.regions[name][1], self.normal[(slice(None), *slices)]
            rows = []
            for w, wavelength in enumerate(self.wavelengths):
                turn = wavelength * impedance / (2 * np.pi)                     # sigma to imaginary permittivity
                eps_m, eps_g = eps + 1j * sigma * turn, eps_granite + 1j * sigma_granite * turn
                rows.append(metrics.region_value(name, field[w], normal, big.inverse(eps_m, eps_g, slices), weights, eps_m))
            out[f"mean.{name}"], out[f"max.{name}"] = (np.array(column) for column in zip(*rows))
        return out

    def _cross(self) -> np.ndarray:
        """Extinction from the interference of the incident and the scattered field on the outer box (free space)."""
        (ka, kb) = self.scatter[2]
        e_inc, h_inc = self.sums["line_e"], self.sums["line_h"]
        h_node = np.zeros_like(e_inc)
        h_node[:, 1:-1] = 0.5 * (h_inc[:, :-1] + h_inc[:, 1:])                  # H of the plane wave at the E planes
        total = 0.0
        for side, m in enumerate(self.scatter[2]):                              # z faces: E_x,inc H_y* + E_x H_y,inc*
            key = f"scatter.2.{side}"
            zero = np.zeros_like(self.sums[key + ".eb"])
            total = total + self._face("scatter", 2, side, e_extra=(np.broadcast_to(e_inc[:, m, None, None, None], self.sums[key + ".ea"].shape), zero))
            total = total + self._face("scatter", 2, side, h_extra=(np.broadcast_to(h_node[:, m, None, None, None], self.sums[key + ".hb"].shape), zero.copy()))
        for side in range(2):                                                   # y faces: -E_x,inc H_z*; here a = z, b = x
            key = f"scatter.1.{side}"
            shape = self.sums[key + ".eb"].shape                                # (w, x cells, 1, z nodes)
            e_b = np.broadcast_to(e_inc[:, None, None, ka:kb + 1], shape)
            total = total + self._face("scatter", 1, side, e_extra=(np.zeros_like(self.sums[key + ".ea"]), e_b))
        for side in range(2):                                                   # x faces: -E_z H_y,inc*; here a = y, b = z
            key = f"scatter.0.{side}"
            shape = self.sums[key + ".ha"].shape                                # (w, 1, y nodes, z cells)
            h_a = np.broadcast_to(h_inc[:, None, None, ka:kb], shape)
            total = total + self._face("scatter", 0, side, h_extra=(np.zeros_like(self.sums[key + ".hb"]), h_a))
        return -total.real


def run(model, case, q, wavelengths, sigma: float, checkpoint: Path | None = None, seconds: float = np.inf,
        dtype=np.float32, flux: bool = True, layers: int = LAYERS) -> dict | None:
    """One run of a case at one conductivity; None if the time allowed ran out (the state is then in `checkpoint`)."""
    speed, impedance = constants(q)
    solver = Run(model, case.eps, sigma, q("em.granite_eps"), q("em.granite_conductivity"), case.ground, case.direction,
                 wavelengths, speed, impedance, dtype, flux, layers)
    if checkpoint is not None and checkpoint.exists():
        solver.load(checkpoint)
    if solver.advance(seconds):
        if checkpoint is not None:
            checkpoint.unlink(missing_ok=True)
        return solver.results()
    solver.save(checkpoint)
    return None
