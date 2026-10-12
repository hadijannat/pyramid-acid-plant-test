"""Water and gas movement: reduced models that decide S03, S08, S13, S14 and S17 by their criteria.

Assumptions (also written to the manifest):
- Water moves through an opening by the orifice law, Q = Cd a sqrt(2 g h); vessels are prismatic.
- "The Gallery filled" means filled to its roof, as S12 and S13 say; the peak level is not otherwise stated.
- An opening below the falling water surface carries water, not gas. The Ascending Passage, the Queen's passage and the well shaft all meet the Gallery at its foot, so they stay covered until the Gallery is all but empty.
- The antechamber opening lies under the full Gallery's surface too: until the surface has fallen to the opening's top, gas enters there only by the suction in excess of the water standing over it, and from then on freely. The Gallery is its surveyed section carried along the slope; the water that enters the antechamber meanwhile is S13's matter.
- The antechamber path with the slabs down is one opening, the grooves plus the leak round one slab though three stand one after another, in series with the two King's Chamber shafts; the King's Chamber itself is gas-tight apart from these.
- Gas is incompressible air at the ledger's density, moving at a steady rate, the Gallery volume over the drain time; the suction is capped at what a hanging water column can apply (02 section 4.4).
- Masonry joints leak gas as laminar slots, over their whole length from the start of the draw, from air-filled masonry at outside pressure; a gas-tight Gallery is what the tight end of the joint aperture approaches.
- The chamber behind Davison's passage is closed and only gives up the gas its pressure drop releases; what it lends while the suction is high and takes back later is left out.
- Sulfur dioxide fills the King's Chamber pure, as S03 and S13 say, and is well mixed; it leaves by diffusion up the shafts and by a wind-driven through-flow that must lift the dense gas up the leeward shaft. Gusts, the breathing of the chamber with the barometer and temperature differences are not modelled.
- The same charge runs out by its own weight through an opening at the chamber's floor that has no water beyond it, under the head of the gas below the shaft mouths, where the air comes in. S03 counts this for the antechamber path, as an unmixed layer, with the Gallery open to the air; the floor inlet by which the gas arrives is taken as closed, which the hypothesis does not say. With the Gallery closed only an exchange through the one opening is left, hours to more than a day; with water over the opening nothing drains, and S13's water pushes out at most the 16 percent of the charge below the shaft mouths.
"""
from pyramid.flow import gas, hydraulics, retention  # noqa: F401  (importing them registers their quantities)
from pyramid.flow.network import all_results  # noqa: F401
from pyramid.ledger import Ledger
from pyramid.screening import DAY, YEAR, G, Result
from pyramid.simkit import corners, three_way

ASSUMPTIONS = [line[2:] for line in __doc__.splitlines() if line.startswith("- ")]


def _at(ledger: Ledger, inputs) -> dict[str, float]:
    return {id: ledger.q(id) for id in inputs}


def _span(result: Result, scale: float = 1.0, digits: int = 0) -> str:
    """'value (low to high)' of a result, scaled and rounded for a sentence."""
    return f"{result.value * scale:.{digits}f} ({result.low * scale:.{digits}f} to {result.high * scale:.{digits}f})"


def _pressure(pascals: float) -> str:
    return f"{pascals:.0f} Pa" if pascals < 1e4 else f"{pascals / 1e3:.0f} kPa"


def _s03(ledger, r):
    half, slow = r["flow.retention_half_time"], r["flow.diffusion_half_time"]
    head, speed, ratio = r["flow.dense_gas_head"], r["flow.flush_wind_speed"], r["flow.so2_density_ratio"]
    shortest, longest = ledger.rng("flow.delivery_to_draw_interval")
    strongest = ledger.rng("flow.wind_speed")[1]
    # The gas path of the hypothesis leaves the chamber at its floor, and a gas this dense runs out of a floor
    # opening by its own weight, through the antechamber path: at its fastest at the unfavourable end, shut (and
    # the time without end) at the favourable one.
    path = ("ante.groove_connected_area", "flow.slab_leak_area")
    drain, drain_low, drain_high = corners(ledger, retention.DRAIN_IDS + path,
                                           lambda v: retention.drain_half_time(v, gas.opening_area(v)))
    # That loss and the shafts' run together, in a storm with the path open, so their rates add and the charge
    # lasts a shorter time than under either. 1 / inf is 0.0: the shut path leaves the shafts' time.
    kept_low = 1 / (1 / half.low + 1 / drain_low)
    kept_high = 1 / (1 / half.high + 1 / drain_high)
    # Judgement call: the criterion and 00 section 7 item 5 set no measure of "remains". It is read as at least
    # half the charge still being in the chamber at the draw, so the half-time is set against the interval.
    status = three_way(kept_low >= longest, kept_high >= shortest)
    text = (
        "With its shafts open a King's Chamber of pure sulfur dioxide loses half its charge by diffusion in "
        f"{_span(slow, 1 / YEAR)} years, and no wind below {_span(speed)} m/s can drive a through-flow, because "
        f"the gas, {ratio.value:.1f} times as dense as air, would have to be lifted up the leeward shaft against "
        f"{_span(head)} Pa. "
    )
    if drain < float("inf"):
        slowest = "never with the path shut" if drain_high == float("inf") else f"{drain_high / 60:.0f} at the slowest"
        text += (
            "The same weight carries it out of an opening at the chamber's floor while no water stands beyond it "
            "and the Gallery is open to the air, which the hypothesis does not say for the time before the fill: "
            f"through the {gas.opening_area(_at(ledger, path)) * 1e4:.0f} cm2 of grooves and one slab's clearance "
            "in the antechamber, the gas path of the hypothesis, half the charge is gone in about "
            f"{drain / 60:.0f} minutes ({drain_low / 60:.0f} at the fastest, {slowest}). "
        )
    interval = ("the interval between delivery and draw, which the hypothesis does not state and which is taken "
                f"as {shortest / 60:.0f} minutes to {longest / DAY:.0f} days")
    reading = "Remaining is read as half the charge still being there at the draw (a judgement call)"
    if status == "pass":
        return status, text + (
            f"Even in a wind of {strongest:.0f} m/s the half-time is {kept_low / DAY:.0f} days or more, no shorter "
            f"than {interval}. {reading}."
        )
    if status == "fail":
        return status, text + (
            f"Yet the half-time is {kept_high / 60:.0f} minutes at the most, shorter than {interval}. {reading}."
        )
    if half.low < longest:
        both = (f", and to {kept_low / 60:.0f} with the floor opening draining at its fastest as well"
                if drain_low < float("inf") else "")
        storm = (f"In the {strongest:.0f} m/s at the top of the assumed wind range the half-time falls to "
                 f"{half.low / 60:.0f} minutes{both}, against {interval}")
    else:
        storm = (f"Up to the {strongest:.0f} m/s of the assumed wind range the shafts keep half the charge for "
                 f"{half.low / YEAR:.0f} years or more, against {interval}")
    return status, text + (
        f"{storm}; a charge diluted to a tenth is held only below {speed.value * 0.1 ** 0.5:.0f} m/s, and below "
        "the wind that lifts it the model loses gas up the shafts by diffusion alone, which is a limit of the "
        f"model. {reading}, and the hypothesis states neither the composition of the charge nor what keeps it in."
    )


def _s08(ledger, r):
    gap, level = r["flow.documented_water_below_chamber"], r["flow.reservoir_level_vessels"]
    volume, prime, inflow = r["flow.fill_volume"], r["flow.prime_volume"], r["flow.fill_inflow"]
    if gap.high <= 0:
        return "pass", (
            f"The highest documented water stands {-gap.high:.0f} m or more above the foot of the Descending "
            "Passage, so water reaches the Subterranean Chamber without an assumed reservoir; one fill takes "
            f"{_span(volume)} m3."
        )
    # The criterion makes a pass depend on an assumed reservoir, and 02 section 5.3 lists that reservoir as the
    # hypothesis-favourable alternative to the evidence-based boundary. So documented levels that deliver nothing
    # do not fail the claim: it holds on the assumption, and the rule reports what must be assumed.
    foot = ledger.q("dp.south_end.z")
    floor = foot - (ledger.q("sub.roof_centre.z") - ledger.q("sub.floor_depth_pit"))
    pit = foot - ledger.rng("pit.original_bottom.z")[0]
    above = ", still above that water" if gap.low > pit else ""
    perched = ledger.rng("hydro.perched_water_asl")
    return "conditional", (
        "The highest water documented at Khufu or beside it, the Old Kingdom flood peak or today's water table, "
        f"stands {_span(gap)} m below the foot of the Descending Passage; the chamber's deepest floor lies "
        f"{floor:.1f} m and the pit's original bottom up to {pit:.1f} m lower than that foot{above}. Perched water "
        f"at {perched[0]:.0f} to {perched[1]:.0f} m above sea level is interpreted from geophysics toward Menkaure "
        "and none is reported at Khufu, so it is not counted. No documented water therefore reaches the "
        "Subterranean Chamber, and the "
        "step holds only for a reservoir that is assumed: the hypothesis names one without level, volume or inlet, "
        "and nothing on site attests it. It must stand at pavement level or above and enter by a conduit that no "
        f"survey shows, or {ledger.q('dp.entrance.z'):.1f} m above the pavement to use the entrance, the only "
        "surveyed opening; to fill the Gallery by communicating vessels alone it must stand "
        f"{ledger.q('gg.roof_top.z'):.1f} m above the pavement, {_span(level)} m above sea level. One fill takes "
        f"{_span(volume)} m3, an inflow of {inflow.value:.2f} m3/s if it takes "
        f"{ledger.q('flow.fill_time') / 3600:.0f} h, after {_span(prime)} m3 to prime the Subterranean Chamber and "
        "the Descending Passage up to the pavement."
    )


def _s13(ledger, r):
    head, pressure = r["flow.antechamber_water_head"], r["flow.kc_holdback_pressure"]
    rate, time = r["flow.kc_ingress_rate"], r["flow.kc_flood_time"]
    vent, lock = r["flow.kc_vent_time"], r["flow.kc_gaslock_depth"]
    # The claim and 00 section 5 item 9: the hypothesis states no drain route, so the criterion's last clause is
    # unmet and the claim cannot pass. It fails outright where the first clause fails whatever the route.
    if head.low <= 0:
        return "undefined", (
            f"With the Gallery full to its roof the water stands {_span(head, digits=1)} m above the antechamber "
            "floor, so it need not enter the King's Chamber, but the hypothesis states no drain route, which the "
            "criterion requires."
        )
    grooves = ledger.q("ante.groove_connected_area")
    by_grooves = ""
    if grooves > 0:
        hours = hydraulics.flood_time(_at(ledger, time.inputs), grooves) / 3600
        by_grooves = f", through the {grooves * 1e4:.0f} cm2 of the grooves alone after {hours:.1f} h"
    return "fail", (
        f"With the Gallery full to its roof the water stands {_span(head, digits=1)} m above the antechamber floor "
        f"and presses with {pressure.value / 1e3:.0f} kPa, so an opening that passes gas passes water: past slabs "
        f"as loose as the surviving fragment {_span(rate, digits=2)} m3/s enter and the water stands at the King's "
        f"Chamber shaft mouths after {_span(time, 1 / 60)} minutes{by_grooves}, and with the path shut no gas "
        f"passes either. Holding the water back would take {pressure.value / 1e3:.0f} kPa of gas pressure, which "
        f"the open shafts release in {vent.value:.0f} s, and with the shafts shut the water still rises "
        f"{lock.value:.1f} m or more in the chamber. Water stays out only if the fill stops at the antechamber "
        f"floor, {ledger.q('ante.floor.z'):.1f} m above the pavement, and the hypothesis states no drain route."
    )


def _under_water(ledger, r) -> tuple[dict[str, float], float, str]:
    """The draw's inputs at their ledger values, the water pressure over the antechamber opening with the Gallery
    full, in Pa, and the clause that says what it does to the draw."""
    under = r["flow.submerged_share"]
    q = _at(ledger, r["flow.shaft_share"].inputs)
    head = q["hydro.water_density"] * G * gas.opening_depth(q)
    return q, head, (
        f"lies {gas.opening_depth(q):.1f} m under the surface of the full Gallery, and until "
        f"{_span(under, 100, 1)} percent of the Gallery has drained gas enters it only where the suction exceeds "
        f"the water standing over it, {head / 1e3:.0f} kPa at the start"
    )


def _s14(ledger, r):
    share, dp, start = r["flow.shaft_share"], r["flow.draw_pressure"], r["flow.start_pressure"]
    absent, flip = r["flow.slabs_absent_share"], r["flow.joint_aperture_half"]
    q, head, under_water = _under_water(ledger, r)
    grooves = gas.draw(q, area=q["ante.groove_connected_area"])[1]
    one_after_another = gas.series_area(q | _at(ledger, ("ante.slot_count",)))
    fastest, slowest = ledger.rng("hydro.drain_time")
    tight, wide = ledger.rng("hydro.joint_aperture")
    short, long = ledger.rng("flow.joint_path_length")
    # The same share with the path held open at its ledger area: what the leaks and the drain rate do by
    # themselves, apart from whether a path exists at all: S15 decides that for the grooves, and no claim decides
    # whether the slabs seat tight.
    area = gas.opening_area(q)
    _, open_low, open_high = corners(ledger, gas.SWEPT, lambda v: gas.draw(q | v, area=area)[1])
    turn = gas.flip_drain_time(q, fastest, slowest) if area > 0 else None
    turn = f", or the drain {turn[1]} than {turn[0] / 60:.0f} minutes" if turn else ""
    alone = ", when the joints alone supply the pocket," if start.value < head else ""
    most = ", the most a water column can pull" if start.high >= gas.suction_cap(q) else ""
    # "Most" is more than half. The hypothesis states no drain rate, so the rule sweeps the three rates 02
    # evaluates, as Tier 0 does for S16, and the sentence names the rate at which the share crosses one half.
    status = three_way(share.low > 0.5, share.high > 0.5)
    return status, (
        f"The antechamber opening {under_water}; where the path past the slabs is open, that water runs through it "
        f"into the King's Chamber meanwhile, which S13 judges. Draining the Gallery in "
        f"{q['hydro.drain_time'] / 3600:.0f} h "
        f"through {area * 1e4:.0f} cm2 of grooves and one slab's clearance, with masonry joints of "
        f"{q['hydro.joint_aperture'] * 1e3:.2f} mm leaking along a path of {q['flow.joint_path_length']:.1f} m, "
        f"{100 * share.value:.0f} percent of the replacement gas comes down the King's Chamber shafts; the "
        f"pressure difference is {_pressure(start.value)} at the start{alone} and {_pressure(dp.value)} once the "
        f"opening is clear. Over drain times of {fastest / 60:.0f} minutes to {slowest / 3600:.0f} h, joints of "
        f"{tight * 1e3:.2f} to {wide * 1e3:.2f} mm and joint paths of {short:.1f} to {long:.1f} m the share runs "
        f"from {100 * open_low:.0f} to {100 * open_high:.0f} percent with that path open, and from "
        f"{100 * share.low:.0f} percent if the path is shut, as blind grooves and seated slabs would leave it; the "
        f"pressure difference runs from {_pressure(dp.low)} to {_pressure(start.high)}{most}. "
        f"Through the grooves alone the share is {100 * grooves:.0f} percent, through the three slabs' "
        f"clearances one after another, which pass what {one_after_another * 1e4:.0f} cm2 passes, "
        f"{100 * gas.draw(q, area=one_after_another)[1]:.0f} percent, and with no slab in the passage "
        f"{100 * absent.value:.0f} percent. More than half comes down the shafts with the joints tighter than "
        f"{flip.value * 1e3:.2f} mm{turn}; the hypothesis states neither a drain rate nor how the Gallery is made "
        "gas-tight."
    )


def _s17(ledger, r):
    tight, leaky = r["flow.antechamber_share"], r["flow.slabs_absent_share"]
    down, down_leaky = r["flow.slabs_down_share"], r["flow.shaft_share"]
    wedge, flip = r["flow.foot_wedge_share"], r["flow.joint_aperture_nine_tenths"]
    q, _, under_water = _under_water(ledger, r)
    narrow, wide = ledger.rng("hydro.joint_aperture")
    short, long = ledger.rng("flow.joint_path_length")
    fastest, slowest = ledger.rng("hydro.drain_time")
    area = gas.opening_area(q)
    # Judgement calls, both named in the basis. "The openings as surveyed" have no slab in the antechamber passage
    # (02 section 5.3), so the status follows the share through that passage; whether a path exists with the slabs
    # down is reported, not judged: S15 decides it for the grooves, and no claim decides whether the slabs seat
    # tight. And 01 calls the syringe "a leakage question" (summary and claim 4), so gas leaking through the joints
    # counts against the passage at the unfavourable end, though no survey lists a joint as an opening: worst is
    # the leaking Gallery, best the gas-tight one. That second call decides the word: the surveyed openings alone
    # give the status below.
    status = three_way(leaky.low > 0.9, tight.high > 0.9)
    surveyed_alone = {"pass": "pass", "fail": "fail", "conditional": "stay conditional"}[
        three_way(tight.low > 0.9, tight.high > 0.9)]
    return status, (
        "Of the Gallery's five surveyed openings the Ascending Passage, the Queen's passage and the well shaft meet "
        f"it at its foot and stay under water until {100 * wedge.high:.1f} percent of it or less is left, and "
        f"Davison's passage ends in a closed chamber. The antechamber opening {under_water}. With gas-tight "
        f"masonry nothing else can enter, so {_span(tight, 100, 1)} percent of the displaced volume is drawn "
        "through the antechamber passage as surveyed, with no slab in it. Counting gas that leaks in through "
        f"{q['hydro.joint_length']:.0f} m of masonry joints of {narrow * 1e3:.2f} to {wide * 1e3:.2f} mm, from "
        f"air-filled masonry at outside pressure {short:.1f} to {long:.1f} m behind the Gallery's face, a leak "
        "that is assumed and that 01 leaves open for the syringe, the share is "
        f"{_span(leaky, 100)} percent over drain times of {fastest / 60:.0f} minutes to {slowest / 3600:.0f} h and "
        f"passes 90 percent with joints tighter than {_span(flip, 1e3, 2)} mm or somewhat wider, the model letting "
        "neither the pocket's gas thin nor Davison's chamber lend. Counting that leak against 'the openings as "
        "surveyed', though no survey lists a joint as an opening, is a judgement call: with the surveyed openings "
        f"alone the claim would {surveyed_alone}. That the status follows the passage as surveyed, with no slab in "
        "it, is a second one: with the slabs of the hypothesis "
        f"down the two shares are {100 * down.value:.1f} and {100 * down_leaky.value:.0f} percent through "
        f"{area * 1e4:.0f} cm2 of grooves and one slab's clearance, and nothing if that path is shut, which takes "
        "blind grooves, the question of S15, and slabs seated tight as well, which no claim decides."
    )


RULES = {"S03": _s03, "S08": _s08, "S13": _s13, "S14": _s14, "S17": _s17}


def verdicts(ledger: Ledger, results: dict[str, Result]) -> dict[str, tuple[str, str]]:
    return {claim: rule(ledger, results) for claim, rule in RULES.items()}
