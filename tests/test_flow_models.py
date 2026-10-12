"""The flow models against closed forms: each expected number is computed here from the formula it tests."""
import itertools
import math

import numpy as np
import pytest
from scipy.integrate import solve_ivp

from pyramid import flow, ledger, screening
from pyramid.flow import gas, hydraulics, retention
from pyramid.screening import G


@pytest.fixture(scope="module")
def led() -> ledger.Ledger:
    return ledger.load()


@pytest.fixture(scope="module")
def q(led) -> dict[str, float]:
    """Every ledger quantity at its value."""
    return {id: quantity.value for id, quantity in led.quantities.items()}


# --- water ----------------------------------------------------------------------------------


def test_a_tank_empties_through_an_orifice_in_torricellis_time():
    area, cda, depth = 2.0, 0.01, 3.0
    expected = area / cda * math.sqrt(2 * depth / G)  # h(t) = h0 (1 - t / T)^2
    # stop a hair above the orifice: the level meets it with zero slope, 1e-8 of the depth is 1e-4 of the time
    times, levels = hydraulics.simulate([area], [depth], [(0, None, 0.0, cda)], 2 * expected, until=(0, 1e-8 * depth))
    assert times[-1] == pytest.approx(expected, rel=0.01)
    assert times[-1] == pytest.approx(expected, rel=2e-4)  # and far inside the 1 percent asked for
    halfway = np.interp(expected / 2, times, levels[:, 0])
    assert halfway == pytest.approx(depth / 4, rel=1e-6)  # a quarter of the depth is left at half the time


def test_two_vessels_settle_at_a_common_level_and_keep_their_water():
    areas, start, cda = np.array([3.0, 5.0]), np.array([4.0, 1.0]), 0.02
    common = float(areas @ start / areas.sum())  # 2.125 m
    settle = 2 * math.sqrt(start[0] - start[1]) / (cda * math.sqrt(2 * G) * (1 / areas[0] + 1 / areas[1]))
    times, levels = hydraulics.simulate(areas, start, [(0, 1, 0.5, cda)], 2 * settle)
    water = levels @ areas
    assert np.max(np.abs(water / water[0] - 1)) < 1e-9
    assert levels[-1] == pytest.approx([common, common], abs=1e-6)
    # at half the settling time the difference has fallen to a quarter: sqrt(difference) falls linearly
    difference = np.interp(settle / 2, times, levels[:, 0] - levels[:, 1])
    assert difference == pytest.approx((start[0] - start[1]) / 4, rel=1e-4)


def test_an_orifice_above_the_lower_vessel_discharges_freely():
    # the sill at 2 m is above the lower level, so only the upper vessel's head over the sill drives the flow
    times, levels = hydraulics.simulate([1.0, 100.0], [3.0, 0.0], [(0, 1, 2.0, 0.01)], 10.0)
    expected = 2.0 + (1.0 - 0.01 * math.sqrt(2 * G) * 10.0 / 2) ** 2
    assert levels[-1, 0] == pytest.approx(expected, rel=1e-8)


def test_the_flood_time_is_the_simulated_rise_to_the_shaft_mouths(q):
    area = hydraulics.loose_area(q)
    floor, mouths = q["kc.floor.z"], q["kc.floor.z"] + q["kcs.mouth_height"]
    link = (0, 1, floor, q["flow.discharge_coefficient"] * area)
    times, _ = hydraulics.simulate([math.inf, hydraulics.flood_area(q)], [q["gg.roof_top.z"], floor], [link], 1e5,
                                   until=(1, mouths))
    assert hydraulics.flood_time(q, area) == pytest.approx(times[-1], rel=1e-6)
    assert hydraulics.kc_flood_time(q) == pytest.approx(369.6, rel=0.01)  # about six minutes


def test_the_gas_lock_depth_obeys_boyles_law(q):
    depth = hydraulics.kc_gaslock_depth(q)
    compressed = q["site.atm_pressure"] * q["kc.height"] / (q["kc.height"] - depth)
    water = q["site.atm_pressure"] + q["hydro.water_density"] * G * (q["gg.roof_top.z"] - q["kc.floor.z"] - depth)
    assert compressed == pytest.approx(water, rel=1e-12)
    assert 0 < depth < q["kc.height"]


def test_the_fill_volume_is_the_sum_02_lists(led, q):
    # 02 working W3 and 09: about 860 to 875 m3 for the Gallery, Queen's Chamber, both passages and the well shaft
    assert hydraulics.fill_volume(q) == pytest.approx(573.0 + 164.1 + 5.1 + 50.5 + 44.3 + 28.8)
    assert hydraulics.fill_volume(q) == pytest.approx(868, rel=0.01)
    # 02 section 2.2: Old Kingdom and modern water 43 to 53 m below the base, the passage foot 30 m below it
    assert hydraulics.documented_water_below_chamber(q) == pytest.approx(60 - 29.9974 - 15)


# --- gas ------------------------------------------------------------------------------------


def test_parallel_orifices_share_the_gas_by_area_and_loss():
    density, total = 1.2, 0.3
    area_a, loss_a, area_b, loss_b = 0.05, 19.0, 0.02, 1.0 / 0.6**2  # a duct with K = 19, a sharp orifice Cd = 0.6
    paths = [gas.orifice(area_a / math.sqrt(loss_a), density), gas.orifice(area_b / math.sqrt(loss_b), density)]
    dp, (flow_a, flow_b) = gas.solve(paths, total, 1e5)
    assert flow_a / flow_b == pytest.approx(area_a / area_b * math.sqrt(loss_b / loss_a), rel=0.01)
    assert flow_a / flow_b == pytest.approx(area_a / area_b * math.sqrt(loss_b / loss_a), rel=1e-12)
    conductance = area_a / math.sqrt(loss_a) + area_b / math.sqrt(loss_b)
    assert dp == pytest.approx(density / 2 * (total / conductance) ** 2, rel=1e-9)


def test_losses_in_series_add():
    # two equal orifices in series pass 1 / sqrt(2) of what one passes at the same pressure difference
    assert gas.in_series(0.03, 0.03) == pytest.approx(0.03 / math.sqrt(2))
    assert gas.in_series(0.0, 0.03) == 0.0


def test_the_gas_drawn_is_the_water_drained(q):
    volume, drain = q["gg.volume"], q["hydro.drain_time"]
    viscosity = q["hydro.air_density"] * q["hydro.air_kinematic_viscosity"]
    paths = [gas.orifice(gas.antechamber_conductance(q, gas.opening_area(q)), q["hydro.air_density"]),
             gas.slot(q["hydro.joint_length"], q["hydro.joint_aperture"], q["flow.joint_path_length"], viscosity)]
    _, flows = gas.solve(paths, volume / drain, 1e5)
    assert sum(flows) * drain == pytest.approx(volume, rel=1e-9)
    _, antechamber, joints, stored = gas.draw(q)
    assert antechamber + joints + stored == pytest.approx(1.0, rel=1e-9)


def test_two_paths_agree_with_the_quadratic_they_obey():
    # k sqrt(dp) + c dp = Q is a quadratic in sqrt(dp)
    k, c, total = 0.011 * math.sqrt(2 / 1.2), 8e-4, 0.16
    root = ((-k + math.sqrt(k * k + 4 * c * total)) / (2 * c)) ** 2
    dp, flows = gas.solve([gas.orifice(0.011, 1.2), lambda dp: c * dp], total, 1e5)
    assert dp == pytest.approx(root, rel=1e-10)
    assert flows[1] == pytest.approx(c * root, rel=1e-10)


def test_the_suction_stops_at_the_cap():
    dp, flows = gas.solve([gas.orifice(1e-6, 1.2)], 1.0, 5e4)
    assert dp == 5e4 and flows[0] == pytest.approx(1e-6 * math.sqrt(2 * 5e4 / 1.2))


def test_an_open_antechamber_with_tight_masonry_gives_tier0s_shaft_pressure(led, q):
    # with nothing but the two shafts in the way the network must return Tier 0's number (09 row 23: 25 Pa)
    tier0 = screening.all_results(led)["t0.shaft_draw_pressure"].value
    assert gas.draw(q, area=1e9, joints=False)[0] == pytest.approx(tier0, rel=1e-9)
    assert tier0 == pytest.approx(25, rel=0.05)


def test_the_flip_apertures_are_where_the_share_crosses(led, q):
    # the roots leave out the gas Davison's chamber gives up, a few parts in a hundred thousand here
    half = q | {"hydro.joint_aperture": gas.joint_aperture_half(q)}  # with the slabs down
    assert gas.draw(half)[1] == pytest.approx(0.5, rel=1e-4)
    nine_tenths = q | {"hydro.joint_aperture": gas.joint_aperture_nine_tenths(q)}  # with no slab in the passage
    assert gas.draw(nine_tenths, area=gas.passage_area(q))[1] == pytest.approx(0.9, rel=1e-4)
    # with the opening never under water they are the closed forms of the steady draw: the path carries the share
    # s of Q at dp = (rho / 2) (s Q / C)^2 and the joints the rest, c dp = (1 - s) Q
    total, density = q["gg.volume"] / q["hydro.drain_time"], q["hydro.air_density"]
    pocket = tuple(q[id] for id in gas._POCKET)
    for share, area in ((0.5, gas.opening_area(q)), (0.9, gas.passage_area(q))):
        conductance = gas.antechamber_conductance(q, area)
        slope = (1 - share) * total / (density / 2 * (share * total / conductance) ** 2)
        steady = gas.summed(total, conductance, density, slope, gas.suction_cap(q), q["hydro.water_density"], pocket,
                            submerged=False)
        assert steady[2] == pytest.approx(share, rel=1e-12)
        # under water the joints have the pocket to themselves at first, so they must be tighter for the same share
        aperture = (12 * density * q["hydro.air_kinematic_viscosity"] * q["flow.joint_path_length"] * slope
                    / q["hydro.joint_length"]) ** (1 / 3)
        assert gas.flip_aperture(q, share, area) < aperture
    # and the drain time at which half comes down the shafts, at the ledger's joints
    time, word = gas.flip_drain_time(q, *led.rng("hydro.drain_time"))
    assert gas.draw(q | {"hydro.drain_time": time})[1] == pytest.approx(0.5, rel=1e-6)
    assert word == "slower" and gas.draw(q | {"hydro.drain_time": 2 * time})[1] > 0.5
    # joints of 0.05 mm leave more than half at every drain rate: there is no such time
    assert gas.flip_drain_time(q | {"hydro.joint_aperture": 5e-5}, *led.rng("hydro.drain_time")) is None


# --- gas: the antechamber opening under water -------------------------------------------------


def test_the_gallery_section_is_tier0s_and_the_pocket_is_its_integral(q):
    bands = gas.section_bands(q)
    assert sum(width * (high - low) for low, high, width in bands) == pytest.approx(screening._gg_section(q))
    slope = math.radians(q["gg.angle"])
    length = q["gg.floor_length"] * math.cos(slope)
    roof = q["gg.south_end.z"] + q["gg.height"]

    def by_slices(level, slices=20000):
        """The Gallery above a level, cut into slices along its length: the floor falls away to the north."""
        volume = 0.0
        for i in range(slices):
            depth = level - (q["gg.south_end.z"] - math.tan(slope) * (i + 0.5) * length / slices)  # over the floor
            volume += sum(width * max(0.0, high - max(low, depth)) for low, high, width in bands) * length / slices
        return volume / (screening._gg_section(q) * length)

    top = q["ante.floor.z"] + q["ante.low_passage.height"]
    for level in (top, q["ante.floor.z"], q["gg.south_end.z"] - 0.5, roof - 1.0):
        assert gas.pocket_share(q, level) == pytest.approx(by_slices(level), rel=1e-4)
    assert gas.pocket_share(q, roof) == 0.0
    # a plain box of the same height: the pocket is a wedge, (H - h0)^2 / (2 tan(a)) across the width
    box = q | {"gg.overhang": 0.0, "gg.slot_width": q["gg.width"]}
    height = q["gg.height"]
    assert gas.pocket_share(box, roof - 2.0) == pytest.approx(2.0**2 / (2 * math.tan(slope)) / (height * length))
    # 44.10 m is the opening's top and 42.99 m its floor; the full Gallery stands 7.4 m over the top
    assert gas.opening_depth(q) == pytest.approx(51.5 - 44.10, abs=0.01)
    assert gas.submerged_share(q) == pytest.approx(0.132, abs=0.001)
    assert gas.pocket_share(q, q["ante.floor.z"]) == pytest.approx(0.181, abs=0.001)


def test_the_closed_form_of_one_orifice_and_one_leak_is_the_general_solvers_answer():
    density, total, cap = 1.2, 0.16, 9.9e4
    heads = [0.0, 150.0, 5e3, 3e4, 7.2e4]
    for conductance, slope in ((0.011, 8e-4), (0.024, 1e-6), (0.011, 0.0), (0.0, 8e-4), (1e-7, 1e-9), (0.0, 0.0)):
        dp, through, leak = gas.split(total, conductance, density, slope, heads, cap)
        for i, head in enumerate(heads):
            paths = [gas.orifice(conductance, density, head), lambda dp: slope * dp]
            expected, flows = gas.solve(paths, total, cap)
            assert dp[i] == pytest.approx(expected, rel=1e-9), (conductance, slope, head)
            assert [through[i], leak[i]] == pytest.approx(flows, rel=1e-9, abs=1e-15)
    # an orifice under water and nothing else: the suction is the water over it plus the orifice's own loss
    dp, through, _ = gas.split(total, 0.011, density, 0.0, [3e4], cap)
    assert dp[0] == pytest.approx(3e4 + density / 2 * (total / 0.011) ** 2, rel=1e-12)
    assert through[0] == pytest.approx(total, rel=1e-12)
    # a leak that carries everything below the head leaves the orifice dry
    dp, through, leak = gas.split(total, 0.011, density, 8e-4, [3e4], cap)
    assert dp[0] == pytest.approx(total / 8e-4) and through[0] == 0.0 and leak[0] == pytest.approx(total)


def _share_level_by_level(q, area, levels=400):
    """The antechamber path's share of a draw, each water level solved by bisection: the model's own laws."""
    total, density = q["gg.volume"] / q["hydro.drain_time"], q["hydro.air_density"]
    conductance, slope = gas.antechamber_conductance(q, area), gas.joint_slope(q)
    top = q["ante.floor.z"] + q["ante.low_passage.height"]
    roof = q["gg.south_end.z"] + q["gg.height"]
    passed = 0.0
    for i in range(levels):
        upper, lower = roof - (roof - top) * i / levels, roof - (roof - top) * (i + 1) / levels
        head = q["hydro.water_density"] * G * ((upper + lower) / 2 - top)
        _, (through, leak) = gas.solve([gas.orifice(conductance, density, head), lambda dp: slope * dp], total,
                                       gas.suction_cap(q))
        passed += (gas.pocket_share(q, lower) - gas.pocket_share(q, upper)) * through / (through + leak)
    _, (through, leak) = gas.solve([gas.orifice(conductance, density), lambda dp: slope * dp], total,
                                   gas.suction_cap(q))
    return passed + (1 - gas.pocket_share(q, top)) * through / (through + leak)


def test_the_draw_is_summed_over_the_water_level(q):
    passage = gas.passage_area(q)
    for aperture, drain, area in ((5.08e-4, 3600.0, None), (1e-4, 3600.0, passage), (5e-5, 21600.0, passage),
                                  (2e-4, 600.0, None)):
        case = q | {"hydro.joint_aperture": aperture, "hydro.drain_time": drain}
        open_area = gas.opening_area(q) if area is None else area
        _, share, joints, stored = gas.draw(case, area=area)
        assert share / (1 - stored) == pytest.approx(_share_level_by_level(case, open_area), rel=1e-3)
        assert share + joints + stored == pytest.approx(1.0, rel=1e-9)
        # eight times as many levels move it by less than one part in ten thousand
        args = (case["gg.volume"] / drain, gas.antechamber_conductance(case, open_area), case["hydro.air_density"],
                gas.joint_slope(case), gas.suction_cap(case), case["hydro.water_density"],
                tuple(case[id] for id in gas._POCKET))
        assert gas.summed(*args)[2] == pytest.approx(gas.summed(*args, steps=8 * gas.STEPS)[2], abs=1e-4)


def test_leaking_joints_have_the_pocket_to_themselves_while_the_opening_is_under_water(q):
    # at the ledger's joints the pocket is fed at 195 Pa, against 72 kPa of water over the opening: nothing
    # passes it until the surface is within 2 cm of its top, so the share is the steady one less the part
    # of the Gallery displaced by then
    head = q["hydro.water_density"] * G * gas.opening_depth(q)
    assert head == pytest.approx(72.4e3, rel=0.01)
    assert gas.start_pressure(q) == pytest.approx(q["gg.volume"] / q["hydro.drain_time"] / gas.joint_slope(q))
    assert gas.start_pressure(q) < head / 100
    for area in (None, gas.passage_area(q)):
        steady, summed = gas.draw(q, area=area, submerged=False), gas.draw(q, area=area)
        assert summed[1] == pytest.approx((1 - gas.submerged_share(q)) * steady[1], rel=2e-3)
        assert summed[0] == steady[0]  # once the opening is clear the pressure is the steady one
    # with gas-tight masonry the gas has no other way in: the suction rises to the water over the opening
    # plus the path's own loss, and all of it still comes through
    tight = gas.draw(q, area=gas.passage_area(q), joints=False)
    assert gas.start_pressure(q, area=gas.passage_area(q), joints=False) == pytest.approx(head + tight[0], rel=1e-12)
    assert tight[1] + tight[3] == pytest.approx(1.0, rel=1e-12)
    # and nothing at all through a shut path, where the water hangs at the most it can pull
    shut = gas.draw(q, area=0.0, joints=False)
    assert shut[0] == gas.suction_cap(q) and shut[1] == 0.0


def test_the_ranges_hold_a_sweep_of_the_drain_time_and_of_the_gallerys_section(led, q):
    results = flow.all_results(led)
    # the shares turn round in the drain time at some apertures, where corners need not be the extremes
    deciding = ("hydro.joint_aperture", "flow.joint_path_length", "flow.discharge_coefficient",
                "ante.groove_connected_area", "flow.slab_leak_area")
    times = np.geomspace(*led.rng("hydro.drain_time"), 25)
    turned = False
    for name, area in (("shaft_share", None), ("slabs_absent_share", gas.passage_area(q))):
        result = results[f"flow.{name}"]
        for corner in itertools.product(*(led.rng(id) for id in deciding)):
            case = q | dict(zip(deciding, corner))
            curve = [gas.draw(case | {"hydro.drain_time": float(time)}, area=area)[1] for time in times]
            assert result.low - 0.002 <= min(curve) and max(curve) <= result.high + 0.002
            turned = turned or max(curve) > max(curve[0], curve[-1]) + 1e-6
    assert turned
    # the Gallery's section and levels are held at their ledger values in those ranges: over their own ranges
    # the share moves by less than a hundredth, as the share displaced under water does
    under = results["flow.submerged_share"]
    assert under.high - under.low < 0.01 and under.inputs == gas._POCKET
    held = [id for id in gas._PHASE if led.rng(id)[0] < led.rng(id)[1]]
    for area in (None, gas.passage_area(q)):
        shares = [gas.draw(q | dict(zip(held, corner)), area=area)[1]
                  for corner in itertools.product(*(led.rng(id) for id in held))]
        assert max(shares) - min(shares) < 0.01
    for name in ("shaft_share", "slabs_absent_share", "draw_pressure", "start_pressure", "joint_aperture_half"):
        assert set(gas._PHASE) <= set(results[f"flow.{name}"].inputs)


def test_three_clearances_one_after_another_pass_less_than_one(q):
    slabs = q | {"ante.groove_connected_area": 0.0}
    assert gas.series_area(slabs) == pytest.approx(q["flow.slab_leak_area"] / math.sqrt(3))
    assert gas.series_area(slabs) < gas.series_area(q) < gas.opening_area(q)
    assert gas.series_area(q | {"flow.slab_leak_area": 0.0}) == 0.0  # the grooves pass only the last slab


def test_three_gallery_openings_lie_at_its_foot(q):
    openings = {o.name: o for o in flow.network.gallery_openings(q)}
    foot = {name for name, o in openings.items() if flow.network.at_the_foot(q, o)}
    assert foot == {"Ascending Passage", "Queen's passage", "well shaft mouth"}
    # 01 claim 4: 1.27 m2, about 0.5 m2, about 1.17 m2, about 0.67 x 0.75 m
    assert openings["Ascending Passage"].area == pytest.approx(1.27, rel=0.01)
    assert openings["well shaft mouth"].area == pytest.approx(0.5, rel=0.02)
    assert openings["antechamber passage"].area == pytest.approx(1.17, rel=0.01)
    assert openings["Davison's passage"].area == pytest.approx(0.67 * 0.75, rel=0.01)
    assert gas.foot_wedge_share(q) < 0.01


# --- retention ------------------------------------------------------------------------------


def test_diffusion_through_a_thin_tube_has_the_closed_form_time_constant():
    volume, length, area, diffusivity = 300.0, 60.0, 0.005, 1.2e-5  # the tube holds a thousandth of the volume
    expected = volume * length / (diffusivity * area)
    assert retention.tube_time_constant(volume, [(length, area)], diffusivity) == pytest.approx(expected, rel=0.01)
    # the tube's own content delays the loss by A L / (3 V) to first order, which the model resolves
    measured = retention.tube_time_constant(volume, [(length, area)], diffusivity, cells=200)
    assert measured / expected - 1 == pytest.approx(area * length / (3 * volume), rel=0.02)


def test_the_kings_chamber_shafts_lose_gas_as_two_tubes_in_parallel(q):
    tubes = [(q[f"kcs.{side}.length"], q[f"kcs.{side}.width"] * q[f"kcs.{side}.height"]) for side in ("north", "south")]
    closed = q["kc.volume"] / (q["flow.so2_diffusivity"] * sum(area / length for length, area in tubes))
    assert retention.diffusion_time_constant(q) == pytest.approx(closed)
    assert retention.tube_time_constant(q["kc.volume"], tubes, q["flow.so2_diffusivity"]) == pytest.approx(closed, rel=0.01)
    assert retention.diffusion_half_time(q) / screening.YEAR == pytest.approx(361, rel=0.01)


def test_sulfur_dioxide_is_2p2_times_as_dense_as_air(q):
    assert retention.so2_density_ratio(q) == pytest.approx(2.2, rel=0.01)  # 03: 2.2 by molar masses
    rise = q["kcs.exit.z"] - q["kc.floor.z"] - q["kcs.mouth_height"]
    assert retention.dense_gas_head(q) == pytest.approx((2.2118 - 1) * q["hydro.air_density"] * G * rise, rel=1e-3)


def _half_time_by_integration(q, wind):
    """The half-time from the model's own equation, integrated step by step."""
    air, volume = q["hydro.air_density"], q["kc.volume"]
    drive = q["flow.wind_pressure_coefficient_difference"] * air * wind**2 / 2
    head, slow = retention.dense_gas_head(q), retention.diffusion_time_constant(q)
    north, south = (q[f"kcs.{s}.width"] * q[f"kcs.{s}.height"] for s in ("north", "south"))
    friction = air / 2 * (q["hydro.kcs_north_loss_coefficient"] / north**2
                          + q["hydro.kcs_south_loss_coefficient"] / south**2)

    def rate(_, y):
        return -y * (math.sqrt(max(0.0, drive - head * y[0]) / friction) / volume + 1 / slow)

    def half(_, y):
        return y[0] - 0.5

    half.terminal = True
    return solve_ivp(rate, (0, 1e12), [1.0], events=half, rtol=1e-10, atol=1e-12).t_events[0][0]


def test_the_half_time_follows_the_models_equation(q):
    threshold = retention.flush_wind_speed(q)
    assert threshold == pytest.approx(math.sqrt(2 * retention.dense_gas_head(q) / q["hydro.air_density"]))
    for wind in (1.05 * threshold, 1.5 * threshold, 3 * threshold):  # flowing from the start
        assert retention.half_time(q, wind) == pytest.approx(_half_time_by_integration(q, wind), rel=1e-4)
    # below the wind that lifts even a half-thinned charge nothing flows, and diffusion alone is left
    assert retention.half_time(q, 0.7 * threshold) == pytest.approx(retention.diffusion_half_time(q))
    assert retention.half_time(q, 0.0) == pytest.approx(retention.diffusion_half_time(q))
    # a wind far above the threshold flushes a well-mixed chamber as if the gas weighed nothing: ln(2) V / Q
    north, south = (q[f"kcs.{s}.width"] * q[f"kcs.{s}.height"] for s in ("north", "south"))
    series = 1 / math.sqrt(q["hydro.kcs_north_loss_coefficient"] / north**2
                           + q["hydro.kcs_south_loss_coefficient"] / south**2)
    wind = 100 * threshold
    weightless = math.log(2) * q["kc.volume"] / (series * wind * math.sqrt(q["flow.wind_pressure_coefficient_difference"]))
    assert retention.half_time(q, wind) == pytest.approx(weightless, rel=1e-3)
    assert retention.half_time(q, wind, fraction=0.0) == pytest.approx(weightless, rel=1e-6)


def test_a_dense_charge_runs_out_of_a_floor_opening_under_the_head_up_to_the_shaft_mouths(q):
    area = gas.opening_area(q)  # 202 cm2, at the chamber's floor
    floor, depth, cda = q["kc.length"] * q["kc.width"], q["kc.height"], q["flow.discharge_coefficient"] * area
    # The chamber is closed above the shaft mouths, where the air comes in: they hold the pressure at their level,
    # as the air tube of Mariotte's bottle does, so the head is steady and is that of the gas below them.
    dense = q["site.atm_pressure"] * q["chem.molar_mass_so2"] / (screening.R * q["chem.temperature"])  # p M / (R T)
    head = (dense - q["hydro.air_density"]) * G * q["kcs.mouth_height"]
    assert head == pytest.approx(13.08, rel=1e-3)  # (2.663 - 1.204) x 9.807 x 0.9144 Pa
    expected = floor * depth / 2 / (cda * math.sqrt(2 * head / dense))  # 160.2 / (0.01229 x 3.135) = 4158 s
    assert expected == pytest.approx(4158, rel=1e-3)
    assert retention.drain_half_time(q, area) == pytest.approx(expected, rel=1e-12)
    assert retention.drain_half_time(q, area) / 60 == pytest.approx(69, rel=0.01)  # not the 32 of a falling head
    # the orifice simulation's own run: water under a head held at h_mouth (1 - rho_air / rho_so2) over a sill
    # discharges at the same rate, and has delivered half the chamber's volume when the lower vessel is half full
    held = 100.0 + q["kcs.mouth_height"] * (1 - 1 / retention.so2_density_ratio(q))
    times, _ = hydraulics.simulate([math.inf, floor], [held, 0.0], [(0, 1, 100.0, cda)], 1e5, until=(1, depth / 2))
    assert retention.drain_half_time(q, area) == pytest.approx(times[-1], rel=1e-6)
    # the gas above the mouths adds to what must leave, not to the head: twice the height takes twice as long
    assert retention.drain_half_time(q | {"kc.height": 2 * depth}, area) == pytest.approx(2 * expected)
    assert retention.drain_half_time(q | {"kcs.mouth_height": 4 * q["kcs.mouth_height"]}, area) == pytest.approx(expected / 2)
    assert retention.drain_half_time(q, 0.0) == math.inf  # a shut path lets nothing out


def test_a_thinner_charge_is_flushed_by_a_weaker_wind(q):
    assert retention.flush_wind_speed(q, 0.1) == pytest.approx(retention.flush_wind_speed(q) * math.sqrt(0.1))
    wind = 12.0  # between the two thresholds
    assert retention.half_time(q, wind, fraction=1.0) == pytest.approx(retention.diffusion_half_time(q))
    assert retention.half_time(q, wind, fraction=0.1) < 6 * 3600
