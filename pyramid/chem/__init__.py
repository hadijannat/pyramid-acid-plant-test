"""Chemistry and feed: reduced models that decide claims S01, E01, S19, S22 and S23.

transfer (gas into water), aqueous (speciation, oxidation, the gas the water cannot take), walls (limestone and
its gypsum layer) and feed (hydrogen sulfide) each list their assumptions. Every quantity here is a pure function
of ledger numbers, evaluated at the ledger values and at every corner of their ranges; each is monotone in each
input, so the corners are its extremes.
"""
from pyramid import screening
from pyramid.chem import aqueous, feed, transfer, walls
from pyramid.ledger import Ledger
from pyramid.screening import YEAR, Result
from pyramid.simkit import corners, three_way

HOUR = 3600  # seconds in an hour, for readable sentences
CYCLES = 10  # the criterion of S23 asks for ten fill and drain cycles
NOTHING = 1e-9  # a share of the gas below this is rounding, not gas

# One row per quantity: (id, label, unit, formula, inputs, function), as Tier 0 lays them out.
QUANTITIES = [
    ("chem.capture_share", "Share of the sulfur dioxide that reaches the water of the half-full Gallery in one cycle",
     "1", "y = (1 - exp(-t / tau)) / (1 + 1 / m); tau = V / (2 K A (1 + 1 / m)); 1 / K = 1 / k_g + 1 / (m k_L); "
     "m = H R T; A = S / tan(a)", transfer.CAPTURE, transfer.capture_share),
    ("chem.capture_equilibrium", "Share of the largest batch the water of the half-full Gallery holds at equilibrium",
     "1", "n_gas / V_gas = a0([H+]) c / (H R T), with [H+] from the charge balance of the dissolved sulfur(IV)",
     aqueous.EQUILIBRIUM, aqueous.capture_at_equilibrium),
    ("chem.uptake_pace", "Uptake rate of sulfur dioxide over the rate at which a one-cycle fill displaces the gas",
     "1", "Da = K A t / V_gallery", transfer.CAPTURE, transfer.uptake_pace),
    ("chem.oxidation_half_life", "Half-life of dissolved sulfur(IV) under the iron law at the batch's starting pH",
     "s", "t = ln 2 / (k [Fe(III)] a2([H+])); oxygen permitting", aqueous.OXIDATION, aqueous.half_life),
    ("chem.least_air", "Least share of air in the gas a full stroke draws into the Gallery",
     "1", "x = 1 - V_chamber / V_gallery", ("kc.volume", "gg.volume"), aqueous.least_air),
    ("chem.forced_back_least_air", "Share of the gas the rising water must push back, with the least air",
     "1", "f = x_N2 (1 - H_N2 R T) + leftover O2 less what dissolves; all SO2 dissolved, all usable O2 used",
     aqueous.GAS, lambda q: aqueous.forced_back(q, aqueous.least_air(q))),
    ("chem.forced_back_stoichiometric", "Share of the gas pushed back for the mixture with oxygen for all its sulfur",
     "1", "as chem.forced_back_least_air with x_air = 1 - 1 / (1 + 0.5 / x_O2)",
     aqueous.GAS, lambda q: aqueous.forced_back(q, aqueous.stoichiometric_air(q))),
    ("chem.air_without_pushback", "Largest share of air in the gas for which nothing need be pushed back",
     "1", "x = H_N2 R T / (1 - x_O2)", aqueous.GAS, aqueous.air_without_pushback),
    ("chem.sulfur_oxidisable_without_pushback", "Share of the sulfur that the oxygen of that much air can oxidise",
     "1", "y = x_O2 x / (0.5 (1 - x))", aqueous.GAS,
     lambda q: aqueous.sulfur_oxidisable(q, aqueous.air_without_pushback(q))),
    ("chem.gypsum_layer_per_cycle", "Gypsum layer that grows in one cycle on a wall bare at its start",
     "m", "d = sqrt(Vm D C t); C = 2 n_SO2 / V_gallery", walls.WALL, walls.layer_per_cycle),
    ("chem.fill_dissolves", "Gypsum layer one Gallery of fresh water dissolves in coming to saturation",
     "m", "d = s rho V_gallery Vm / A_wall", walls.WALL, walls.fill_dissolves),
    ("chem.still_fill_dissolves", "Gypsum layer a still fill of fresh water dissolves by diffusion alone in one cycle",
     "m", "d = 2 s rho sqrt(D_w t / pi) Vm", walls.WALL, walls.still_fill_dissolves),
    ("chem.saturating_margin", "What a saturating fill dissolves over the layer one cycle grows",
     "1", "chem.fill_dissolves / chem.gypsum_layer_per_cycle", walls.WALL, walls.saturating_margin),
    ("chem.still_margin", "What a still fill dissolves over the layer one cycle grows",
     "1", "chem.still_fill_dissolves / chem.gypsum_layer_per_cycle; the cycle time cancels",
     walls.WALL, walls.still_margin),
    ("chem.wall_loss_per_cycle", "Limestone lost in a cycle that starts with a bare wall",
     "m", "w = x c V_gallery Vc / A_wall + d Vc / Vm; x = min(1, (s rho / c)^2)", walls.WALL, walls.loss_per_cycle),
    ("chem.wall_loss_ten_cycles", "Limestone lost in ten cycles if every fill strips the layer",
     "m", "10 x chem.wall_loss_per_cycle", walls.WALL, lambda q: CYCLES * walls.loss_per_cycle(q)),
    ("chem.h2s_per_batch", "Hydrogen sulfide one full batch needs",
     "mol", "n = p V / (R T), a mole for each mole of sulfur dioxide", screening._SO2, feed.batch_moles),
    ("chem.h2s_mass_per_batch", "Mass of the hydrogen sulfide one full batch needs",
     "kg", "m = n M", feed.FEED, feed.batch_mass),
    ("chem.h2s_flux", "Hydrogen sulfide flux for one full batch per cycle",
     "mol/s", "F = n / t", feed.FEED, feed.flux),
    ("chem.h2s_mass_per_year", "Hydrogen sulfide for a year of full batches",
     "kg", "m = n M x one year / t", feed.FEED, feed.yearly_mass),
    ("chem.cave_air_per_batch", "Cave air at the analogue's ceiling that holds the sulfur of one batch",
     "m3", "V = V_chamber / x_H2S", feed.CAVE_AIR, feed.cave_air_per_batch),
]


def results(ledger: Ledger) -> dict[str, Result]:
    out = {}
    for id, label, unit, formula, inputs, fn in QUANTITIES:
        value, low, high = corners(ledger, inputs, fn)
        out[id] = Result(id, label, value, low, high, unit, formula, inputs)
    return out


def _cycle(ledger: Ledger) -> str:
    """The cycle time and its range, in words."""
    low, high = ledger.rng("rx.cycle_time")
    return (
        f"a cycle of {ledger.q('rx.cycle_time') / HOUR:.0f} h (the hypothesis states none; {low / HOUR:.0f} h to "
        f"{high / YEAR:.0f} yr is taken as its range)"
    )


def _s19(ledger, r):
    share, held = r["chem.capture_share"], r["chem.capture_equilibrium"]
    # The criterion's lines (03 section 4.4): pass from 90 percent, fail below 50 percent.
    status = three_way(share.low >= 0.90, share.high >= 0.50)
    still, stirred = ledger.rng("rx.kg_gas")
    head = (
        f"With the Gallery half full and {_cycle(ledger)}, {100 * share.value:.0f} percent of the sulfur dioxide "
        f"crosses the level surface into the water "
    )
    tail = (
        f" The water could hold {100 * held.value:.0f} percent at equilibrium, so the rate decides, and it "
        f"depends on the cycle time and on whether the gas over the water stands still or convects (gas-side "
        f"coefficient {1e3 * still:.3f} to {1e3 * stirred:.0f} mm/s, assumed), neither of which the hypothesis "
        "gives."
    )
    if status == "pass":
        return status, head + (
            f"({100 * share.low:.0f} percent at the least), at least the 90 percent from which the criterion passes "
            "the claim."
        ) + tail
    spread = f"({100 * share.low:.0f} to {100 * share.high:.0f} percent over the ranges of the inputs), "
    if status == "fail":
        return status, head + spread + "below the 50 percent under which the criterion fails the claim." + tail
    return status, head + spread + (
        "which over those ranges is neither always at the 90 percent from which the criterion passes the claim nor "
        "always under the 50 percent below which it fails it."
    ) + tail


def _s22(ledger, r):
    air, least, mixture = r["chem.least_air"], r["chem.forced_back_least_air"], r["chem.forced_back_stoichiometric"]
    limit, oxidisable, pace = (r["chem.air_without_pushback"], r["chem.sulfur_oxidisable_without_pushback"],
                               r["chem.uptake_pace"])
    # The criterion as written: uptake keeps pace, so that no gas is forced back. The unfavourable end is the gas
    # with the most air and the slowest uptake; the favourable end is the least air a full stroke admits.
    # Judgement call: the favourable end is not a gas without air, because S14, S15 and S17 put air in it.
    status = three_way(max(least.high, mixture.high) < NOTHING and pace.low >= 1,
                       least.low < NOTHING and pace.high >= 1)
    head = (
        f"A full stroke draws {ledger.q('gg.volume'):.0f} m3 of gas into the Gallery and the King's Chamber holds "
        f"{ledger.q('kc.volume'):.0f} m3, so at least {100 * air.value:.0f} percent of the gas over the water is "
        f"the outside air of S14 ({100 * air.low:.0f} percent at the least). "
    )
    if status != "fail":
        return status, head + (
            f"Its nitrogen and unused oxygen can dissolve in the rising water, and the sulfur dioxide is taken up at "
            f"{pace.value:.1f} times the rate at which the water displaces it ({pace.low:.2g} to {pace.high:.2g} "
            "times over the ranges of the inputs), "
        ) + ("so nothing is forced back at any end of the ranges."
             if status == "pass" else
             "so whether gas is forced back depends on the cycle time and the stirring, which the hypothesis does "
             "not give.")
    return status, head + (
        "Its nitrogen hardly dissolves: if all the sulfur dioxide dissolved, the oxidation used every mole of "
        "oxygen it could and the water arrived free of dissolved gas, the rising water would still push "
        f"{100 * least.value:.0f} percent of the gas back ({100 * least.low:.0f} to {100 * least.high:.0f} percent "
        f"over the ranges of the inputs), and {100 * mixture.value:.0f} percent of a mixture that carries the oxygen "
        f"for all its sulfur. Nothing is pushed back only if air is under {100 * limit.value:.1f} percent of the gas "
        f"({100 * limit.high:.1f} percent at most), which brings oxygen for {100 * oxidisable.value:.1f} percent of "
        "the sulfur; the hypothesis states no gas fraction and no stroke."
    )


def _s23(ledger, r):
    layer, fill = r["chem.gypsum_layer_per_cycle"], r["chem.fill_dissolves"]
    saturating, still = r["chem.saturating_margin"], r["chem.still_margin"]
    ten, share = r["chem.wall_loss_ten_cycles"], r["t0.gypsum_saturation_loss"]
    # The criterion as written: fail if the layer is stripped each cycle. The unfavourable end is a fill that comes
    # to saturation (03 check V17), the favourable end a fill that stands still and dissolves by diffusion alone.
    status = three_way(saturating.high < 1, still.low < 1)
    head = (
        f"Fresh water lets bare limestone neutralise {100 * share.value:.0f} percent of the strongest batch before "
        f"gypsum can form (Tier 0), and the layer that then grows by acid diffusing through it reaches "
        f"{1e6 * layer.value:.1f} micrometres in {_cycle(ledger)} ({1e6 * layer.low:.1f} to {1e6 * layer.high:.0f} "
        f"micrometres over the ranges of the inputs). One fill of fresh water can dissolve {1e3 * fill.value:.2f} mm "
        f"of gypsum, {saturating.value:.0f} times that layer ({saturating.low:.1f} times at the least), "
    )
    if status == "fail":
        return status, head + (
            f"and water standing still for as long as the acid did dissolves {still.value:.1f} times the layer by "
            f"diffusion alone ({still.low:.1f} times at the least), so every fill strips it and every cycle starts "
            f"on bare stone: {1e3 * ten.value / CYCLES:.2f} mm of wall per cycle and {1e3 * ten.value:.1f} mm in ten "
            f"({1e3 * ten.low:.1f} to {1e3 * ten.high:.1f} mm over the ranges of the inputs). The outcome rests on "
            "the layer being the diffusion-limited one of 03, not on the cycle time, which cancels for still water."
        )
    if status == "pass":
        # Judgement call: the criterion also asks for a wall loss the surviving surfaces allow, and the ledger
        # holds no measured bound on it, so a layer that outlasts every fill still cannot pass the claim here.
        return "conditional", (
            f"The gypsum layer grows to {1e6 * layer.value:.1f} micrometres in {_cycle(ledger)} and one fill of "
            f"fresh water dissolves {saturating.value:.2g} times that ({saturating.high:.2g} times at most), so the "
            "layer outlasts every fill; the criterion also asks for a wall loss the surviving surfaces allow, and "
            "the ledger holds no measured bound on it."
        )
    return status, head + (
        f"so a fill that comes to saturation strips it, but water standing still for as long as the acid did "
        f"dissolves only {still.value:.2g} times the layer by diffusion alone ({still.low:.2g} to {still.high:.2g} "
        "times over the ranges of the inputs), so whether the layer lasts depends on how the fresh water moves "
        "against the wall, which the hypothesis does not say."
    )


def _feed(ledger, r) -> str:
    """The numbers both feed claims rest on."""
    moles, mass, flux = r["chem.h2s_per_batch"], r["chem.h2s_mass_per_batch"], r["chem.h2s_flux"]
    yearly, air = r["chem.h2s_mass_per_year"], r["chem.cave_air_per_batch"]
    return (
        f"one full batch needs {moles.value:.0f} mol of hydrogen sulfide, {mass.value:.0f} kg, a mole for each mole "
        f"of sulfur dioxide in the King's Chamber, which is {flux.value:.2g} mol/s and {yearly.value / 1000:.0f} t a "
        f"year at one batch every {ledger.q('rx.cycle_time') / HOUR:.0f} h, and {flux.low:.2g} to {flux.high:.2g} "
        "mol/s over the cycle times taken; the "
        "hypothesis states no cycle rate, so the required flux is undefined (07 section 4.4). 07 gives no flux for "
        "any seep or spring to set against it: its one analogue is a concentration, read from an abstract, at "
        f"which one batch is the sulfide in {air.value / 1e6:.1f} million m3 of cave air"
    )


def _s01(ledger, r):
    # Both sides of the criterion's comparison are missing, whatever the numbers: the hypothesis states no cycle
    # rate (as for S31 in Tier 0) and 07 holds no analogue flux, so the status is fixed.
    return "undefined", (
        "O" + _feed(ledger, r)[1:] + f" ({1e6 * ledger.q('rx.h2s_cave_air'):.0f} ppmv in active sulfuric-acid caves)."
    )


def _e01(ledger, r):
    # The passing clause is documentary and unmet; the failing clause is the flux comparison of S01.
    return "undefined", (
        "No opened source gives a measured hydrogen sulfide flux, composition or source pressure under the "
        "plateau: 07 read the cited paper in full, and it measured no gas and reports no present-day seepage, so "
        "the passing clause is not met. The failing clause cannot be evaluated either: " + _feed(ledger, r) + "."
    )


RULES = {"S01": _s01, "E01": _e01, "S19": _s19, "S22": _s22, "S23": _s23}


def verdicts(ledger: Ledger, results: dict[str, Result]) -> dict[str, tuple[str, str]]:
    """{claim: (status, basis)} for the five claims; the rules also read Tier 0's results, which stand."""
    known = screening.all_results(ledger) | results
    return {claim: rule(ledger, known) for claim, rule in RULES.items()}
