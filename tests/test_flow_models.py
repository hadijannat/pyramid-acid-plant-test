"""The flow models against closed forms: each expected number is computed here from the formula it tests."""
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


def test_the_flip_apertures_are_where_the_share_crosses(q):
    for share, aperture in ((0.5, gas.joint_aperture_half(q)), (0.9, gas.joint_aperture_nine_tenths(q))):
        # the closed form leaves out the gas Davison's chamber gives up, a few parts in a million here
        assert gas.draw(q | {"hydro.joint_aperture": aperture})[1] == pytest.approx(share, rel=1e-4)


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


def test_a_thinner_charge_is_flushed_by_a_weaker_wind(q):
    assert retention.flush_wind_speed(q, 0.1) == pytest.approx(retention.flush_wind_speed(q) * math.sqrt(0.1))
    wind = 12.0  # between the two thresholds
    assert retention.half_time(q, wind, fraction=1.0) == pytest.approx(retention.diffusion_half_time(q))
    assert retention.half_time(q, wind, fraction=0.1) < 6 * 3600
