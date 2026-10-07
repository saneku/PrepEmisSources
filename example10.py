from src import *
import numpy as np
from datetime import datetime, timedelta
from scipy.stats import norm

# Example 10:
# Emissions of ash, SO2, sulfate and water vapor for the 2015 Calbuco eruption, built from the
# source term inverted in Figure 10 of
#   Mingari et al. (2023), Reconstructing tephra fall deposits via ensemble-based data
#   assimilation techniques, Geosci. Model Dev., 16, 3459-3478, doi:10.5194/gmd-16-3459-2023
#
# The paper describes two eruptive phases (hours are UTC):
#   1st phase: starts 22 Apr 2015 21:00, lasts ~1.6 h, 0.078 km3 (31.6 %), column top ~20 km a.s.l.
#   2nd phase: starts 23 Apr 2015 04:00, lasts   6 h,  0.169 km3 (68.4 %), column top ~16 km a.s.l.
# with a bulk density of 800 kg/m3 (total 0.247 km3 -> ~198 Mt).
#
# Compared with calbuco_example.py this script
#   * uses a uniform time step with a smooth (trapezoidal) emission rate per phase instead of
#     constant hourly Umbrella profiles, so the rise and fall of each pulse (Fig. 10) is resolved;
#   * puts the higher cloud in the 1st phase and the lower one in the 2nd phase (as in the paper);
#   * uses a Suzuki-type vertical mass distribution (Pfeiffer et al., 2005, Eq. 26 of the paper),
#     measured from the vent altitude;
#   * derives the ash bin fractions from the paper's bi-Gaussian grain-size distribution;
#   * builds all four species with one function (no copy-pasted profile lists), and has no time gaps.
#
# The phase timing, volumes, density and top heights are taken from the paper's text. The ramp
# duration and the Suzuki parameter A of each phase were chosen by eye to resemble Fig. 10.
# SO2, sulfate and water vapor masses are NOT given in the paper; they are kept from calbuco_example.py.

# ----------------------------------------------------------------------------------------------
# Eruption source parameters
# ----------------------------------------------------------------------------------------------
LAT, LON = -41.326, -72.614
VENT_ALTITUDE_M = 2003.0                    # Calbuco summit, a.s.l.
ERUPTION_DAY = datetime(2015, 4, 22)        # 'hours since 22 April 2015 00 UTC' as in Fig. 10
BULK_DENSITY = 800.0                        # kg/m3
RAMP_HOURS = 0.25                           # duration of the linear rise/decay of each pulse

PHASES = [
    dict(start_h=21.0, duration_h=1.6, volume_km3=0.078, top_asl_m=20000.0, suzuki_A=2.5),
    dict(start_h=28.0, duration_h=6.0, volume_km3=0.169, top_asl_m=16000.0, suzuki_A=4.0),
]
SUZUKI_LAMBDA = 3.0

# Time axis of the output: from the first emission to the first zero profile after the last phase
START_H, END_H = 21.0, 36.0                 # hours since ERUPTION_DAY
DT_MIN = 10                                 # time step of the emission profiles, minutes

# Total emitted mass, Mt. 1 Mt = 1e9 kg; 1 km3 = 1e9 m3
ASH_MASS_MT = sum(p["volume_km3"] for p in PHASES) * BULK_DENSITY
SO2_MASS_MT = 0.40
SULFATE_MASS_MT = 0.60
WATERVAPOR_MASS_MT = 3.0

# Total grain-size distribution (TGSD) of the paper: two Gaussians in phi units (d_mm = 2**-phi)
TGSD = [dict(weight=0.15, mean_phi=-1.2, std_phi=1.71),    # coarse population
        dict(weight=0.85, mean_phi=3.49, std_phi=1.46)]    # fine population


def tgsd_ash_mass_fractions():
    """
    Mass fraction of the 10 ash bins, ordered as expected by Emission_Ash.setMassFractions
    (smallest bin first, i.e. 'bin10' ... 'bin1').

    The bins are the same radius ladder (1.95 ... 1000 micron) that Emission_Ash uses, so the
    diameter is 2*r. Mass beyond the last bin (d > 2 mm) is dropped and the rest renormalised.
    """
    r_hi = 1.953125 * 2.0 ** np.arange(10)                  # micron
    r_lo = np.concatenate(([1.955e-02], r_hi[:-1]))
    phi_of_r = lambda r_um: -np.log2(2.0 * r_um / 1000.0)    # radius [um] -> phi of the diameter

    fractions = np.zeros(10)
    for mode in TGSD:
        cdf = lambda r_um: norm.cdf(phi_of_r(r_um), loc=mode["mean_phi"], scale=mode["std_phi"])
        # larger radius = smaller phi, so P(r_lo < r < r_hi) = cdf(phi(r_lo)) - cdf(phi(r_hi))
        fractions += mode["weight"] * (cdf(r_lo) - cdf(r_hi))

    print(f"TGSD: {100 * (1.0 - fractions.sum()):.1f} % of the mass is outside the 10 bins and is dropped")
    return fractions / fractions.sum()


def suzuki_shape(z_at_m, top_asl_m, A, lam=SUZUKI_LAMBDA, vent_m=VENT_ALTITUDE_M):
    """
    Vertical distribution of the emitted mass among the model levels (sums to 1):
    dm/dz ~ {(1 - z/H) exp[A (z/H - 1)]}^lam, with z measured from the vent and H the column top
    above the vent. Weighted by the layer thickness, because the profile values are per level.
    """
    z = np.asarray(z_at_m, dtype=float)
    VerticalProfile._ensure_within_domain_top(z, top_asl_m, "top_asl_m", "Suzuki (Calbuco)")

    edges = np.concatenate(([max(z[0] - 0.5 * (z[1] - z[0]), 0.0)], 0.5 * (z[1:] + z[:-1]),
                            [z[-1] + 0.5 * (z[-1] - z[-2])]))
    dz = np.diff(edges)

    H = top_asl_m - vent_m
    x = (z - vent_m) / H
    inside = (x > 0.0) & (x < 1.0)
    shape = np.zeros_like(z)
    shape[inside] = ((1.0 - x[inside]) * np.exp(A * (x[inside] - 1.0))) ** lam
    shape *= dz
    return shape / shape.sum()


def emission_rate_kg_s(t_h):
    """
    Mass eruption rate [kg/s] at times t_h (hours since ERUPTION_DAY), summed over the phases.
    Each phase is a trapezoid: linear rise, plateau and linear decay. The plateau is set so that
    the phase erupts exactly volume_km3 * BULK_DENSITY.
    """
    t_h = np.asarray(t_h, dtype=float)
    rate = np.zeros_like(t_h)
    for ph in PHASES:
        mass_kg = ph["volume_km3"] * 1.0e9 * BULK_DENSITY
        peak = mass_kg / ((ph["duration_h"] - RAMP_HOURS) * 3600.0)     # area = peak*(D - ramp)
        s, d = ph["start_h"], ph["duration_h"]
        rate += np.interp(t_h, [s, s + RAMP_HOURS, s + d - RAMP_HOURS, s + d], [0.0, peak, peak, 0.0],
                          left=0.0, right=0.0)
    return rate


def interval_mean_rate_kg_s(t_start_h, dt_min):
    """Mean mass eruption rate over [t_start, t_start + dt]; keeps the mass independent of dt_min."""
    sub_h = t_start_h + (np.arange(dt_min * 10) + 0.5) / (10.0 * 60.0)   # 6-second sub-steps
    return emission_rate_kg_s(sub_h).mean()


def phase_at(t_h):
    """The phase active at t_h (hours), or None. Used to choose the vertical shape."""
    for ph in PHASES:
        if ph["start_h"] <= t_h < ph["start_h"] + ph["duration_h"]:
            return ph
    return None


def build_profiles(staggerred_h):
    """
    One list of VerticalProfile with a fixed time step, in [Mt/s] summed over the levels.
    Normalised shapes are scaled with the (interval-mean) eruption rate. The last profile is
    VerticalProfile_Zero, as required by the writer.
    """
    n_steps = int(round((END_H - START_H) * 60 / DT_MIN))
    profiles = []
    for k in range(n_steps + 1):
        t_h = START_H + k * DT_MIN / 60.0
        when = ERUPTION_DAY + timedelta(hours=t_h)
        date_args = (when.year, when.month, when.day, when.hour + when.minute / 60.0, DT_MIN * 60)

        if k == n_steps:
            profile = VerticalProfile_Zero(staggerred_h, *date_args)
        else:
            rate_mt_s = interval_mean_rate_kg_s(t_h, DT_MIN) * 1.0e-9
            # a time step overlapping a phase boundary is assigned to the phase active at its middle
            ph = phase_at(t_h + 0.5 * DT_MIN / 60.0)
            if rate_mt_s == 0.0 or ph is None:
                profile = VerticalProfile_Zero(staggerred_h, *date_args)
            else:
                shape = suzuki_shape(staggerred_h, ph["top_asl_m"], ph["suzuki_A"])
                profile = VerticalProfile(staggerred_h, rate_mt_s * shape, *date_args)
        profile.setDatetime(when)
        profiles.append(profile)
    return profiles


def build_scenario(emission, staggerred_h):
    scenario = EmissionScenario(emission)
    for profile in build_profiles(staggerred_h):
        scenario.add_profile(profile)
    return scenario


def print_summary(scenario):
    """Compare the discretised source with the numbers quoted in the paper."""
    total = scenario.getScenarioEmittedMass()
    print(f"\nDiscretised ash source: {total:.1f} Mt (target {ASH_MASS_MT:.1f} Mt), "
          f"peak rate {max(np.sum(p.values) for p in scenario.profiles) * 1e9:.2e} kg/s")
    for i, ph in enumerate(PHASES, start=1):
        s = ERUPTION_DAY + timedelta(hours=ph["start_h"])
        e = s + timedelta(hours=ph["duration_h"])
        mass = sum(p.getProfileEmittedMass() for p in scenario.profiles if s <= p.start_datetime < e)
        print(f"  phase {i}: {mass / total * 100:.1f} % of the mass, "
              f"{mass * 1e9 / BULK_DENSITY / 1e9:.3f} km3 (paper: {ph['volume_km3']:.3f} km3)")


if __name__ == "__main__":
    # Path to the directory with the 'wrfinput_d01' file
    netcdf_handler = WRFNetCDFWriter(source_dir="./")
    y, x = netcdf_handler.findClosestGridCell(LAT, LON)
    # heights of the 'mass' points (a.s.l.) in the model column that contains the volcano
    staggerred_h = netcdf_handler.getColumn_H(x, y)

    ash_e = Emission_Ash(mass_mt=ASH_MASS_MT, lat=LAT, lon=LON)
    ash_e.setMassFractions(tgsd_ash_mass_fractions())

    emission_scenarios = [
        build_scenario(ash_e, staggerred_h),
        build_scenario(Emission_SO2(mass_mt=SO2_MASS_MT, lat=LAT, lon=LON), staggerred_h),
        build_scenario(Emission_Sulfate(mass_mt=SULFATE_MASS_MT, lat=LAT, lon=LON), staggerred_h),
        build_scenario(Emission_WaterVapor(mass_mt=WATERVAPOR_MASS_MT, lat=LAT, lon=LON), staggerred_h),
    ]
    print_summary(emission_scenarios[0])

    # The profiles are already on the model levels and on a uniform time grid, so only the height
    # interpolation (a no-op here) and the top-of-domain check are done by this writer.
    emission_writer = EmissionWriter_NonUniformInHeightProfiles(emission_scenarios, netcdf_handler,
                                                                output_interval_m=DT_MIN)
    emission_writer.write()

    # Plot the scenarios (compare the ash panel with Fig. 10 of the paper)
    emission_writer.plot_scenarios()
