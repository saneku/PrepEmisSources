from src import *
import sys
import numpy as np
from datetime import datetime, timedelta
from scipy.stats import norm

# Example 10:
# Emissions of ash, SO2, sulfate and water vapor for the 2015 Calbuco eruption, reproducing the
# source term inverted in Figure 10 of
# Mingari et al. (2023), Reconstructing tephra fall deposits via ensemble-based data
# assimilation techniques, Geosci. Model Dev., 16, 3459-3478, doi:10.5194/gmd-16-3459-2023
#
# Figure 10 shows two eruptive phases (hours are UTC since 22 April 2015 00:00):
#   1st phase: ~20.7 - 22.6 h, 0.078 km3 (31.6 %), plateau ~12.5e6 kg/s, cloud up to ~20 km a.s.l.
#   2nd phase: ~27.7 - 34.0 h, 0.169 km3 (68.4 %), plateau ~6.3e6 kg/s, cloud up to ~16 km a.s.l.
# with a bulk density of 800 kg/m3 (total 0.247 km3 -> ~198 Mt).
#
# Everything below was read off the figure itself (digitised from the PDF):
#   * the mass eruption rate in time = the dash-dotted line (table of rate values per phase), which
#     is then scaled so that every phase erupts exactly the volume given in the paper;
#   * the vertical distribution = the colour map. Its unit is the linear source strength,
#     kg s-1 m-1, i.e. mass rate per metre of altitude. Each phase is constant in time and is
#     described by a fit to the colour map. The 1st phase reaches down only to ~7.5 km and is
#     described by a Suzuki distribution between 7.5 and ~20 km. The 2nd phase is two parabolic
#     layers (~12 km and ~14.6 km) plus a weak broad low-level tail (amplitude, centre, half-width).
#   The vertical integral of the colour map reproduces the plateau rates of the dash-dotted line
#   (12.2e6 and 6.2e6 kg/s), which confirms the unit and the digitisation.
# SO2, sulfate and water vapor masses are NOT given in the paper; the values below are assumptions.

# This scenario is used in:
#   Rizza et al., "Evaluating the Cloud Radiative Forcing Impacts of the 2015 Calbuco eruption",
#   in "Atmospheric Chemistry-Climate Interactions: Advances in Coupled Modeling and Applications".

# ----------------------------------------------------------------------------------------------
# Eruption source parameters
# ----------------------------------------------------------------------------------------------
LAT, LON = -41.326, -72.614                 # Calbuco
ERUPTION_DAY = datetime(2015, 4, 22)        # 'hours since 22 April 2015 00 UTC' as in Fig. 10
BULK_DENSITY = 800.0                        # kg/m3

PHASES = [
    dict(volume_km3=0.078,
         # (hours since ERUPTION_DAY, mass eruption rate in 1e6 kg/s): the dash-dotted line of Fig. 10
         rate_table=[(20.70, 0.0), (20.80, 2.7), (20.95, 7.1), (21.20, 11.8), (21.30, 12.4),
                     (21.90, 12.8), (22.10, 11.6), (22.30, 8.8), (22.45, 2.2), (22.55, 0.0)],
         # Suzuki distribution between base and top [km a.s.l.]: with x = (z - base)/(top - base),
         # dm/dz ~ {(1 - x) exp[A (x - 1)]}^lam (Pfeiffer et al., 2005; Eq. 26 of the paper).
         # A, lam were fitted to the colour map; the profile is zero below base_km.
         suzuki=dict(base_km=7.5, top_km=20.4, A=2.13, lam=4.35)),
    dict(volume_km3=0.169,
         rate_table=[(27.65, 0.0), (27.75, 1.0), (27.85, 3.0), (27.95, 5.0), (28.30, 6.4),
                     (30.60, 6.2), (33.35, 6.85), (33.60, 5.4), (33.75, 2.9), (33.90, 1.4),
                     (34.05, 0.0)],
         # (amplitude, centre [km a.s.l.], half-width [km]) of the parabolas A*(1 - ((z-c)/w)^2),
         # amplitude in 1e3 kg s-1 m-1 (only the shape matters, the rate comes from rate_table)
         parabolas=[(0.69, 11.96, 2.00),      # lower layer
                    (0.74, 14.61, 1.38),      # upper layer
                    (0.41, 11.85, 5.09)]),    # broad low-level tail (set the amplitude to 0 to drop it)
]

# Time axis of the output: from the first emission to the first zero profile after the last phase
START_H, END_H = 20.5, 34.5                 # hours since ERUPTION_DAY
DT_MIN = 10                                 # time step of the emission profiles, minutes

# Total emitted mass, Mt. 1 Mt = 1e9 kg; 1 km3 = 1e9 m3
#ASH_MASS_MT = sum(p["volume_km3"] for p in PHASES) * BULK_DENSITY
ASH_MASS_MT = 200.0
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


def parabolic_density(z_km, parabolas):
    """Linear source strength [arbitrary units per metre] = sum of parabolas A*(1-((z-c)/w)^2), zero outside."""
    z_km = np.asarray(z_km, dtype=float)
    density = np.zeros_like(z_km)
    for amplitude, centre, half_width in parabolas:
        u = (z_km - centre) / half_width
        density += np.where(np.abs(u) < 1.0, amplitude * (1.0 - u ** 2), 0.0)
    return density


def suzuki_density(z_km, base_km, top_km, A, lam):
    """Suzuki linear source strength [arbitrary units per metre] between base_km and top_km, zero outside."""
    z_km = np.asarray(z_km, dtype=float)
    x = (z_km - base_km) / (top_km - base_km)
    density = np.zeros_like(z_km)
    inside = (x > 0.0) & (x < 1.0)
    density[inside] = ((1.0 - x[inside]) * np.exp(A * (x[inside] - 1.0))) ** lam
    return density


def vertical_density(z_km, phase):
    """Linear source strength of a phase: Suzuki if the phase defines 'suzuki', else its parabolas."""
    if "suzuki" in phase:
        return suzuki_density(z_km, **phase["suzuki"])
    return parabolic_density(z_km, phase["parabolas"])


def vertical_shape(z_at_m, phase, max_lost=0.05):
    """
    Distribution of the emitted mass among the model levels (sums to 1). The colour map of Fig. 10
    is a density per metre, so it is multiplied by the layer thickness: the profile values are
    per level. Mass above the model top would be lost; fail if that is more than max_lost.
    """
    z = np.asarray(z_at_m, dtype=float)
    edges = np.concatenate(([max(z[0] - 0.5 * (z[1] - z[0]), 0.0)], 0.5 * (z[1:] + z[:-1]),
                            [z[-1] + 0.5 * (z[-1] - z[-2])]))
    dz = np.diff(edges)

    z_fine_km = np.arange(0.0, 40.0, 0.01)
    fine = vertical_density(z_fine_km, phase)
    lost = fine[z_fine_km * 1000.0 > edges[-1]].sum() / fine.sum()
    if lost > max_lost:
        raise ValueError(f"{100 * lost:.1f} % of the emitted mass would be above the model top "
                         f"({edges[-1]:.0f} m). Use a wrfinput with a higher model top or lower the profile.")
    if lost > 0.005:
        print(f"Note: {100 * lost:.1f} % of the vertical profile is above the model top and is dropped")

    shape = vertical_density(z / 1000.0, phase) * dz
    return shape / shape.sum()


def phase_rate_kg_s(t_h, phase):
    """
    Mass eruption rate [kg/s] of one phase at times t_h (hours since ERUPTION_DAY): the digitised
    rate_table, scaled so that the phase erupts exactly volume_km3 * BULK_DENSITY.
    """
    table_t, table_rate = np.array(phase["rate_table"], dtype=float).T
    table_mass_kg = np.trapezoid(table_rate, table_t) * 3600.0 * 1.0e6
    scale = phase["volume_km3"] * 1.0e9 * BULK_DENSITY / table_mass_kg
    return scale * 1.0e6 * np.interp(t_h, table_t, table_rate, left=0.0, right=0.0)


def emission_rate_kg_s(t_h):
    """Mass eruption rate [kg/s] at times t_h, summed over the phases."""
    t_h = np.asarray(t_h, dtype=float)
    return sum(phase_rate_kg_s(t_h, ph) for ph in PHASES)


def interval_mean_rate_kg_s(t_start_h, dt_min, phase):
    """Mean mass eruption rate of a phase over [t_start, t_start + dt]; keeps the mass independent of dt_min."""
    sub_h = t_start_h + (np.arange(dt_min * 10) + 0.5) / (10.0 * 60.0)   # 6-second sub-steps
    return phase_rate_kg_s(sub_h, phase).mean()


def phase_window_h(phase):
    """(start, end) of a phase in hours since ERUPTION_DAY: the extent of its rate table."""
    return phase["rate_table"][0][0], phase["rate_table"][-1][0]


def build_profiles(staggerred_h):
    """
    One list of VerticalProfile with a fixed time step, in [Mt/s] summed over the levels.
    Each phase contributes its normalised vertical shape scaled with its interval-mean eruption
    rate (the phases do not overlap in time). The last profile is VerticalProfile_Zero, as
    required by the writer.
    """
    shapes = [vertical_shape(staggerred_h, ph) for ph in PHASES]   # constant in time

    n_steps = int(round((END_H - START_H) * 60 / DT_MIN))
    profiles = []
    for k in range(n_steps + 1):
        t_h = START_H + k * DT_MIN / 60.0
        when = ERUPTION_DAY + timedelta(hours=t_h)
        date_args = (when.year, when.month, when.day, when.hour + when.minute / 60.0, DT_MIN * 60)

        values = np.zeros(len(staggerred_h))
        if k < n_steps:
            for ph, shape in zip(PHASES, shapes):
                values += interval_mean_rate_kg_s(t_h, DT_MIN, ph) * 1.0e-9 * shape      # kg/s -> Mt/s
        if values.any():
            profile = VerticalProfile(staggerred_h, values, *date_args)
        else:
            profile = VerticalProfile_Zero(staggerred_h, *date_args)
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
    paper_mt = sum(p["volume_km3"] for p in PHASES) * BULK_DENSITY
    print(f"\nDiscretised ash source: {total:.1f} Mt (paper volumes: {paper_mt:.1f} Mt; "
          f"the scenario is normalised to {ASH_MASS_MT:.1f} Mt when written), "
          f"peak rate {max(np.sum(p.values) for p in scenario.profiles) * 1e9:.2e} kg/s")
    for i, ph in enumerate(PHASES, start=1):
        start, end = phase_window_h(ph)
        s, e = ERUPTION_DAY + timedelta(hours=start), ERUPTION_DAY + timedelta(hours=end)
        # every time step that overlaps the phase window
        mass = sum(p.getProfileEmittedMass() for p in scenario.profiles
                   if p.start_datetime < e and p.start_datetime + timedelta(seconds=p.duration_sec) > s)
        print(f"  phase {i}: {mass / total * 100:.1f} % of the mass, "
              f"{mass * 1e9 / BULK_DENSITY / 1e9:.3f} km3 (paper: {ph['volume_km3']:.3f} km3)")


if __name__ == "__main__":
    # Path to the directory with the 'wrfinput_d01' file
    netcdf_handler = WRFNetCDFWriter(source_dir="./")
    try:
        y, x = netcdf_handler.findClosestGridCell(LAT, LON)
    except ValueError as err:
        sys.exit(f"ERROR: {err}")
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

    # Save the scenarios as images (compare the ash panel with Fig. 10 of the paper).
    # Works without a display; use emission_writer.plot_scenarios() to open windows instead.
    for scenario, name in zip(emission_scenarios, ["ash", "so2", "sulfate", "h2o"]):
        scenario.save_fig(f"{name}_calbuco.png", dpi=300)
