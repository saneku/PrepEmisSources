from src import *
import numpy as np
import os
from datetime import datetime, timedelta

# Example 5:
# explosive eruption at Hayli Gubbi was detected in satellite data at around 0830 UTC on 23 November 2025
# The eruption produced an ash plume that reached an altitude of approximately 14 km
# and drifted eastward over the Red Sea. The eruption was also accompanied by a significant SO2 plume.
# https://volcano.si.edu/volcano.cfm?vn=221091

# This script was updated with the ash+SO2 setup copied from example5_5.py.
# Ash: read from ./scenarios/Hayli Gubbi_Ukhov_2025/ash_emissions.txt
# (EmissionScenario_HayliGubbi), with low-level emissions (0-5 km) removed.
# SO2: synthetic 30-minute Suzuki/zero pulse sequence:
# 08:30-11:00 UTC descending tops; 11:00-14:00 UTC fixed 17.5 km;
# 14:00-23:00 UTC mostly zeros with a repeated active block at 18:00-20:30;
# 23:00-01:00 UTC on 24 Nov fixed 15 km, then a final zero profile.
# Both ash and SO2 pulses are reduced by 2x after 17:00 UTC on 23 Nov 2025.

if __name__ == "__main__":
    LAT, LON = 13.51, 40.722
    YEAR, MONTH, DAY = 2025, 11, 23

    ash_mass_mt = 0.8
    so2_mass_mt = 0.15

    PROFILE_INTERVAL_MIN = 30
    DURATION = PROFILE_INTERVAL_MIN * 60
    REDUCE_AFTER_DT = datetime(YEAR, MONTH, DAY, 17, 0)

    netcdf_handler = WRFNetCDFWriter(source_dir="./")
    y, x = netcdf_handler.findClosestGridCell(LAT, LON)
    staggerred_h = netcdf_handler.getColumn_H(x, y)

    # Ash emissions from example6.py
    ash_e = Emission_Ash(mass_mt=ash_mass_mt, lat=LAT, lon=LON, bin_n=10, mean_r=2.4, stddev=1.8)
    ash_e.setMassFractions(np.array([0.017, 0.158, 0.422, 0.326, 0.072, 0.005, 0.000, 0.000, 0.000, 0.000]))
    ash_scenario = EmissionScenario_HayliGubbi(
        ash_e,
        "./scenarios/Hayli Gubbi_Ukhov_2025/ash_emissions.txt",
    )
    ash_scenario.set_values_by_criteria(0, height_min_m=0, height_max_m=5000)

    # SO2 emissions copied from example5_5.py
    def suzuki_args_dt(dt_obj, top_height, scale):
        hour_decimal = dt_obj.hour + dt_obj.minute / 60.0
        return [
            staggerred_h,
            dt_obj.year,
            dt_obj.month,
            dt_obj.day,
            hour_decimal,
            DURATION,
            float(top_height),
            10,
            float(scale),
        ]

    def zero_args_dt(dt_obj):
        hour_decimal = dt_obj.hour + dt_obj.minute / 60.0
        return [staggerred_h, dt_obj.year, dt_obj.month, dt_obj.day, hour_decimal, DURATION]

    so2_start_dt = datetime(YEAR, MONTH, DAY, 8, 30)
    so2_final_zero_dt = datetime(YEAR, MONTH, DAY + 1, 1, 0)
    interval = timedelta(minutes=PROFILE_INTERVAL_MIN)

    all_so2_times = []
    current_dt = so2_start_dt
    while current_dt <= so2_final_zero_dt:
        all_so2_times.append(current_dt)
        current_dt += interval

    block1_end = datetime(YEAR, MONTH, DAY, 11, 0)
    block2_end = datetime(YEAR, MONTH, DAY, 14, 0)
    pause_end = datetime(YEAR, MONTH, DAY, 23, 0)
    block1_duration = block1_end - so2_start_dt
    block1b_start = datetime(YEAR, MONTH, DAY, 18, 0)
    block1b_end = block1b_start + block1_duration

    block1_steps = len([dt for dt in all_so2_times if dt < block1_end])
    block1_active_steps = block1_steps
    block1_active_end = so2_start_dt + block1_active_steps * interval
    block1b_active_end = block1b_start + block1_active_steps * interval

    block1_times = [dt for dt in all_so2_times if dt < block1_active_end]
    block1_gap_times = [dt for dt in all_so2_times if block1_active_end <= dt < block1_end]
    block1b_times = [dt for dt in all_so2_times if block1b_start <= dt < block1b_active_end]
    block1b_gap_times = [dt for dt in all_so2_times if block1b_active_end <= dt < block1b_end]
    block2_times = [dt for dt in all_so2_times if block1_end <= dt < block2_end]
    pause_times = [dt for dt in all_so2_times if block2_end <= dt < pause_end and not (block1b_start <= dt < block1b_end)]
    block3_times = [dt for dt in all_so2_times if pause_end <= dt < so2_final_zero_dt]
    pause_times_pre = [dt for dt in pause_times if dt < block1b_start]
    pause_times_post = [dt for dt in pause_times if dt >= block1b_end]

    block1_tops = np.linspace(14000.0, 10500.0, len(block1_times))
    block1_scales = np.linspace(1.48, 0.1, len(block1_times))
    block1b_tops = np.linspace(14000.0, 10500.0, len(block1b_times))
    block1b_scales = np.linspace(0.50, 0.1, len(block1b_times))
    block2_scales = np.linspace(1.0, 0.1, len(block2_times))
    block3_scales = np.linspace(0.50, 0.1, len(block3_times))

    so2_profiles = []
    for dt_obj, top_h, scale in zip(block1_times, block1_tops, block1_scales):
        so2_profiles.append((VerticalProfile_Suzuki, suzuki_args_dt(dt_obj, top_h, scale)))
    for dt_obj in block1_gap_times:
        so2_profiles.append((VerticalProfile_Zero, zero_args_dt(dt_obj)))
    for dt_obj, scale in zip(block2_times, block2_scales):
        so2_profiles.append((VerticalProfile_Suzuki, suzuki_args_dt(dt_obj, 17500.0, scale)))
    for dt_obj in pause_times_pre:
        so2_profiles.append((VerticalProfile_Zero, zero_args_dt(dt_obj)))
    for dt_obj, top_h, scale in zip(block1b_times, block1b_tops, block1b_scales):
        so2_profiles.append((VerticalProfile_Suzuki, suzuki_args_dt(dt_obj, top_h, scale)))
    for dt_obj in block1b_gap_times:
        so2_profiles.append((VerticalProfile_Zero, zero_args_dt(dt_obj)))
    for dt_obj in pause_times_post:
        so2_profiles.append((VerticalProfile_Zero, zero_args_dt(dt_obj)))
    for dt_obj, scale in zip(block3_times, block3_scales):
        so2_profiles.append((VerticalProfile_Suzuki, suzuki_args_dt(dt_obj, 15000.0, scale)))
    so2_profiles.append((VerticalProfile_Zero, zero_args_dt(so2_final_zero_dt)))

    so2_scenario = EmissionScenario(Emission_SO2(mass_mt=so2_mass_mt, lat=LAT, lon=LON))
    for p, args in so2_profiles:
        so2_scenario.add_profile(p(*args))

    # Decrease emission pulse intensity by 2x after 17:00 UTC on 23 Nov 2025.
    # With 30-minute profiles, this affects 17:30 onward.
    ash_scenario.scale_values_by_criteria(
        0.5,
        condition_func=lambda _h, dt: dt > REDUCE_AFTER_DT,
    )
    so2_scenario.scale_values_by_criteria(
        0.5,
        condition_func=lambda _h, dt: dt > REDUCE_AFTER_DT,
    )

    emission_writer = EmissionWriter_NonUniformInHeightProfiles(
        [ash_scenario, so2_scenario],
        netcdf_handler,
        output_interval_m=PROFILE_INTERVAL_MIN,
    )

    print(so2_scenario.get_emitted_mass_within(2))
    emission_writer.write()

    # Always save plots so results are available in headless environments.
    emission_writer.plot_scenarios(
        output_dir=".",
        filename_fmt="example5_5_scenario_{index:02d}_{material}.png",
    )
    print(
        "Saved scenario plots: "
        "example5_5_scenario_01_ash.png, "
        "example5_5_scenario_02_so2.png"
    )

    # Show interactive figures only when a display is available.
    if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
        emission_writer.plot_scenarios()
    else:
        print("No interactive display detected; skipped on-screen plotting.")
