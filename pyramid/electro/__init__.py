"""electro: ground current, lightning, the piezoelectric chain and room acoustics. Decides S04, E21, S06 and E13.

conduction solves steady conduction on a graded grid; sources puts the pyramid, the King's Chamber granite and the
ore sheets on it for a telluric far field and for a stroke at the summit; piezo runs Tier 0's two piezoelectric
chains backwards to the field the granite would need; rooms ranks three rooms by decay time and modal quality factor.
Each module's docstring lists its assumptions; ASSUMPTIONS collects them for the manifest.

The ranges: every conduction number is taken at the ledger values and at every corner of the ranges of its swept
inputs (simkit.corners), which brackets it where it is monotone in each input. The fields are not proved monotone,
so the verdicts are drawn only where the margin is orders of magnitude, far more than any corner could hide.
"""
import math

from pyramid import screening, simkit
from pyramid.electro import piezo, rooms, sources
from pyramid.ledger import Ledger
from pyramid.screening import Result

FAR_FIELD_QUIET = 1e-7  # V/m: the low end of the far-field range written in the criteria of S04 and E21
SWEPT = sources.MATERIALS + (sources.SHELL,)
ORE_SWEPT = sources.SHEETS + ("plateau.host_resistivity",)
ORE_RESISTIVITY = "plateau.hematite_resistivity_specular"  # its low end is the most conductive hematite measured
FAR_FIELDS = ("em.telluric_field_storm", "em.telluric_field_extreme")
STROKES = ("em.stroke_current_median", "em.stroke_current_max")
MODEL = sources.GEOMETRY + SWEPT

ASSUMPTIONS = [
    "Conduction is steady; the stroke is taken at its peak current as if steady, which leaves out induction and so "
    "overstates the field at the chamber.",
    "The pyramid is homogeneous masonry in its designed square shape, cut off at today's platform, on a half-space of "
    "bedrock; the air is insulating; joints, casing and a wetter skin are not drawn.",
    "The King's Chamber is an insulating cavity lined with a granite shell of one assumed thickness; the relieving "
    "chambers, the antechamber and every other void are left out.",
    "The granite's peak field is the largest cell value on cells of about one metre; it grows by about a tenth each "
    "time the cells are halved because the field is singular along the cavity's edges, while the volume mean is "
    "converged to about 2 percent.",
    "An ore body is a pair of vertical sheets of the most conductive hematite measured, in line with the far field and "
    "ending at the base edges; their thickness, depth and length are assumed and swept.",
    "The telluric far field runs north-south, across the chamber's short side, which gives a resistive body the "
    "larger field.",
    "The field the granite needs is Tier 0's single-pulse chain run backwards, with every input of that chain at its "
    "generous end for the favourable end. Tier 0's S07 chain, a sustained drive across the antechamber's granite leaf "
    "for which no source is proposed, needs a lower field at its generous end; its figure is reported beside the "
    "pulse chain's and decides no status.",
    "Non-negligible, in the criteria of S04 and E21, is read as reaching the field the pulse chain needs: a judgement "
    "call.",
    "The fail clause of S06's criterion, a field screened to the conduction value of order kV/m or less, is read as "
    "the field staying below the pulse chain's need at the favourable end: a judgement call. The model is a "
    "conduction model, so its field is the conduction value by construction.",
    "The rooms are hard-walled boxes with Sabine decay from the walls and the air: one assumed wall absorption shared "
    "by the three rooms, and air absorption as frequency squared scaled to the ledger's 13 kHz value; open passage "
    "mouths are a sensitivity case only.",
    "The field in the lining of a gas-filled chamber is capped at the air-breakdown field, whatever the masonry's "
    "resistivity.",
    "Ranks first, in the criterion of E13, is read as first in both decay time and modal quality factor: a judgement "
    "call.",
]


def _sweep(ledger: Ledger, swept: tuple[str, ...], summary) -> dict[str, tuple[float, float, float]]:
    """Each number of summary(q) at the ledger values, with its least and greatest over the corners of `swept`."""
    base = {i: ledger.q(i) for i in MODEL + sources.SHEETS}
    solved = {}

    def run(q):
        key = tuple(q[i] for i in swept)
        if key not in solved:
            solved[key] = summary(base | q)
        return solved[key]

    names = run({i: ledger.q(i) for i in swept})
    return {name: simkit.corners(ledger, swept, lambda q, name=name: run(q)[name]) for name in names}


def _scaled(triple, value: float, low: float, high: float) -> tuple[float, float, float]:
    """A (value, low, high) per unit of drive, times the drive at its ledger value, its least and its greatest."""
    return triple[0] * value, triple[1] * low, triple[2] * high


def conduction_results(ledger: Ledger, h: float = 1.0) -> dict[str, Result]:
    """The telluric and lightning fields from the three-dimensional model, on cells of h metres at the chamber."""
    out = {}

    def add(name, label, triple, unit, formula, inputs):
        out[f"electro.{name}"] = Result(f"electro.{name}", label, *triple, unit, formula, inputs)

    storm = ledger.q(FAR_FIELDS[0])
    extreme = ledger.rng(FAR_FIELDS[1])[1]
    telluric = _sweep(ledger, SWEPT, lambda q: sources.telluric_summary(q, h))
    model = "div(sigma grad phi) = 0, far field E0 north-south, air insulating"
    add("telluric_granite_ratio", "Peak telluric field in the King's Chamber granite over the far field",
        telluric["granite_peak"], "1", f"max |E| in the granite / E0; {model}", MODEL)
    add("telluric_granite_mean_ratio", "Volume-mean telluric field in the King's Chamber granite over the far field",
        telluric["granite_mean"], "1", f"mean |E| in the granite / E0; {model}", MODEL)
    add("telluric_masonry_ratio", "Telluric field in the masonry beside the King's Chamber over the far field",
        telluric["masonry"], "1", f"mean |E| in the masonry at chamber level / E0; {model}", MODEL)
    add("telluric_summit_ratio", "Telluric field in the summit masonry over the far field",
        telluric["summit"], "1", f"mean |E| in the top layer of masonry / E0; {model}", MODEL)
    add("telluric_field", "Largest telluric field at the summit or in the granite",
        _scaled(telluric["largest"], storm, FAR_FIELD_QUIET, extreme), "V/m",
        "E0 max(granite peak ratio, summit ratio); E0 the storm-time value, 1e-7 V/m at the least, the extreme at most",
        MODEL + FAR_FIELDS)

    best_ore = ledger.rng(ORE_RESISTIVITY)[0]
    ore = _sweep(ledger, ORE_SWEPT, lambda q: sources.telluric_summary(q, h, best_ore))["largest"]
    # The masonry, the granite and the lining are not swept again with the sheets: their spread in the sheet-free
    # sweep is carried over as a factor. The unfavourable end is the sheet-free model, because the earthy hematite
    # that observers describe is more resistive than the rock and adds nothing.
    spread = telluric["largest"][2] / telluric["largest"][0]
    ore = (ore[0], min(ore[1], telluric["largest"][1]), ore[2] * spread)
    ore_inputs = MODEL + sources.SHEETS + (ORE_RESISTIVITY,)
    add("ore_ratio", "Largest telluric field at the summit or in the granite over the far field, with ore sheets",
        ore, "1", f"max(granite peak, summit) / E0 with two sheets of conductance t / rho_ore; {model}", ore_inputs)
    add("ore_field", "Largest telluric field at the summit or in the granite, with ore sheets",
        _scaled(ore, storm, FAR_FIELD_QUIET, extreme), "V/m",
        "E0 times the ratio with sheets; E0 as for the sheet-free field", ore_inputs + FAR_FIELDS)

    stroke = _sweep(ledger, SWEPT, lambda q: sources.lightning_summary(q, h))
    median, (median_low, _), largest = ledger.q(STROKES[0]), ledger.rng(STROKES[0]), ledger.rng(STROKES[1])[1]
    model = "div(sigma grad phi) = 0, I entering over the summit platform, air insulating"
    add("lightning_granite_field", "Peak field in the King's Chamber granite at the stroke's peak current",
        _scaled(stroke["granite_peak"], median, median_low, largest), "V/m",
        f"I max |E| per ampere in the granite; {model}; I the median stroke, the design maximum at most",
        MODEL + STROKES)
    add("lightning_granite_mean_field", "Volume-mean field in the King's Chamber granite at the stroke's peak current",
        _scaled(stroke["granite_mean"], median, median_low, largest), "V/m",
        f"I mean |E| per ampere in the granite; {model}", MODEL + STROKES)
    add("lightning_conduction_multiple", "Peak field in the granite over the even-spreading conduction value",
        stroke["multiple"], "1", "max |E| in the granite / (rho I / section at chamber level), 04 section 4.5", MODEL)
    return out


def chain_results(ledger: Ledger, conduction: dict[str, Result]) -> dict[str, Result]:
    """What the piezoelectric chain needs, and how the model's fields compare with it."""
    out = {}

    def add(name, label, triple, unit, formula, inputs):
        out[f"electro.{name}"] = Result(f"electro.{name}", label, *triple, unit, formula, inputs)

    chain = "E = t_rise sqrt(2 I / Z_air) / (d L), Tier 0's pulse chain inverted"
    gas_solid = simkit.corners(ledger, piezo.GAS_SOLID, piezo.needed_field_gas_solid)
    add("needed_field_gas_solid", "Field in the granite for the weakest documented gas-solid acoustic effect",
        gas_solid, "V/m", f"{chain}; I = 0.30 W/cm2 and up", piezo.GAS_SOLID)
    add("needed_field_sustained",
        "Field in the antechamber's granite leaf for the weakest documented gas-solid acoustic effect, under a "
        "sustained drive",
        simkit.corners(ledger, piezo.SUSTAINED, piezo.needed_field_sustained), "V/m",
        "E = sqrt(2 I / Z_air) / (2 pi f d L_leaf), Tier 0's S07 chain inverted; I = 0.30 W/cm2 and up",
        piezo.SUSTAINED)
    add("needed_field_wet_film", "Field in the granite to cavitate a wet film from the gas side",
        simkit.corners(ledger, piezo.WET_FILM, piezo.needed_field_wet_film), "V/m",
        f"{chain}; I the intensity of Tier 0's required sound level", piezo.WET_FILM)

    reached = conduction["electro.lightning_granite_field"]
    add("lightning_shortfall", "Field the chain needs over the peak field a stroke puts in the granite",
        (gas_solid[0] / reached.value, gas_solid[1] / reached.high, gas_solid[2] / reached.low), "1",
        "needed field for the gas-solid effect / peak field in the granite", piezo.GAS_SOLID + reached.inputs)

    # The chain turns a voltage across the granite into displacement (u = d E L = d V), and no two points of an ore
    # body differ in potential by more than the far field times its length. So the length of sheet whose whole
    # end-to-end voltage, dropped across the granite alone, would give the chain what it needs bounds every
    # arrangement of sheets, drawn or not.
    thickness = ledger.q("em.piezo_thickness")
    storm, extreme = ledger.q(FAR_FIELDS[0]), ledger.rng(FAR_FIELDS[1])[1]
    add("ore_gather_length", "Length of ore sheet whose whole telluric voltage would equal what the chain needs",
        (gas_solid[0] * thickness / storm, gas_solid[1] * thickness / extreme, gas_solid[2] * thickness / FAR_FIELD_QUIET),
        "m", "l = E_needed L / E0", piezo.GAS_SOLID + FAR_FIELDS)

    # The verdict uses the resistivity measured in the pyramid's own masonry. Its core has not been measured and may
    # be drier, so the resistivity at which the design-maximum stroke would bring the peak to the air-breakdown field
    # is reported too: the field in the masonry goes as rho I once the ground is the better conductor.
    resistive = ledger.rng("em.limestone_resistivity")[1]
    breakdown = ledger.q("em.air_breakdown_field")
    add("lightning_breakdown_resistivity", "Masonry resistivity at which the design-maximum stroke brings the granite's "
        "peak field to air breakdown", (resistive * breakdown / reached.high,) * 3, "ohm m",
        "rho = rho_max E_breakdown / peak field at the favourable end; the field goes as rho I",
        reached.inputs + ("em.air_breakdown_field",))

    skin = screening.all_results(ledger)["t0.skin_depth_lightning"]
    depth = sources.chamber_depth({i: ledger.q(i) for i in sources.GEOMETRY})
    add("chamber_skin_depths", "Depth of the King's Chamber inside the nearest face, in skin depths at the stroke's "
        "frequency", (depth / skin.value, depth / skin.high, depth / skin.low), "1",
        "distance from the chamber's centre to the nearest face / Tier 0 skin depth", sources.GEOMETRY + skin.inputs)
    return out


def room_results(ledger: Ledger) -> dict[str, Result]:
    """Lowest mode, decay time and modal quality factor of the three rooms."""
    out = {}

    def add(name, label, triple, unit, formula, inputs):
        out[f"electro.{name}"] = Result(f"electro.{name}", label, *triple, unit, formula, inputs)

    for room, spec in rooms.ROOMS.items():
        ids, label = rooms.inputs(room), spec["label"]
        add(f"lowest_mode_{room}", f"Lowest mode of the {label} as a hard-walled box",
            simkit.corners(ledger, ids, lambda q, room=room: rooms.lowest_mode(q, room)), "Hz", "f = c / (2 L)", ids)
        add(f"decay_time_{room}", f"Decay time of the {label} at the antechamber's lowest mode",
            simkit.corners(ledger, ids, lambda q, room=room: rooms.decay_time(q, room, rooms.reference_frequency(q))),
            "s", "T60 = 24 ln(10) V / (c (alpha S + 4 m V))", ids)
        add(f"modal_q_{room}", f"Quality factor of the lowest mode of the {label}",
            simkit.corners(ledger, ids, lambda q, room=room: rooms.quality_factor(q, room, rooms.lowest_mode(q, room))),
            "1", "Q = 2 pi f T60 / (6 ln 10) at f = c / (2 L)", ids)
    # The ranking is taken with one draw of every input for the three rooms together, so that the wall absorption,
    # which is one ledger quantity, has one value at a time.
    add("decay_lead", "Antechamber decay time over the longest of the other two rooms",
        simkit.corners(ledger, rooms.ALL, rooms.decay_lead), "1", "T60 of the antechamber / max T60 of the others",
        rooms.ALL)
    add("quality_lead", "Quality factor of the antechamber's lowest mode over the highest of the other two rooms",
        simkit.corners(ledger, rooms.ALL, rooms.quality_lead), "1", "Q of the antechamber / max Q of the others",
        rooms.ALL)
    mouths = rooms.ALL + rooms.PASSAGE
    add("decay_lead_open", "Antechamber decay time over the longest of the other two rooms, passage mouths open",
        simkit.corners(ledger, mouths, lambda q: rooms.decay_lead(q, True)), "1",
        "as decay_lead with A = alpha S + open mouths + 4 m V", mouths)
    add("quality_lead_open", "Quality factor of the antechamber's lowest mode over the highest other, passage mouths open",
        simkit.corners(ledger, mouths, lambda q: rooms.quality_lead(q, True)), "1",
        "as quality_lead with A = alpha S + open mouths + 4 m V", mouths)
    return out


def all_results(ledger: Ledger, h: float = 1.0) -> dict[str, Result]:
    conduction = conduction_results(ledger, h)
    return conduction | chain_results(ledger, conduction) | room_results(ledger)


# --- Verdict rules ---------------------------------------------------------------------------


def _orders(larger: float, smaller: float) -> float:
    return math.log10(larger / smaller)


def _pulse_chain(ledger: Ledger) -> str:
    """What the 2.7e7 V/m belongs to: Tier 0's chain for one pulse, named with the two inputs it has no range for."""
    return ("Tier 0's single-pulse piezoelectric chain, a field applied across "
            f"{ledger.q('em.piezo_thickness'):g} m of granite within the {1e6 * ledger.q('em.pulse_rise_time'):g} "
            "microsecond rise of a stroke,")


def _sustained_chain(ledger: Ledger) -> str:
    """Tier 0's other chain, the one of S07, at the fast end of its assumed drive."""
    return (f"Tier 0's S07 chain, a sustained drive of {ledger.rng('ac.drive_frequency')[1] / 1e6:g} MHz across the "
            "antechamber's granite leaf for which no source is proposed,")


def _against_the_chain(ledger: Ledger, r, field: Result, holds_at_best: bool) -> tuple[str, str]:
    """The three-way status of a telluric field against the pulse chain's need, and the sentence that says so.

    Judgement call: the criteria of S04 and E21 ask for a "non-negligible" field or charge and give no number. The
    only use the hypothesis makes of a field in the granite is the piezoelectric chain, so the line is the field at
    which Tier 0's single-pulse chain, with every input at its generous end, first reaches a documented acoustic
    effect. A charge is tied to its field by Gauss's law (a surface density of eps0 eps_r E), so the one comparison
    covers both words. Tier 0's S07 chain reaches that effect at a lower field, under a sustained drive that nothing
    in the hypothesis supplies; the sentence gives its figure beside the line, and the status does not read it.
    """
    needed, sustained = r["electro.needed_field_gas_solid"], r["electro.needed_field_sustained"]
    status = simkit.three_way(field.low >= needed.high, holds_at_best)
    reaches = f"at which {_pulse_chain(ledger)} first reaches a documented acoustic effect"
    call = "the line this rule takes for non-negligible as a judgement call"
    if status == "fail":
        beside = (f"and the field is {_orders(sustained.low, field.high):.1f} orders of magnitude below that too"
                  if field.high < sustained.low else "which the field reaches at the favourable end")
        return status, (
            f"is {_orders(needed.low, field.high):.1f} orders of magnitude below the {needed.low:.1e} V/m {reaches} "
            f"with every input at its generous end, {call}; a charge held by such a field is short by the same "
            f"factor. {_sustained_chain(ledger)} reaches the same effect at {sustained.low:.1e} V/m with every input "
            f"at its generous end, {beside}.")
    if status == "pass":
        return status, (f"is above the {needed.high:.1e} V/m {reaches} with every input at its least generous end, "
                        f"{call}.")
    return status, (f"is neither always below {needed.low:.1e} V/m nor always above {needed.high:.1e} V/m, the ends "
                    f"of the field {reaches}, {call}.")


def _s04(ledger, r):
    field, needed = r["electro.telluric_field"], r["electro.needed_field_gas_solid"]
    granite, masonry, summit = (r[f"electro.telluric_{part}_ratio"] for part in ("granite", "masonry", "summit"))
    status, tail = _against_the_chain(ledger, r, field, field.high >= needed.low)
    return status, (
        f"In a steady conduction model of the pyramid on bedrock, a far field of {FAR_FIELD_QUIET:.0e} to "
        f"{ledger.rng(FAR_FIELDS[1])[1]:.0e} V/m leaves {masonry.value:.2f} of itself ({masonry.low:.2f} to "
        f"{masonry.high:.2f} over the ranges of the inputs) in the masonry at chamber level and {summit.value:.3f} "
        f"({summit.low:.3f} to {summit.high:.3f}) at the summit, and puts {granite.value:.1f} ({granite.low:.1f} to "
        f"{granite.high:.1f}) times itself in the King's Chamber granite at the peak: {field.high:.2f} V/m at the "
        f"most, which {tail}")


def _e21(ledger, r):
    field, needed, ratio = r["electro.ore_field"], r["electro.needed_field_gas_solid"], r["electro.ore_ratio"]
    gather, plain = r["electro.ore_gather_length"], r["electro.telluric_granite_ratio"]
    length = ledger.rng("plateau.vein_leakage_length")[1]
    # holds at best if the drawn sheets reach the line, or if sheets as long as any swept could offer its voltage
    status, tail = _against_the_chain(ledger, r, field, field.high >= needed.low or length >= gather.low)
    thin, thick = ledger.rng("elec.ore_sheet_thickness")
    shallow, deep = ledger.rng("elec.ore_sheet_depth")
    return status, (
        f"With two vertical sheets of the most conductive hematite measured ({ledger.rng(ORE_RESISTIVITY)[0]} ohm m) "
        f"in line with the far field and ending at the base, the conduction model puts {ratio.value:.1f} times the "
        f"far field in the King's Chamber granite or at the summit ({ratio.low:.1f} to {ratio.high:.1f} over sheets "
        f"{thin:g} to {thick:g} m thick, {shallow:.0f} to {deep:.0f} m deep and up to {length:.0f} m long, all "
        f"assumed), against {plain.value:.1f} without sheets: {field.high:.2f} V/m at the most, which {tail} Sheets "
        f"would have to gather the far field over {gather.low:.1e} m to offer the pulse chain its voltage.")


def _s06(ledger, r):
    peak, mean, needed, sustained = (r[f"electro.{name}"] for name in (
        "lightning_granite_field", "lightning_granite_mean_field", "needed_field_gas_solid", "needed_field_sustained"))
    multiple, shortfall, skin = (r[f"electro.{name}"] for name in
                                 ("lightning_conduction_multiple", "lightning_shortfall", "chamber_skin_depths"))
    breakdown = ledger.q("em.air_breakdown_field")
    # The criterion: pass if the peak field in the granite exceeds what the chain needs; fail if the interior field is
    # screened to the conduction value of order kV/m or less. The model is a conduction model, so its field is the
    # conduction value by construction, and the favourable corner (tens of kV/m) is neither of order kV/m nor above
    # the need. Judgement call, named in the basis: the fail clause is read as the field staying below the need of
    # the pulse chain even at the favourable end (the design-maximum stroke, the most resistive masonry measured,
    # every input of that chain at its generous end). A return stroke is a single pulse (04 claim C6), so the pulse
    # chain is the one the claim is held to; the S07 chain's lower figure is given beside it.
    # The favourable end is capped at the air-breakdown field, the ledger's ceiling on any field beside a gas-filled
    # chamber, so under the pulse chain the verdict does not turn on how resistive the unmeasured core is taken to
    # be. The cap lies above what the sustained chain needs, and the basis says so.
    status = simkit.three_way(peak.low >= needed.high, min(peak.high, breakdown) >= needed.low)
    core, measured = r["electro.lightning_breakdown_resistivity"].value, ledger.rng("em.limestone_resistivity")[1]
    under_cap = "; the sustained chain's need lies under that cap" if sustained.low < breakdown else ""
    capped = (f" A core of {core:.0e} ohm m, {core / measured:.0f} times the most resistive masonry measured in place, "
              f"would bring that peak to the breakdown field, which caps it below the pulse chain's need{under_cap}."
              if needed.low > breakdown else "")
    head = (
        f"A stroke of {ledger.q(STROKES[0]) / 1e3:.0f} kA entering at the summit and spreading by steady conduction "
        f"puts {peak.value / 1e3:.1f} kV/m in the King's Chamber granite at the peak ({mean.value / 1e3:.1f} kV/m as "
        f"a volume mean), {multiple.value:.1f} times the even-spreading conduction value, and "
        f"{peak.high / 1e3:.0f} kV/m at the favourable corner of the ranges, the {ledger.rng(STROKES[1])[1] / 1e3:.0f} "
        f"kA design maximum in the most resistive masonry measured ({peak.low:.0f} V/m at the least). ")
    ceiling = (f"{needed.low / breakdown:.1f} times the {breakdown:.0e} V/m at which air breaks down"
               if needed.low > breakdown else f"below the {breakdown:.0e} V/m at which air breaks down")
    induction = (f" The chamber lies {skin.value:.1f} skin depths ({skin.low:.1f} to {skin.high:.1f}) inside the "
                 "nearest face, and induction, left out here, lowers the field there further.")
    if status == "fail":
        even_low, even_high = ledger.rng("em.piezo_field_lightning")  # 04's even-spreading estimate
        beside = (f"{sustained.low / peak.high:.0f} times that corner" if sustained.low > peak.high
                  else "which that corner reaches")
        beside += (" and below the breakdown field" if sustained.low < breakdown
                   else f" and {sustained.low / breakdown:.1f} times the breakdown field")
        return status, head + (
            f"{_pulse_chain(ledger)} needs {needed.low:.1e} V/m with every input at its generous end to reach a "
            f"documented acoustic effect, {shortfall.low:.0f} times the {peak.high / 1e3:.0f} kV/m of that corner and "
            f"{ceiling}. {_sustained_chain(ledger)} reaches the same effect at {sustained.low:.1e} V/m with every "
            f"input at its generous end, {beside}; a return stroke is a single pulse (04 claim C6), so the claim is "
            "held to the pulse chain. The criterion's fail clause, a field screened to the conduction value of order kV/m "
            "or less, is read as the field staying below the pulse chain's need at the favourable end, the order "
            f"kV/m being 04's own estimate of the conduction value ({even_low / 1e3:.2f} to {even_high / 1e3:.0f} "
            "kV/m by even spreading): a judgement call. In this model the field in the granite is the conduction "
            "value by construction."
            + capped + induction)
    if status == "pass":
        return status, head + (
            f"That exceeds the {needed.high:.1e} V/m that {_pulse_chain(ledger)} needs with every input at its "
            "least generous end to reach a documented acoustic effect." + induction)
    return status, head + (
        f"{_pulse_chain(ledger)} needs {needed.low:.1e} to {needed.high:.1e} V/m to reach a documented acoustic "
        f"effect ({ceiling} at the low end), which the field reaches over part of the ranges of the inputs only."
        + induction)


def _e13(ledger, r):
    names = list(rooms.ROOMS)
    decay, quality, mode = ({room: r[f"electro.{kind}_{room}"] for room in names}
                            for kind in ("decay_time", "modal_q", "lowest_mode"))
    decay_lead, quality_lead = r["electro.decay_lead"], r["electro.quality_lead"]
    open_decay, open_quality = r["electro.decay_lead_open"], r["electro.quality_lead_open"]
    # Judgement call: "ranks first" is read as first in both measures the criterion names. A lead above 1 is first.
    status = simkit.three_way(decay_lead.low > 1 and quality_lead.low > 1, decay_lead.high > 1 and quality_lead.high > 1)

    def rank(measure):
        ordered = sorted(names, key=lambda room: -measure[room].value)
        return ("first", "second", "last")[ordered.index("antechamber")]

    def listed(measure, unit, digits):
        return ", ".join(f"{rooms.ROOMS[room]['label']} {measure[room].value:.{digits}f}{unit}" for room in names)

    head = (
        "As hard-walled boxes with one assumed wall absorption, the three rooms decay at "
        f"{mode['antechamber'].value:.0f} Hz in: {listed(decay, ' s', 1)}; the quality factors of their lowest modes "
        f"({', '.join(f'{mode[room].value:.1f}' for room in names)} Hz) are: {listed(quality, '', 0)}. The antechamber "
        f"ranks {rank(decay)} of three in decay time, with {decay_lead.value:.2f} of the longest other "
        f"({decay_lead.low:.2f} to {decay_lead.high:.2f} over the ranges of the inputs), and {rank(quality)} in modal "
        f"quality factor, with {quality_lead.value:.2f} of the highest other ({quality_lead.low:.2f} to "
        f"{quality_lead.high:.2f}). ")
    if status == "fail":
        cause = [name for name, lead in (("decay time", decay_lead), ("modal quality factor", quality_lead))
                 if lead.high <= 1]
        return status, head + (
            f"It is never first in {' or in '.join(cause)}, so it does not rank first in both, the reading this rule "
            "takes of the criterion as a judgement call; the decay times go as volume over wall area, whatever the "
            f"absorption the rooms share. With the passage mouths open it falls to {open_decay.value:.2f} of the "
            f"longest decay and {open_quality.value:.2f} of the highest quality factor. No acoustic measurement of the "
            "antechamber exists to check the model.")
    if status == "pass":
        return status, head + "It stays first in both over the whole of the ranges, so the model ranks it first."
    return status, head + (
        "Over the ranges of the inputs it is first in both measures at the favourable end only, so the ranking "
        "turns on dimensions and absorptions that are not known well enough.")


RULES = {"S04": _s04, "E21": _e21, "S06": _s06, "E13": _e13}


def verdicts(ledger: Ledger, results: dict[str, Result]) -> dict[str, tuple[str, str]]:
    return {claim: rule(ledger, results) for claim, rule in RULES.items()}
