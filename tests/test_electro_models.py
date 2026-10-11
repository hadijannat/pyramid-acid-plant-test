"""The scene on the conduction grid, the inverted piezoelectric chain and the room acoustics, against closed forms."""
import math

import pytest

from pyramid import ledger, screening
from pyramid.electro import piezo, rooms, sources


@pytest.fixture(scope="module")
def led() -> ledger.Ledger:
    return ledger.load()


@pytest.fixture(scope="module")
def q(led):
    """Every ledger value the models read."""
    ids = (sources.GEOMETRY + sources.MATERIALS + (sources.SHELL,) + sources.SHEETS + piezo.GAS_SOLID + piezo.WET_FILM
           + sum((rooms.inputs(room) for room in rooms.ROOMS), ()))
    return {i: led.q(i) for i in ids}


# --- The pyramid on the grid ------------------------------------------------------------------


def test_grid_refinement_changes_the_kings_chamber_field_by_less_than_5_percent(q):
    # Halving the cells at the chamber from 2 m to 1 m. The volume-mean field in the granite is the converged
    # number; the largest cell value is not, because the field is singular along the cavity's edges, and the test
    # records how far it moves so that nobody takes it for converged.
    for summary in (sources.telluric_summary, sources.lightning_summary):
        coarse, fine = summary(q, 2.0), summary(q, 1.0)
        assert fine["granite_mean"] == pytest.approx(coarse["granite_mean"], rel=0.05)
        assert fine["masonry"] == pytest.approx(coarse["masonry"], rel=0.05)
        assert 0.05 < fine["granite_peak"] / coarse["granite_peak"] - 1 < 0.30


def test_the_telluric_field_is_lower_in_the_raised_body_than_in_the_ground(q):
    # 04 section 5.3 expects this from current continuity: the masonry carries less than the far field, the summit
    # far less, and a resistive granite body holds more than the masonry round it (1.5 times for a sphere).
    found = sources.telluric_summary(q, 3.0)
    assert found["summit"] < 0.1 < found["masonry"] < 1.0
    assert 1.2 < found["granite_mean"] / found["masonry"] < 2.5
    assert found["largest"] == found["granite_peak"] > found["granite_mean"]


def test_the_fields_scale_as_conduction_must(q):
    # Dividing every resistivity by ten leaves a field that is driven by a far field unchanged and divides by ten a
    # field that is driven by a current.
    tenth = q | {"em.limestone_resistivity": q["em.limestone_resistivity"] / 10,
                 "plateau.host_resistivity": q["plateau.host_resistivity"] / 10,
                 "em.granite_conductivity": q["em.granite_conductivity"] * 10}
    assert sources.telluric_summary(tenth, 4.0)["granite_mean"] == pytest.approx(
        sources.telluric_summary(q, 4.0)["granite_mean"], rel=1e-6)
    stroke, scaled = sources.lightning_summary(q, 4.0), sources.lightning_summary(tenth, 4.0)
    assert scaled["granite_mean"] == pytest.approx(stroke["granite_mean"] / 10, rel=1e-6)
    assert scaled["multiple"] == pytest.approx(stroke["multiple"], rel=1e-6)


def test_the_stroke_at_chamber_level_is_the_even_spreading_value_times_a_factor_of_order_one(q):
    # 04 section 4.5: 30 kA over the 162.7 m square section at +43 m in 500 ohm m gives 1.13 A/m2 and 0.57 kV/m;
    # here the section is taken at the chamber's mid-height, 45.9 m. Current that enters at the summit of a cone
    # flows radially, I / (solid angle r^2), which on the axis is 1.7 times the even value at this level.
    side = q["pyr.base_side"] * (1 - 45.9162 / q["pyr.height_original"])
    assert sources.uniform_spreading(q) == pytest.approx(q["em.limestone_resistivity"] / side**2, rel=1e-4)
    assert 30e3 * sources.uniform_spreading(q) == pytest.approx(599.0, rel=0.01)
    found = sources.lightning_summary(q, 3.0)
    assert 1.0 < found["masonry"] / sources.uniform_spreading(q) < 2.0
    assert found["granite_peak"] > found["granite_mean"] > found["masonry"]


def test_ore_sheets_raise_the_field_by_a_factor_of_order_one(q):
    # The most favourable sheets swept: 10 m thick, 300 m deep, 500 m long, of the best hematite measured.
    best = q | {"elec.ore_sheet_thickness": 10.0, "elec.ore_sheet_depth": 300.0, "plateau.vein_leakage_length": 500.0}
    plain, sheets = sources.telluric_summary(q, 3.0), sources.telluric_summary(best, 3.0, 0.003)
    assert 1.2 < sheets["granite_mean"] / plain["granite_mean"] < 3.0
    # earthy hematite is more resistive than the rock: such a sheet changes nothing
    earthy = sources.telluric_summary(best, 3.0, 72000.0)
    assert earthy["granite_mean"] == pytest.approx(plain["granite_mean"], rel=1e-3)


def test_the_chamber_lies_54_m_inside_the_south_face(q):
    # (half-width at chamber level - offset south) x sin(slope) = (79.1 - 11.0) x 0.787
    assert sources.chamber_depth(q) == pytest.approx((79.12 - 11.02) * math.sin(math.radians(51.87)), rel=0.005)


# --- The piezoelectric chain run backwards ----------------------------------------------------


def test_the_needed_field_inverts_tier_0s_chain(q):
    for needed, intensity in ((piezo.needed_field_gas_solid(q), q["ac.gas_solid_intensity"]),):
        assert screening.piezo_intensity(q | {"em.piezo_field_lightning": needed}) == pytest.approx(intensity)
    # closed form: v = sqrt(2 I / Z), E = v t_rise / (d L): 3.81 m/s and 1.36e10 V/m with the bulk coefficient
    speed = math.sqrt(2 * 3000.0 / 413.0)
    assert piezo.needed_field_gas_solid(q) == pytest.approx(speed * 5e-6 / (1.4e-15 * 1.0), rel=1e-9)
    assert piezo.needed_field_gas_solid(q) == pytest.approx(1.361e10, rel=1e-3)
    # the most generous chain: the local-probe coefficient and the heavier air, 2.67e7 V/m, 8.9 times air breakdown
    generous = q | {"em.granite_piezo_d": 7.0e-13, "ac.air_impedance": 428.0}
    assert piezo.needed_field_gas_solid(generous) == pytest.approx(2.674e7, rel=1e-3)


def test_the_wet_film_field_carries_tier_0s_required_level(q):
    # 1 W/cm2 in the liquid over the air-to-water transmission 4 Z1 Z2 / (Z1 + Z2)^2: 896 W/cm2 in the air with the
    # ledger's impedances (09 row 47 has 877 with 428 and 1.5e6), then the same inversion.
    air, water = q["ac.air_impedance"], q["ac.water_impedance"]
    in_air = q["ac.cavitation_intensity"] / (4 * air * water / (air + water) ** 2)
    assert in_air == pytest.approx(8.96e6, rel=0.01)
    needed = piezo.needed_field_wet_film(q)
    assert screening.piezo_intensity(q | {"em.piezo_field_lightning": needed}) == pytest.approx(in_air, rel=1e-9)
    assert needed > 50 * piezo.needed_field_gas_solid(q)


# --- Rooms ------------------------------------------------------------------------------------


def test_the_lowest_axial_mode_of_a_box_is_c_over_2l(q):
    speed = q["ac.sound_speed_air"]
    found = rooms.modes((10.0, 5.0, 4.0), speed, 60.0)
    assert found[0][0] == pytest.approx(speed / 20.0, rel=1e-12) and found[0][1] == (1, 0, 0)
    assert [n for _, n in found[:4]] == [(1, 0, 0), (0, 1, 0), (2, 0, 0), (1, 1, 0)] or \
        [n for _, n in found[:4]] == [(1, 0, 0), (2, 0, 0), (0, 1, 0), (1, 1, 0)]  # (2,0,0) and (0,1,0) coincide
    assert found[3][0] == pytest.approx(speed / 2 * math.hypot(1 / 10.0, 1 / 5.0))
    for room, spec in rooms.ROOMS.items():
        longest = max(q[i] for i in spec["dims"])
        listed = rooms.modes([q[i] for i in spec["dims"]], speed, 110.0)
        assert rooms.lowest_mode(q, room) == pytest.approx(speed / (2 * longest)) == pytest.approx(listed[0][0])
    # 05 section 5.5 item 6, the sanity benchmark: King's Chamber modes near 16, 30 and 33 Hz (c / 2L for its length,
    # height and width: 16.4, 29.4 and 32.8 Hz); 05 section 5.2: the antechamber's first modes are 45 to 104 Hz
    kings = [f for f, _ in rooms.modes([q[i] for i in rooms.ROOMS["kings_chamber"]["dims"]], speed, 34.0)]
    ante = [f for f, _ in rooms.modes([q[i] for i in rooms.ROOMS["antechamber"]["dims"]], speed, 110.0)]
    assert kings[:3] == pytest.approx([16.39, 29.36, 32.78], abs=0.02)
    assert ante[:2] == pytest.approx([45.24, 58.09], abs=0.02)  # its height and its length
    assert any(f == pytest.approx(speed / (2 * q["ante.width"])) == pytest.approx(103.94, abs=0.02) for f in ante)


def test_the_decay_time_is_sabines_and_the_quality_factor_follows_from_it(q):
    # King's Chamber: V = 320.4 m3, S = 293.3 m2, one passage mouth of 1.167 m2, alpha = 0.02: A = 7.03 m2 and
    # T60 = 24 ln(10) V / (c A) = 0.161 V / A = 7.34 s; Q = 2 pi f T60 / (6 ln 10).
    length, width, height = (q[i] for i in rooms.ROOMS["kings_chamber"]["dims"])
    volume, area = length * width * height, 2 * (length * width + length * height + width * height)
    mouth = q["ante.low_passage.width"] * q["ante.low_passage.height"]
    absorbing = q["ac.wall_absorption"] * area + mouth
    expected = 24 * math.log(10) * volume / (q["ac.sound_speed_air"] * absorbing)
    frequency = rooms.reference_frequency(q)
    assert frequency == pytest.approx(45.24, abs=0.01)
    assert rooms.decay_time(q, "kings_chamber", frequency) == pytest.approx(expected, rel=1e-3)  # air adds under 0.1 %
    assert expected == pytest.approx(7.34, abs=0.01)
    assert rooms.quality_factor(q, "kings_chamber", 16.388) == pytest.approx(2 * math.pi * 16.388 * 7.34 / 13.816, rel=2e-3)
    # the air law returns the ledger's 13 kHz value and is frequency squared
    assert rooms.air_attenuation(q, 13000.0) * rooms.NEPER == pytest.approx(q["ac.absorption_13khz"])
    assert rooms.air_attenuation(q, 6500.0) == pytest.approx(rooms.air_attenuation(q, 13000.0) / 4)


def test_the_antechamber_decays_fastest_open_or_shut(q):
    frequency = rooms.reference_frequency(q)
    open_times = {room: rooms.decay_time(q, room, frequency) for room in rooms.ROOMS}
    assert open_times["kings_chamber"] > open_times["grand_gallery"] > open_times["antechamber"]
    assert open_times["antechamber"] == pytest.approx(0.92, abs=0.01)
    shut = {room: rooms.decay_time(q, room, frequency, open_passages=False) for room in rooms.ROOMS}
    assert shut["kings_chamber"] > shut["grand_gallery"] > shut["antechamber"]
    # shut and with one wall absorption the ratio is that of V / S: (320.4 / 293.3) / (18.5 / 44.7) = 2.64
    assert rooms.closed_decay_ratio(q) == pytest.approx((320.4 / 293.3) / (18.5 / 44.7), rel=2e-3)
    assert shut["kings_chamber"] / shut["antechamber"] == pytest.approx(rooms.closed_decay_ratio(q), rel=1e-3)
