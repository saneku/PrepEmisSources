from src import *
import numpy as np
from datetime import datetime, timedelta

# Example 5:
# explosive eruption at Hayli Gubbi was detected in satellite data at around 0830 UTC on 23 November 2025
# The eruption produced an ash plume that reached an altitude of approximately 14 km
# and drifted eastward over the Red Sea. The eruption was also accompanied by a significant SO2 plume.
# https://volcano.si.edu/volcano.cfm?vn=221091

# Ash: 08:30-15:30 UTC on 23 Nov 2025, thirty-minute VerticalProfile_Suzuki snapshots 
# with tops descending 14->7 km, scale 1.0->0.1, then a final zero at 15:30 UTC.

# SO2: 08:30-11:00 UTC same descending Suzuki sequence; 11:00-13:00 UTC Suzuki at fixed 17.5 km (scale 1.0->0.1); 
# 13:00-23:00 UTC pause with zeros except a repeat of the first block from 18:00-20:30 UTC (half active, half zero); 
# 23:00-01:00 UTC on 24 Nov Suzuki at 15 km (scale 1.0->0.1), then zero at 01:00 UTC.

if __name__ == "__main__":
    # Prescribe the location of the volcano, start date, and profile's duration in seconds
    LAT, LON = 13.51, 40.722
    YEAR, MONTH, DAY = 2025, 11, 23
    START_HOUR = 8.5
    END_HOUR = 15.5
    PROFILE_INTERVAL_MIN = 30
    DURATION = PROFILE_INTERVAL_MIN * 60     # seconds
    TOTAL_MINUTES = (END_HOUR - START_HOUR) * 60
    NUM_INTERVALS = int(TOTAL_MINUTES / PROFILE_INTERVAL_MIN)
    if not np.isclose(NUM_INTERVALS * PROFILE_INTERVAL_MIN, TOTAL_MINUTES):
        raise ValueError("Eruption duration must be divisible by PROFILE_INTERVAL_MIN.")
    if NUM_INTERVALS <= 0:
        raise ValueError("END_HOUR must be greater than START_HOUR for Suzuki profiles.")
    SUZUKI_TOP_START = 14000.0
    SUZUKI_TOP_END = 7000.0

    # find the location of the volcano using the information from the wrfinput file
    netcdf_handler = WRFNetCDFWriter(source_dir="./")
    j, i = netcdf_handler.findClosestGridCell(lat=LAT, lon=LON)
    #get the height of the 'mass' points in the wrfinput file
    staggerred_h = netcdf_handler.getColumn_H(i, j)

    interval_hours = PROFILE_INTERVAL_MIN / 60.0
    # Build Suzuki profiles that decrease the column top from 14 km to 7 km
    profile_hours = START_HOUR + np.arange(NUM_INTERVALS) * interval_hours
    profile_tops = np.linspace(SUZUKI_TOP_START, SUZUKI_TOP_END, NUM_INTERVALS)
    profile_scales = np.linspace(1.0, 0.1, NUM_INTERVALS)

    def suzuki_args(start_hour, top_height, scale):
        return [staggerred_h, YEAR, MONTH, DAY, float(start_hour), DURATION, float(top_height), 10, float(scale)]

    def suzuki_args_dt(dt_obj, top_height, scale):
        hour_decimal = dt_obj.hour + dt_obj.minute / 60.0
        return [staggerred_h, dt_obj.year, dt_obj.month, dt_obj.day, hour_decimal, DURATION, float(top_height), 10, float(scale)]

    def zero_args_dt(dt_obj):
        hour_decimal = dt_obj.hour + dt_obj.minute / 60.0
        return [staggerred_h, dt_obj.year, dt_obj.month, dt_obj.day, hour_decimal, DURATION]

    #Ash Emissions
    ash_profiles = [(VerticalProfile_Suzuki, suzuki_args(hour, height, scale)) for hour, height, scale in zip(profile_hours, profile_tops, profile_scales)]
    ash_profiles.append((VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, END_HOUR, DURATION]))

    #Define the ash scenario
    #ash_e = Emission_Ash(mass_mt=0.90, lat=LAT, lon=LON)
    ash_e = Emission_Ash(mass_mt=0.90, lat=LAT, lon=LON, bin_n=10, mean_r=2.4, stddev=1.8)
    #bin10 is the smallest ash particles
    #bin1 is the largest ash particles
                                     #bin10,  bin9,    bin8,   bin7,  bin6,   bin5,   bin4,   bin3,   bin2,    bin1
    #ash_e.setMassFractions(np.array([0.0025, 0.0050, 0.0100, 0.0150, 0.0300, 0.2025, 0.3625, 0.1875, 0.1200, 0.0650]))
    ash_scenario = EmissionScenario(ash_e)
    #Add the ash profiles to the ash scenario
    for p, args in ash_profiles:
        ash_scenario.add_profile(p(*args))

    #SO2 Emissions
    so2_start_dt = datetime(YEAR, MONTH, DAY, 8, 30)
    so2_final_zero_dt = datetime(YEAR, MONTH, DAY + 1, 1, 0)  # 01:00 UTC on 24 Nov
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
    block1_active_steps = max(1, int(np.ceil(block1_steps / 2.0)))
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
    block1_scales = np.linspace(1.48, 0.1, len(block1_times))       #to get 0.3 Mt during first 2 hours
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
    #Define the SO2 scenario
    so2_scenario = EmissionScenario(Emission_SO2(mass_mt=1.0,lat=LAT, lon=LON))
    #Add the SO2 profiles to the so2 scenario
    for p, args in so2_profiles:
        so2_scenario.add_profile(p(*args))

    #so2_scenario.plot()

    # mass emitted in first 2 hours
    print(so2_scenario.get_emitted_mass_within(2))
    # or using timedelta/datetime
    #mt_90m = so2_scenario.get_emitted_mass_within(timedelta(minutes=90))
    #mt_until = so2_scenario.get_emitted_mass_within(datetime(2025, 11, 23, 10, 30))

    #exit()
    #Passing all scenarios to the EmissionWriter
    emission_writer = EmissionWriter_UniformInTimeProfiles([so2_scenario,ash_scenario], netcdf_handler, output_interval_m=PROFILE_INTERVAL_MIN)
    emission_writer.write()

    #Plotting the scenarios
    emission_writer.plot_scenarios()
    #OR plot separately
    #ash_scenario.plot(linestyle='-', color='brown')
    #so2_scenario.plot(linestyle='-', color='blue')
    #sulfate_scenario.plot(linestyle='-', color='red')
    #watervapor_scenario.plot(linestyle='-', color='blue',marker="+")
