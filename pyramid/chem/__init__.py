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
     aqueous.MIXTURE, lambda q: aqueous.forced_back(q, aqueous.stoichiometric_air(q))),
    ("chem.air_without_pushback", "Largest share of air in the gas for which nothing need be pushed back",
     "1", "x = H_N2 R T / (1 - x_O2)", aqueous.THRESHOLD, aqueous.air_without_pushback),
    ("chem.sulfur_oxidisable_without_pushback", "Share of the sulfur that the oxygen of that much air can oxidise",
     "1", "y = x_O2 x / (0.5 (1 - x))", aqueous.THRESHOLD,
     lambda q: aqueous.sulfur_oxidisable(q, aqueous.air_without_pushback(q))),
    ("chem.gypsum_layer_per_cycle", "Gypsum layer that grows in one cycle on a wall bare at its start",
     "m", "d = sqrt(Vm D C t); C = 2 n_SO2 / V_gallery", walls.LAYER, walls.layer_per_cycle),
    ("chem.fill_dissolves", "Gypsum layer one Gallery of fresh water dissolves in coming to saturation",
     "m", "d = s rho V_gallery Vm / A_wall", walls.FILL, walls.fill_dissolves),
    ("chem.still_fill_dissolves", "Gypsum layer a still fill of fresh water dissolves by diffusion alone in its dwell",
     "m", "d = 2 s rho sqrt(D_w f t / pi) Vm; f = fresh dwell over acid dwell", walls.STILL,
     walls.still_fill_dissolves),
    ("chem.saturating_margin", "What a saturating fill dissolves over the layer one cycle grows",
     "1", "chem.fill_dissolves / chem.gypsum_layer_per_cycle", tuple(dict.fromkeys(walls.LAYER + walls.FILL)),
     walls.saturating_margin),
    ("chem.still_margin", "What a still fill dissolves over the layer one cycle grows",
     "1", "chem.still_fill_dissolves / chem.gypsum_layer_per_cycle; the cycle time cancels, the fresh dwell f does not",
     tuple(dict.fromkeys(walls.LAYER + walls.STILL)), walls.still_margin),
    ("chem.fresh_dwell_to_strip",
     "Dwell of still fresh water, as a share of the acid's, at which it just dissolves the layer one cycle grows",
     "1", "f / chem.still_margin^2; f cancels", tuple(dict.fromkeys(walls.LAYER + walls.STILL)), walls.dwell_to_strip),
    ("chem.layer_left_under_acid",
     "Share of a cycle's layer that stands under still acid, which dissolves it outside while it grows beneath",
     "1", "2 / (r + sqrt(r^2 + 4)); r = 2 x sqrt(D_w t / pi) Vm / chem.gypsum_layer_per_cycle; x (c + x) = "
     "(s rho)^2; from dd/dt = Vm D C / (2 d) - x Vm sqrt(D_w / (pi t))", walls.ACID, walls.left_under_acid),
    ("chem.deposit_over_fill", "Most gypsum a whole batch can lay down over what one fresh fill dissolves",
     "1", "max(0, c / (s rho) - 1): (c - s rho) V_gallery over s rho V_gallery", walls.DEPOSIT,
     walls.deposit_over_fill),
    ("chem.wall_loss_per_cycle", "Limestone lost in a cycle that starts bare and comes to gypsum saturation",
     "m", "w = x c V_gallery Vc / A_wall + d Vc / Vm; x = min(1, (s rho / c)^2)", walls.LOSS, walls.loss_per_cycle),
    ("chem.wall_loss_ten_cycles", "Limestone lost in ten such cycles, every fill stripping the layer",
     "m", "10 x chem.wall_loss_per_cycle", walls.LOSS, lambda q: CYCLES * walls.loss_per_cycle(q)),
    ("chem.h2s_per_batch", "Hydrogen sulfide one full batch needs",
     "mol", "n = p V / (R T), a mole for each mole of sulfur dioxide", screening._SO2, feed.batch_moles),
    ("chem.h2s_mass_per_batch", "Mass of the hydrogen sulfide one full batch needs",
     "kg", "m = n M", feed.MASS, feed.batch_mass),
    ("chem.h2s_flux", "Hydrogen sulfide flux for one full batch per cycle",
     "mol/s", "F = n / t", feed.FLUX, feed.flux),
    ("chem.h2s_mass_per_year", "Hydrogen sulfide for a year of full batches",
     "kg", "m = n M x one year / t", feed.FEED, feed.yearly_mass),
    ("chem.cave_air_per_batch", "Cave air at the analogue's ceiling that holds the sulfur of one batch",
     "m3", "V = V_chamber / x_H2S", feed.CAVE_AIR, feed.cave_air_per_batch),
]


# The results the viewer should show under each claim: a claim shows a result once it depends on all its inputs.
SHOWN = {
    "S01": ("chem.h2s_per_batch", "chem.h2s_mass_per_batch", "chem.h2s_flux", "chem.h2s_mass_per_year",
            "chem.cave_air_per_batch"),
    "S19": ("chem.capture_share", "chem.capture_equilibrium"),
    "S22": ("chem.least_air", "chem.forced_back_least_air", "chem.forced_back_stoichiometric",
            "chem.air_without_pushback", "chem.sulfur_oxidisable_without_pushback", "chem.uptake_pace"),
    "S23": ("chem.gypsum_layer_per_cycle", "chem.fill_dissolves", "chem.still_fill_dissolves",
            "chem.saturating_margin", "chem.still_margin", "chem.fresh_dwell_to_strip", "chem.layer_left_under_acid",
            "chem.deposit_over_fill", "chem.wall_loss_per_cycle", "chem.wall_loss_ten_cycles"),
}
SHOWN["E01"] = SHOWN["S01"]


def depends_on(ledger: Ledger) -> dict[str, list[str]]:
    """The ledger ids each claim's depends_on must gain for the viewer to show these results under it."""
    inputs = {row[0]: row[4] for row in QUANTITIES}
    return {claim: [i for i in dict.fromkeys(i for id in ids for i in inputs[id])
                    if i not in ledger.claims[claim].depends_on]
            for claim, ids in SHOWN.items()}


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


def _percent(share: float) -> str:
    """A share as a percentage, with a decimal below one percent so that a small share does not print as none."""
    return f"{100 * share:.0f}" if share >= 0.01 else f"{100 * share:.1f}"


def _s19(ledger, r):
    share, held = r["chem.capture_share"], r["chem.capture_equilibrium"]
    # The criterion's lines (03 section 4.4): pass from 90 percent, fail below 50 percent.
    status = three_way(share.low >= 0.90, share.high >= 0.50)
    (still, stirred), (slow, fast) = ledger.rng("rx.kg_gas"), ledger.rng("chem.kl_surface")
    head = (
        f"With the Gallery half full and {_cycle(ledger)}, {_percent(share.value)} percent of the sulfur dioxide "
        f"crosses the level surface into the water "
    )
    tail = (
        f" The water could hold {100 * held.value:.0f} percent at equilibrium, so the rate decides. It depends on "
        "the cycle time, on whether the gas over the water stands still or convects (gas-side coefficient "
        f"{1e3 * still:.3g} to {1e3 * stirred:.3g} mm/s, assumed) and on the film on the water's side of the surface "
        f"(liquid-film coefficient {1e3 * slow:.3g} to {1e3 * fast:.3g} mm/s, assumed with no source), none of which "
        f"the hypothesis gives; the {_percent(share.value)} percent is for a gas-side coefficient of "
        f"{1e3 * ledger.q('rx.kg_gas'):.3g} mm/s and a liquid-film coefficient of "
        f"{1e3 * ledger.q('chem.kl_surface'):.3g} mm/s."
    )
    if status == "pass":
        return status, head + (
            f"({_percent(share.low)} percent at the least), at least the 90 percent from which the criterion passes "
            "the claim."
        ) + tail
    spread = f"({_percent(share.low)} to {_percent(share.high)} percent over the ranges of the inputs), "
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
    call = (" Taking the least air of a full stroke, not a gas without air, as the end most favourable to the "
            "hypothesis is a judgement call.")
    if status != "fail":
        return status, head + (
            f"Its nitrogen and unused oxygen can dissolve in the rising water, and the sulfur dioxide is taken up at "
            f"{pace.value:.1f} times the rate at which the water displaces it ({pace.low:.2g} to {pace.high:.2g} "
            "times over the ranges of the inputs), "
        ) + ("so nothing is forced back at any end of the ranges."
             if status == "pass" else
             "so whether gas is forced back depends on the cycle time and the stirring, which the hypothesis does "
             "not give.") + call
    return status, head + (
        "Its nitrogen hardly dissolves: if all the sulfur dioxide dissolved, the oxidation used every mole of "
        "oxygen it could and the water arrived free of dissolved gas, the rising water would still push "
        f"{100 * least.value:.0f} percent of the gas back ({100 * least.low:.0f} to {100 * least.high:.0f} percent "
        f"over the ranges of the inputs), and {100 * mixture.value:.0f} percent of a mixture that carries the oxygen "
        f"for all its sulfur. Nothing is pushed back only if air is under {100 * limit.value:.1f} percent of the gas "
        f"({100 * limit.high:.1f} percent at most), which brings oxygen for {100 * oxidisable.value:.1f} percent of "
        "the sulfur, while S14 to S17 carry air into the Gallery; the hypothesis states no gas fraction and no "
        "stroke."
    ) + call


def _s23(ledger, r):
    layer, fill = r["chem.gypsum_layer_per_cycle"], r["chem.fill_dissolves"]
    saturating, still = r["chem.saturating_margin"], r["chem.still_margin"]
    needed, left = r["chem.fresh_dwell_to_strip"], r["chem.layer_left_under_acid"]
    ten, share, deposit = r["chem.wall_loss_ten_cycles"], r["t0.gypsum_saturation_loss"], r["chem.deposit_over_fill"]
    # The criterion as written: fail if the layer is stripped each cycle. Only the fresh water can strip it: the
    # acid of the next batch thins it and it grows back from beneath (chem.layer_left_under_acid is above zero).
    # The unfavourable end is a fill that comes to saturation (03 check V17). The favourable end is a fill that
    # stands still, dissolves by diffusion alone and stays for the shortest dwell of the range the ledger takes,
    # because the hypothesis states none.
    status = three_way(saturating.high < 1, still.low < 1)
    shortest, longest = ledger.rng("rx.fresh_dwell")
    head = (
        f"Fresh water lets bare limestone neutralise {100 * share.value:.0f} percent of the strongest batch before "
        f"gypsum can form (Tier 0), and the layer that then grows by acid diffusing through it reaches "
        f"{1e6 * layer.value:.1f} micrometres in {_cycle(ledger)} ({1e6 * layer.low:.1f} to {1e6 * layer.high:.0f} "
        f"micrometres over the ranges of the inputs). One fill of fresh water can dissolve {1e3 * fill.value:.2f} mm "
        f"of gypsum, {saturating.value:.0f} times that layer ({saturating.low:.1f} times at the least); even the "
        f"most gypsum a whole batch can lay down is {100 * deposit.value:.0f} percent of what one fill dissolves "
        f"({100 * deposit.high:.0f} percent at most), "
    )
    stripped = (
        f"every cycle then starts on bare stone, which loses up to {1e3 * ten.value / CYCLES:.2f} mm per cycle and "
        f"{1e3 * ten.value:.1f} mm in ten in bringing each batch to saturation ({1e3 * ten.low:.1f} to "
        f"{1e3 * ten.high:.1f} mm over the ranges of the inputs)"
    )
    if status == "fail":
        return status, head + (
            f"and a fill that stands still dissolves {still.value:.1f} times the layer by diffusion alone "
            f"({still.low:.2f} times at the least, over fresh-water dwells from {shortest:g} to {longest:g} of the "
            f"acid's, which the hypothesis does not state), so every fill strips it; {stripped}. The outcome rests "
            "on the layer being the diffusion-limited one of 03: still water would not strip a thicker deposit."
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
        f"so a fill that comes to saturation strips it; {stripped}. A fill that stands still strips it by diffusion "
        f"alone only if it stands at least {needed.value:.2g} times as long as the acid stood ({needed.high:.2g} "
        f"times at most). The hypothesis does not state that time; over the range taken, {shortest:g} to {longest:g} "
        f"of the acid's, a still fill dissolves {still.low:.2g} to {still.high:.2g} times the layer. The acid of the "
        "next batch does not strip it: still acid dissolves it from outside while it grows from beneath and leaves "
        f"{100 * left.value:.0f} percent of it ({100 * left.low:.0f} to {100 * left.high:.0f} percent). So whether "
        "the layer lasts depends on how long the fresh water stands against the wall and on how it moves, neither "
        "of which the hypothesis states."
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
