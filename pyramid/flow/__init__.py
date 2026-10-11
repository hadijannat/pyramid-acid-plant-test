"""Water and gas movement: reduced models that decide S03, S08, S13, S14 and S17 by their criteria.

Assumptions (also written to the manifest):
- Water moves through an opening by the orifice law, Q = Cd a sqrt(2 g h); vessels are prismatic.
- "The Gallery filled" means filled to its roof, as S12 and S13 say; the peak level is not otherwise stated.
- An opening below the falling water surface carries water, not gas. The Ascending Passage, the Queen's passage and the well shaft all meet the Gallery at its foot, so they stay covered until the Gallery is all but empty.
- The antechamber path with the slabs down is one opening, the grooves plus the leak round the slabs, in series with the two King's Chamber shafts; the King's Chamber itself is gas-tight apart from these.
- Gas is incompressible air at the ledger's density, moving at a steady rate, the Gallery volume over the drain time; the suction is capped at what a hanging water column can apply (02 section 4.4).
- Masonry joints leak gas as laminar slots from air-filled masonry at outside pressure; a gas-tight Gallery is what the tight end of the joint aperture approaches.
- The chamber behind Davison's passage is closed and only gives up the gas its pressure drop releases.
- Sulfur dioxide fills the King's Chamber pure, as S03 and S13 say, and is well mixed; it leaves by diffusion up the shafts and by a wind-driven through-flow that must lift the dense gas up the leeward shaft. Gusts, the breathing of the chamber with the barometer and temperature differences are not modelled.
"""
from pyramid.flow import gas, hydraulics, retention  # noqa: F401  (importing them registers their quantities)
from pyramid.flow.network import all_results  # noqa: F401
from pyramid.ledger import Ledger
from pyramid.screening import DAY, YEAR, Result
from pyramid.simkit import corners, three_way

ASSUMPTIONS = [line[2:] for line in __doc__.splitlines() if line.startswith("- ")]


def _at(ledger: Ledger, inputs) -> dict[str, float]:
    return {id: ledger.q(id) for id in inputs}


def _span(result: Result, scale: float = 1.0, digits: int = 0) -> str:
    """'value (low to high)' of a result, scaled and rounded for a sentence."""
    return f"{result.value * scale:.{digits}f} ({result.low * scale:.{digits}f} to {result.high * scale:.{digits}f})"


def _s03(ledger, r):
    half, slow = r["flow.retention_half_time"], r["flow.diffusion_half_time"]
    head, speed, ratio = r["flow.dense_gas_head"], r["flow.flush_wind_speed"], r["flow.so2_density_ratio"]
    shortest, longest = ledger.rng("flow.delivery_to_draw_interval")
    strongest = ledger.rng("flow.wind_speed")[1]
    # Judgement call: the criterion and 00 section 7 item 5 set no measure of "remains". It is read as at least
    # half the charge still being in the chamber at the draw, so the half-time is set against the interval.
    status = three_way(half.low >= longest, half.high >= shortest)
    text = (
        "With its shafts open a King's Chamber of pure sulfur dioxide loses half its charge by diffusion in "
        f"{_span(slow, 1 / YEAR)} years, and no wind below {_span(speed)} m/s can drive a through-flow, because "
        f"the gas, {ratio.value:.1f} times as dense as air, would have to be lifted up the leeward shaft against "
        f"{_span(head)} Pa. "
    )
    interval = ("the interval between delivery and draw, which the hypothesis does not state and which is taken "
                f"as {shortest / 60:.0f} minutes to {longest / DAY:.0f} days")
    reading = "Remaining is read as half the charge still being there at the draw"
    if status == "pass":
        return status, text + (
            f"Even in a wind of {strongest:.0f} m/s the half-time is {half.low / DAY:.0f} days or more, no shorter "
            f"than {interval}. {reading}."
        )
    if status == "fail":
        return status, text + (
            f"Yet the half-time is {half.high / 60:.0f} minutes at the most, shorter than {interval}. {reading}."
        )
    return status, text + (
        f"In the {strongest:.0f} m/s at the top of the assumed wind range the half-time falls to "
        f"{half.low / 60:.0f} minutes, against {interval}; a charge diluted to a tenth is held only below "
        f"{speed.value * 0.1 ** 0.5:.0f} m/s. {reading}, and the hypothesis states neither the composition of the "
        "charge nor what keeps it in."
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
    return "conditional", (
        "The highest documented water, the Old Kingdom flood peak or today's water table, stands "
        f"{_span(gap)} m below the foot of the Descending Passage, so none reaches the Subterranean Chamber and the "
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


def _s14(ledger, r):
    share, dp = r["flow.shaft_share"], r["flow.draw_pressure"]
    absent, flip = r["flow.slabs_absent_share"], r["flow.joint_aperture_half"]
    q = _at(ledger, share.inputs)
    grooves = gas.draw(q, area=q["ante.groove_connected_area"])[1]
    fastest, slowest = ledger.rng("hydro.drain_time")
    tight, wide = ledger.rng("hydro.joint_aperture")
    # The same share with the path held open at its ledger area: what the leaks and the drain rate do by
    # themselves, apart from whether a path exists at all, which is S15's question.
    area = gas.opening_area(q)
    _, open_low, open_high = corners(ledger, share.inputs, lambda v: gas.draw(v, area=area)[1])
    turn = f", or the drain slower than {gas.flip_drain_time(q) / 60:.0f} minutes" if area > 0 else ""
    # "Most" is more than half. The hypothesis states no drain rate, so the rule sweeps the three rates 02
    # evaluates, as Tier 0 does for S16, and the sentence names the rate at which the share crosses one half.
    status = three_way(share.low > 0.5, share.high > 0.5)
    return status, (
        f"Draining the Gallery in {q['hydro.drain_time'] / 3600:.0f} h through {area * 1e4:.0f} cm2 "
        f"of grooves and slab clearance, with masonry joints of {q['hydro.joint_aperture'] * 1e3:.2f} mm leaking, "
        f"{100 * share.value:.0f} percent of the replacement gas comes down the King's Chamber shafts, at a "
        f"pressure difference of {dp.value:.0f} Pa. Over drain times of {fastest / 60:.0f} minutes to "
        f"{slowest / 3600:.0f} h and joints of {tight * 1e3:.2f} to {wide * 1e3:.2f} mm the share runs from "
        f"{100 * open_low:.0f} to {100 * open_high:.0f} percent with that path open, and from "
        f"{100 * share.low:.0f} percent if the path is shut, as blind grooves and seated slabs would leave it; the "
        f"pressure difference runs from {dp.low:.0f} Pa to {dp.high / 1e3:.0f} kPa, the most a water column can "
        f"pull. Through the grooves alone the share is {100 * grooves:.0f} percent and with no slab in the passage "
        f"{100 * absent.value:.0f} percent. More than half comes down the shafts with the joints tighter than "
        f"{flip.value * 1e3:.2f} mm{turn}; the hypothesis states neither a drain rate nor how the Gallery is made "
        "gas-tight."
    )


def _s17(ledger, r):
    tight, leaky = r["flow.antechamber_share"], r["flow.slabs_absent_share"]
    down, down_leaky = r["flow.slabs_down_share"], r["flow.shaft_share"]
    wedge, flip = r["flow.foot_wedge_share"], r["flow.joint_aperture_nine_tenths"]
    narrow, wide = ledger.rng("hydro.joint_aperture")
    area = gas.opening_area(_at(ledger, down.inputs))
    # Judgement calls. "The openings as surveyed" have no slab in the antechamber passage (02 section 5.3), so the
    # status follows the share through that passage; whether a path exists with the slabs down is S15's question
    # and is reported, not judged. And 01 calls the syringe "a leakage question" (summary and claim 4), so gas
    # leaking through the joints counts against the passage at the unfavourable end, though no survey lists a
    # joint as an opening: worst is the leaking Gallery, best the gas-tight one.
    status = three_way(leaky.low > 0.9, tight.high > 0.9)
    return status, (
        "Of the Gallery's five surveyed openings the Ascending Passage, the Queen's passage and the well shaft meet "
        f"it at its foot and stay under water until {100 * wedge.high:.1f} percent of it or less is left, and "
        f"Davison's passage ends in a closed chamber. So with gas-tight masonry {_span(tight, 100, 1)} percent of "
        "the displaced volume is drawn through the antechamber passage as surveyed, with no slab in it. Counting "
        f"gas that leaks in through masonry joints of {narrow * 1e3:.2f} to {wide * 1e3:.2f} mm, the leakage that "
        f"01 leaves open for the syringe, the share is {_span(leaky, 100)} percent and passes 90 percent with joints "
        f"tighter than {_span(flip, 1e3, 2)} mm. With the slabs of the hypothesis down the two shares are "
        f"{100 * down.value:.1f} and {100 * down_leaky.value:.0f} percent through {area * 1e4:.0f} cm2 of grooves "
        "and slab clearance, and nothing if that path is shut, which is the question of S15."
    )


RULES = {"S03": _s03, "S08": _s08, "S13": _s13, "S14": _s14, "S17": _s17}


def verdicts(ledger: Ledger, results: dict[str, Result]) -> dict[str, tuple[str, str]]:
    return {claim: rule(ledger, results) for claim, rule in RULES.items()}
