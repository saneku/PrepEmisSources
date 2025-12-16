from src import *
import numpy as np


def _decimal_hour(dt):
    """Convert a datetime to decimal hours."""
    return dt.hour + dt.minute / 60.0 + dt.second / 3600.0


def _clone_zero_profile(template_profile):
    """Return a zero profile that preserves the template's timing metadata."""
    dt = template_profile.start_datetime
    zero_profile = VerticalProfile_Zero(
        np.array(template_profile.h, copy=True),
        dt.year,
        dt.month,
        dt.day,
        _decimal_hour(dt),
        max(int(template_profile.duration_sec), 1),
    )
    zero_profile.setDatetime(dt)
    return zero_profile


def approximate_profile_with_suzuki(
    profile,
    k_candidates=(6, 8, 10, 12),
    n_height_samples=12,
    top_buffer_m=1000.0,
):
    """Fit one vertical profile with the closest Suzuki shape using a small grid-search."""
    if profile.duration_sec <= 0 or not np.any(profile.values > 0):
        return _clone_zero_profile(profile)

    dt = profile.start_datetime
    heights = np.array(profile.h, copy=True)
    actual = profile.values
    domain_top = float(heights[-1])

    non_zero_idx = np.where(actual > 0)[0]
    highest_signal = domain_top if non_zero_idx.size == 0 else heights[non_zero_idx[-1]]
    peak_height = heights[np.argmax(actual)]

    lower_bound = max(float(heights[1]) if len(heights) > 1 else float(heights[0]), peak_height + 500.0)
    upper_bound = min(domain_top, highest_signal + top_buffer_m)
    if lower_bound >= upper_bound:
        lower_bound = max(float(heights[0]) + 250.0, 500.0)
        upper_bound = domain_top

    top_candidates = np.linspace(lower_bound, upper_bound, n_height_samples)
    hour_decimal = _decimal_hour(dt)
    duration = max(int(profile.duration_sec), 1)

    best_profile = None
    best_scale = 0.0
    best_error = np.inf

    for k in k_candidates:
        for H in top_candidates:
            try:
                candidate = VerticalProfile_Suzuki(
                    heights,
                    dt.year,
                    dt.month,
                    dt.day,
                    hour_decimal,
                    duration,
                    H=float(H),
                    k=float(k),
                    scale=1.0,
                )
            except ValueError:
                continue

            shape = candidate.values
            denom = float(np.dot(shape, shape))
            if denom <= 0:
                continue

            scale = float(np.dot(actual, shape) / denom)
            if scale < 0:
                continue

            error = float(np.linalg.norm(actual - scale * shape))
            if error < best_error:
                best_error = error
                best_profile = candidate
                best_scale = scale

    if best_profile is None:
        return _clone_zero_profile(profile)

    best_profile.values *= best_scale
    best_profile.duration_sec = profile.duration_sec
    best_profile.setDatetime(dt)
    return best_profile


def approximate_scenario_with_suzuki(
    source_scenario,
    emission_for_result=None,
    k_candidates=(6, 8, 10, 12),
    n_height_samples=12,
):
    """Build a new emission scenario by replacing each profile with its Suzuki fit."""
    target_emission = emission_for_result or source_scenario.type_of_emission
    approximation = EmissionScenario(target_emission)
    for profile in source_scenario.profiles:
        approximation.add_profile(
            approximate_profile_with_suzuki(
                profile,
                k_candidates=k_candidates,
                n_height_samples=n_height_samples,
            )
        )
    return approximation


def scenario_rmse(original_scenario, approximated_scenario):
    """Compute RMSE between two scenarios (assumes aligned profiles and grids)."""
    if original_scenario.getNumberOfProfiles() != approximated_scenario.getNumberOfProfiles():
        raise ValueError("Scenarios must have the same number of profiles to compute RMSE")

    original_matrix = np.array([p.values for p in original_scenario.profiles])
    approx_matrix = np.array([p.values for p in approximated_scenario.profiles])
    if original_matrix.shape != approx_matrix.shape:
        raise ValueError("Scenario grids do not match; interpolate before comparing")

    return float(np.sqrt(np.mean((original_matrix - approx_matrix) ** 2)))

# Example 7: Hayli Gubbi Suzuki fitting example:
# -ingest Hayli Gubbi ash/SO₂ grids (emission strengths at each height/time cell),
# -approximate each snapshot with one Suzuki profile (grid-searching K/H) before plotting/writing.

if __name__ == "__main__":
    # Location of the Hayli Gubbi volcano
    LAT, LON = 13.51, 40.722
    YEAR, MONTH, DAY = 2025, 11, 23
    
    netcdf_handler = WRFNetCDFWriter(source_dir="./")
    y,x = netcdf_handler.findClosestGridCell(LAT,LON)
    staggerred_h=netcdf_handler.getColumn_H(x,y)

    ash_e = Emission_Ash(mass_mt=1.0, lat=LAT, lon=LON, bin_n=10, mean_r=2.4, stddev=1.8)
    so2_e = Emission_SO2(mass_mt=0.3, lat=LAT, lon=LON)
    emisison_scenarios = [ 
        # Ash emissions
        EmissionScenario_HayliGubbi(ash_e,"./scenarios/Hayli Gubbi_Ukhov_2025/ash_emissions.txt"),
        # SO2 emissions
        EmissionScenario_HayliGubbi(so2_e,"./scenarios/Hayli Gubbi_Ukhov_2025/so2_emisisons.txt")
        ]

    #cleaning the scenarios from noise by removing emissions below certain heights and times
    emisison_scenarios[0].set_values_by_criteria(0, height_min_m=0, height_max_m=2000)
    emisison_scenarios[0].set_values_by_criteria(0, height_min_m=16000, height_max_m=24000)
    emisison_scenarios[1].set_values_by_criteria(0, height_min_m=0, height_max_m=7500)
    emisison_scenarios[1].set_values_by_criteria(0, time_start='2025-11-24T08:00')#, time_end='2025-11-24T12:00') 
    emisison_scenarios[1].set_values_by_criteria(0, height_min_m=17000, height_max_m=30000)

    #emission_writer.plot_scenarios()
    emisison_scenarios[0].plot()
    emisison_scenarios[1].plot()
    emisison_scenarios[0].save_fig("ash_hayli_gubbi_ash_original.png", dpi=300)
    emisison_scenarios[1].save_fig("so2_hayli_gubbi_so2_original.png", dpi=300)

    print("Starting Suzuki approximations...")
    # Build Suzuki-based approximations for ash and SO2 scenarios
    approx_scenarios = []
    for idx, scen in enumerate(emisison_scenarios):
        approx = approximate_scenario_with_suzuki(
            scen,
            emission_for_result=scen.type_of_emission,
            k_candidates=(6, 8, 10, 12, 14),
            n_height_samples=16,
        )
        approx.normalize_by_total_mass()
        try:
            rmse = scenario_rmse(scen, approx)
            print(f"Suzuki approximation RMSE for scenario {idx}: {rmse:.3e}")
        except ValueError as err:
            print(f"Could not compute RMSE for scenario {idx}: {err}")
        approx_scenarios.append(approx)

    del emisison_scenarios  # Free memory

    approx_writer = EmissionWriter_NonUniformInHeightProfiles(approx_scenarios, netcdf_handler, output_interval_m=30)
    approx_writer.write()
    approx_writer.plot_scenarios()
    
    # SO2 mass emitted in first 2 hours
    # according to observations, it should be around 0.043 Mt
    print(approx_scenarios[1].get_emitted_mass_within(2))
    
    approx_scenarios[0].save_fig("ash_hayli_gubbi_ash_suzuki_approximation.png", dpi=300)
    approx_scenarios[1].save_fig("so2_hayli_gubbi_so2_suzuki_approximation.png", dpi=300)