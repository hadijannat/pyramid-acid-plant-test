"""Geometric premises: the survey values in the ledger against the criteria of E11, E12, E15, E25, E32 and S15.

Each rule evaluates the claim's criterion in ledger/claims.yaml as written. Where the survey leaves a feature in
dispute, its two readings are the two ends of the three-way rule: pass only if the criterion holds in the
unfavourable reading, fail only if it fails even in the favourable one.

Assumptions:
- A King's Chamber shaft is a level run from the chamber wall, one straight incline at the surveyed mean slope and,
  in the level-end reading, a level last stretch; the casing face is the plane through the base edge and Petrie's
  computed apex. This is the construction of pyramid.geometry.spaces._kc_shaft, restated here so that the premises
  need no CAD kernel.
- An antechamber groove is taken as rectangular at its residual depth, which overstates a half-round groove.
- The clearance round a portcullis slab is the slot width less the one surviving fragment's thickness, over the
  slab's full width.
- "Comparable size" for the Big Void is tested on its length, the only dimension the muon paper states.
"""
import math

from pyramid import simkit
from pyramid.ledger import Ledger, load
from pyramid.screening import Result

INCH = 0.0254  # metres in an inch, a unit conversion

# The criteria's own lines, and the thresholds they leave open (judgement calls, named again in the bases).
EXIT_BAND = (79.0, 81.0)  # E11: "the casing plane at Z = 80 +/- 1 m"
CLAIMED_STONE = (3 * INCH, 5 * INCH)  # E25: the claim's "3 to 5 in"
ABOUT = 0.5 * INCH  # E25 "about that thickness": the record quotes whole inches, so half an inch either side
COMPARABLE = 10.0  # E32 "comparable size": within a factor of ten, the "order of magnitude" of 01 check 12


def shaft_exit(q, side: str, level_end: bool = False) -> tuple[float, float]:
    """(level, length along the axis) at which a King's Chamber shaft, carried on, meets the casing plane.

    At level z the face stands half * (1 - z / apex) from the centre. The axis leaves the chamber wall level,
    climbs at the surveyed slope and, with level_end, runs level for its last stretch.
    """
    way = 1.0 if side == "north" else -1.0
    half, apex = q["pyr.base_side"] / 2, q["pyr.height_original"]
    z = q["kc.floor.z"] + q["kcs.mouth_height"] + q[f"kcs.{side}.height"] / 2  # level of the axis at the mouth
    slope = math.radians(q[f"kcs.{side}.angle"])
    level = q["kcs.horizontal_length"]
    flat = q["kcs.level_end_length"] if level_end else 0.0
    run = half * (1 - z / apex) - way * q[f"kc.{side}_wall.y"] - level - flat  # what the incline must cover
    rest = run / (math.cos(slope) + half / apex * math.sin(slope))
    return z + rest * math.sin(slope), level + rest + flat


def _exit_inputs(side: str, level_end: bool) -> tuple[str, ...]:
    inputs = ("pyr.base_side", "pyr.height_original", "kc.floor.z", "kcs.mouth_height", f"kcs.{side}.height",
              f"kcs.{side}.angle", "kcs.horizontal_length", f"kc.{side}_wall.y")
    return inputs + (("kcs.level_end_length",) if level_end else ())


def _groove_area(q) -> float:
    return q["ante.groove_count"] * q["ante.groove_width"] * q["ante.groove_residual_depth"]


def _passage_length(q) -> float:
    return math.dist(*([q[f"sp.{end}_end.{axis}"] for axis in "xyz"] for end in ("north", "south")))


_SP_ENDS = tuple(f"sp.{end}_end.{axis}" for end in ("north", "south") for axis in "xyz")

# One row per number the bases quote: (id, label, unit, formula, inputs, function of {ledger id: number}).
# simkit.corners is exact for every row: each function is monotone in each input over the ledger's ranges
# (the exit level rises with the slope and the mouth level and falls with the level runs).
# ponytail: the passage length is monotone only while the surveyed ends stay as far apart in x and z as they are
# (0.17 m and 0.06 m at the least); a general bound if the survey errors ever exceed that.
QUANTITIES: list[tuple] = [
    *[(f"premises.kcs_{side}_exit_z{'_level' if level_end else ''}",
       f"Level at which the {side}ern King's Chamber shaft meets the casing plane"
       + (", with a level last stretch" if level_end else ", inclined to the face"),
       "m", "z = z_mouth + s sin(slope); s = (face distance - level runs) / (cos(slope) + (half / apex) sin(slope))",
       _exit_inputs(side, level_end), lambda q, side=side, level_end=level_end: shaft_exit(q, side, level_end)[0])
      for level_end in (False, True) for side in ("north", "south")],
    ("premises.groove_connected_area", "Largest connected area of the antechamber grooves at the door top", "m2",
     "A = grooves x width x residual depth",
     ("ante.groove_count", "ante.groove_width", "ante.groove_residual_depth"), _groove_area),
    ("premises.groove_full_area", "Area of the antechamber grooves at their full measured depth", "m2",
     "A = grooves x width x depth", ("ante.groove_count", "ante.groove_width", "ante.groove_depth"),
     lambda q: q["ante.groove_count"] * q["ante.groove_width"] * q["ante.groove_depth"]),
    ("premises.slab_clearance_area", "Clearance round one portcullis slab", "m2",
     "A = (slot width - slab thickness) x slab width", ("ante.slot_width", "ante.slab_thickness", "ante.slab_width"),
     lambda q: (q["ante.slot_width"] - q["ante.slab_thickness"]) * q["ante.slab_width"]),
    ("premises.sp_length_between_ends", "South passage, distance between its surveyed ends", "m",
     "L = |south end - north end|", _SP_ENDS, _passage_length),
    # the record itself, listed so that the number E25 turns on appears among the results
    ("premises.qcs_stone_left", "Uncut wall stone at each Queen's Chamber shaft mouth, as recorded", "m",
     "t = the thickness in the survey record", ("qcs.stone_left",), lambda q: q["qcs.stone_left"]),
    ("premises.void_length_ratio", "Big Void length over the Grand Gallery's", "1", "L_void / L_gallery",
     ("bv.length", "gg.roof_length_sloping"), lambda q: q["bv.length"] / q["gg.roof_length_sloping"]),
    ("premises.void_centre_above_roof", "Big Void centre above the top of the Gallery roof", "m",
     "z_void - z_roof", ("bv.centre.z", "gg.roof_top.z"), lambda q: q["bv.centre.z"] - q["gg.roof_top.z"]),
]


def results(ledger: Ledger) -> dict[str, Result]:
    return {id: Result(id, label, *simkit.corners(ledger, inputs, fn), unit, formula, inputs)
            for id, label, unit, formula, inputs, fn in QUANTITIES}


def _span(result: Result, digits: int = 1) -> str:
    return f"{result.low:.{digits}f} to {result.high:.{digits}f}"


def _e11(ledger, r):
    exits = [r[f"premises.kcs_{side}_exit_z{variant}"] for variant in ("", "_level") for side in ("north", "south")]
    north, south, north_level, south_level = exits
    low, high = EXIT_BAND
    at_survey = sum(low <= e.value <= high for e in exits)
    always = sum(low <= e.low and e.high <= high for e in exits)
    # ponytail: the favourable end is tested exit by exit, not jointly. The two readings of one shaft share its
    # slope and differ by less than the band is wide, so each can lie inside whenever both ranges reach it; search
    # the corners jointly if a later survey narrows the band.
    reachable = all(e.low <= high and e.high >= low for e in exits)
    flat = ledger.rng("kcs.level_end_length")[1]  # the level run one survey gives the southern outlet
    # The survey record, which no number changes: a level end is drawn for the southern shaft only, by one party
    # (Perring, 1837 to 1839, known through Thomas; the plate is unread), in core masonry; Petrie's theodolite
    # at the same mouth in 1881 found the incline continuing; the northern outlet was forced open before any
    # survey; the casing both would pierce is gone (01 claim 1 and check 4). So the unfavourable reading shows
    # no level end and a pass is out of reach, and the favourable reading shows one for the southern shaft.
    status = simkit.three_way(False, flat > 0 and reachable)
    where = (
        f"Carried to the casing plane at the surveyed slopes, the shafts come out at Z = {north.value:.1f} m in the "
        f"north ({_span(north)} m over the ranges of the inputs) and {south.value:.1f} m in the south "
        f"({_span(south)} m)"
    )
    if flat <= 0:
        return status, (
            "No survey gives either King's Chamber shaft a level outer end, so the premise has no reading in which "
            f"it holds. {where}."
        )
    return status, (
        f"A level outer end is on record for one shaft only: one survey party of 1837 to 1839, known here through a "
        f"later citation of its unread plate, drew the last {flat:.1f} m of the southern channel level, in core "
        "masonry, while the 1881 survey found the incline continuing to that mouth; the northern outlet was forced "
        "open before any survey and its level end is only presumed, and the casing is gone at both, so no survey "
        f"can show a run through it. {where}, and with a level last {flat:.1f} m at {north_level.value:.1f} m "
        f"({_span(north_level)} m) and {south_level.value:.1f} m ({_span(south_level)} m): {at_survey} of the 4 "
        f"lie inside the criterion's 80 +/- 1 m at the surveyed values and {always} of the 4 over the whole of "
        "their ranges"
        + ("." if reachable else ", and at least one cannot reach it at any end of its range.")
    )


def _grooves(ledger, r):
    """(status, the sentence both groove claims share): blind and connected are the two ends of the residual depth."""
    area, full = r["premises.groove_connected_area"], r["premises.groove_full_area"]
    shallow, deep = (1000 * depth for depth in ledger.rng("ante.groove_residual_depth"))
    status = simkit.three_way(area.low > 0, area.high > 0)
    count, width = ledger.q("ante.groove_count"), ledger.q("ante.groove_width")
    reading = {
        "pass": "so a connected duct exists in every reading of the survey",
        "conditional": "so a connected duct exists only in the reading that lets them reach the doorway, and the "
                       "blind reading, which is Petrie's own, has none",
        "fail": "so the grooves are blind in every reading of the survey",
    }[status]
    return status, (
        f"Petrie's depths for the {count:.0f} grooves in the south wall run out to between {shallow:.1f} and "
        f"{deep:.1f} mm at the top of the doorway, where the stone is broken away, {reading}: the connected area is "
        f"{area.high:.4f} m2 at most ({count:.0f} grooves {width:.3f} m wide) against {full.value:.3f} m2 for "
        f"grooves of the full {1000 * ledger.q('ante.groove_depth'):.0f} mm, which the measured taper rules out"
    )


def _e12(ledger, r):
    status, grooves = _grooves(ledger, r)
    return status, (
        f"{grooves}. The {ledger.q('ante.slot_count'):.0f} pairs of slots for the slabs and the "
        f"{ledger.q('ante.groove_count'):.0f} grooves themselves are on record."
    )


def _s15(ledger, r):
    status, grooves = _grooves(ledger, r)
    area, gap = r["premises.groove_connected_area"], r["premises.slab_clearance_area"]
    beside = (
        f"The clearance round one slab, {gap.value:.3f} m2 from the one surviving fragment, is "
        + (f"{gap.value / area.high:.0f} times the grooves at their most" if area.high > 0
           else "open where they are not")
        + ", so the grooves would not be the only way past the slabs."
    )
    return status, (
        "With the slabs down, the duct the claim names from the King's Chamber to the Gallery is the grooves, and the "
        f"criterion tests them: it fails the blind case and allows the connected one about 0.002 m2. {grooves}. "
        f"{beside}"
    )


def _e15(ledger, r):
    between, stations = r["premises.sp_length_between_ends"], ledger.q("sp.length")
    depth = -ledger.q("sp.south_end.z")
    # The record is fixed: Petrie's survey and Haase's, read on the page, both have the passage end blind in rock
    # and neither records an opening at its south end (01 claim 6 and check 16). What the numbers can show is
    # whether the two figures for where it ends agree within the stated errors of the end coordinates.
    agree = between.low <= stations <= between.high
    return ("pass" if agree else "conditional"), (
        f"The survey record has the south passage end blind in rock, {depth:.1f} m below the pavement, with no "
        f"opening at its south end: Petrie's stations make it {stations:.2f} m long and his coordinates for its two "
        f"ends {between.value:.2f} m ({_span(between, 2)} m over their stated errors), "
        + ("and a second survey, read on the page, gives the same length and the same blind end."
           if agree else
           "two figures that disagree, so the record of where the passage ends is not secure.")
    )


def _e25(ledger, r):
    record = r["premises.qcs_stone_left"]
    stone, thin, thick = record.value, record.low, record.high
    claim_low, claim_high = CLAIMED_STONE

    def decided(about: float) -> str:  # closed, and "about" the claim's 3 to 5 in
        def fits(thickness):
            return thickness > 0 and claim_low - about <= thickness <= claim_high + about

        return simkit.three_way(fits(thin) and fits(thick), thick > 0 and thin <= claim_high + about
                                and thick >= claim_low - about)

    status = decided(ABOUT)
    # Two judgement calls. The half inch read into "about" is one, and the basis says whether it moves the word.
    # The other decides it: the thickness rests on one witness (Smyth) quoted twice at second hand, which 01 check
    # 11 grades "two secondary routes, one primary witness", and the rule counts that as what the survey record
    # shows. Held to rest on a secondary source it would be conditional, by the documentary rule of the simulations
    # design, section 2. The closure itself is in Petrie, section 44, re-read in its online edition in 06 (the
    # parameter table and check 19) and read in 01 only as quoted in Thomas's paper (check 11).
    about = ("a reading of 'about' that decides nothing here" if decided(0.0) == status
             else "a judgement call on 'about' that decides the word here")
    outcome = {
        "pass": "So the whole range carried for the record lies within the claimed thickness",
        "conditional": "So only part of the range carried for the record lies within the claimed thickness",
        "fail": "So no part of the range carried for the record lies within the claimed thickness",
    }[status]
    # The low end the ledger carries is no measurement where it is the claim's own 3 in.
    carried = (f"The record is the {1000 * stone:.0f} mm alone: the {1000 * thin:.0f} mm at the low end of the range "
               f"the ledger carries ({1000 * thin:.0f} to {1000 * thick:.0f} mm) is the claim's own figure, and no "
               "source was found for 3 in."
               if thin < stone and math.isclose(thin, claim_low) else
               f"The ledger carries {1000 * thin:.0f} to {1000 * thick:.0f} mm for the record; no source was found "
               "for 3 in.")
    return status, (
        f"The survey record has each Queen's Chamber shaft mouth closed by a plate of the wall stone left uncut "
        f"until both were cut through in 1872. Petrie describes the plate without a thickness (his section 44, "
        f"re-read in its online edition in 06 and read in 01 as quoted by Thomas). The thickness, "
        f"{1000 * stone:.0f} mm "
        f"({stone / INCH:.1f} in), comes from one witness, quoted twice at second hand. Counting that as what the "
        "survey record shows is a judgement call, and it decides the word: held to rest on a secondary source, the "
        f"claim would be conditional. The claim's 3 to 5 in is {1000 * claim_low:.0f} to {1000 * claim_high:.0f} mm. "
        f"{carried} {outcome}, read to half an inch either side, {about}."
    )


def _e32(ledger, r):
    ratio, above = r["premises.void_length_ratio"], r["premises.void_centre_above_roof"]
    (south_low, south_high), (length_low, length_high) = ledger.rng("bv.south_end.y"), ledger.rng("bv.length")
    reach = math.cos(math.radians(ledger.rng("bv.incline_angle")[1]))  # an inclined void covers less ground
    gallery_south, gallery_north = ledger.rng("gg.south_end.y")[1], ledger.rng("gg.north_end.y")[0]

    def comparable(x, factor=COMPARABLE):
        return 1 / factor <= x <= factor

    # Over the Gallery in plan: the void starts south of the Gallery's north end and reaches north of its south end.
    over_worst = south_high < gallery_north and south_low + length_low * reach > gallery_south
    over_best = south_low < gallery_north and south_high + length_high > gallery_south
    status = simkit.three_way(
        above.low > 0 and over_worst and comparable(ratio.low) and comparable(ratio.high),
        above.high > 0 and over_best and (comparable(ratio.low) or comparable(ratio.high)),
    )
    within_two = comparable(ratio.low, 2) and comparable(ratio.high, 2)
    stricter = " (it also holds within a factor of two)" if within_two else ""
    outcome = {
        "pass": f"a published void of comparable size lies above the Gallery{stricter}",
        "conditional": "a void of comparable size above the Gallery follows at some ends of the published ranges only",
        "fail": "the published void is not of comparable size above the Gallery at any end of the published ranges",
    }[status]
    return status, (
        f"The muon paper of 2017 gives a void at least {length_low:.0f} m long, {ratio.value:.2f} of the Gallery's "
        f"{ledger.q('gg.roof_length_sloping'):.1f} m ({_span(ratio, 2)} over the {length_low:.0f} to "
        f"{length_high:.0f} m carried for it), with its centre {above.value:.1f} m above the top of the Gallery roof "
        f"({_span(above)} m) and its south end within {max(abs(south_low), abs(south_high)):.0f} m of the pyramid's "
        f"centre, over the Gallery in plan. Taking comparable as within a factor of {COMPARABLE:.0f} in the one "
        f"dimension published, the order of magnitude that 01 allows (a judgement call), {outcome}. The section is "
        "inferred from the muon excess and not measured, and shape, inclination and the number of voids are open; "
        "the heat-exchanger use is judged separately."
    )


# The thresholds and the choice of status in these rules are judgement calls. They restate the pass and fail lines
# of the criteria in ledger/claims.yaml, which come from research/01-geometry.md.
RULES = {"E11": _e11, "E12": _e12, "E15": _e15, "E25": _e25, "E32": _e32, "S15": _s15}

# Every ledger quantity each rule reads, itself or through the results it quotes. The viewer shows a result under
# a claim only when the claim's depends_on in ledger/claims.yaml holds all the result's inputs, so depends_on must
# gain whichever of these it lacks; the merge applies that, since claims.yaml is not this package's to edit.
_GROOVES = ("ante.groove_count", "ante.groove_width", "ante.groove_residual_depth", "ante.groove_depth")
READS = {
    "E11": tuple(dict.fromkeys(_exit_inputs("north", True) + _exit_inputs("south", True))),
    "E12": (*_GROOVES, "ante.slot_count"),
    "E15": (*_SP_ENDS, "sp.length"),
    "E25": ("qcs.stone_left",),
    "E32": ("bv.length", "gg.roof_length_sloping", "bv.centre.z", "gg.roof_top.z", "bv.south_end.y",
            "bv.incline_angle", "gg.south_end.y", "gg.north_end.y"),
    "S15": (*_GROOVES, "ante.slot_width", "ante.slab_thickness", "ante.slab_width"),
}

ASSUMPTIONS = [
    "A King's Chamber shaft is a level run from the chamber wall, one straight incline at the surveyed mean slope "
    "and, in the level-end reading, a level last stretch, met with the plane of the original casing.",
    "The two readings of a disputed feature (the level outer end of the southern shaft, the grooves reaching the "
    "doorway) are the two ends of the three-way rule; the reading of the direct survey is the unfavourable end.",
    "An antechamber groove is rectangular at its residual depth, which overstates a half-round groove.",
    "The clearance round a portcullis slab is the slot width less the thickness of the one surviving fragment.",
    "Comparable size for the Big Void is tested on its length, the only dimension the muon paper states, within a "
    "factor of ten; the assumed section and volume carried in the ledger decide nothing.",
    "About 3 to 5 in is read to half an inch either side, the precision of a figure quoted in whole inches.",
    "E25: one witness quoted twice at second hand is counted as the survey record of the thickness, a judgement call "
    "that decides pass against conditional; the closure itself is in the direct survey, which gives no thickness.",
]


def verdicts(ledger: Ledger, computed: dict[str, Result] | None = None) -> dict[str, tuple[str, str]]:
    computed = results(ledger) if computed is None else computed
    return {claim: rule(ledger, computed) for claim, rule in RULES.items()}


def figure(computed: dict[str, Result], out_dir) -> None:
    """figures/kcs_exits.png: the four shaft exits with their ranges against the criterion's 80 +/- 1 m."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    exits = [computed[id] for id in computed if id.startswith("premises.kcs_")]
    names = [f"{'north' if '_north_' in e.id else 'south'}, {'level end' if e.id.endswith('_level') else 'inclined'}"
             for e in exits]
    fig, ax = plt.subplots(figsize=(7, 2.8))
    ax.axvspan(*EXIT_BAND, color="0.85", label="criterion: Z = 80 +/- 1 m")
    ax.errorbar([e.value for e in exits], range(len(exits)), fmt="o", color="black", capsize=4,
                xerr=[[e.value - e.low for e in exits], [e.high - e.value for e in exits]],
                label="surveyed values, with the range of the inputs")
    ax.set_yticks(range(len(exits)), names)
    ax.set_ylim(len(exits) - 0.5, -0.5)
    ax.set_xlabel("level of the shaft's exit on the casing plane, m above the pavement")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.3), ncols=2, frameon=False, fontsize=8)
    fig.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    simkit.save_figure(fig, out_dir / "kcs_exits.png", dpi=150)
    plt.close(fig)


def main(root=simkit.RESULTS) -> None:
    ledger = load()
    computed = results(ledger)
    out_dir = simkit.write_results("premises", ledger, computed, verdicts(ledger, computed),
                                   {"assumptions": ASSUMPTIONS}, root)
    figure(computed, out_dir / "figures")


if __name__ == "__main__":
    main()
