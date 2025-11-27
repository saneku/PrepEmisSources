from src import *
import numpy as np

# Example 5:
#explosive eruption at Hayli Gubbi was detected in satellite data at around 0830 UTC on 23 November 2025
#The eruption produced an ash plume that reached an altitude of approximately 14 km 
#and drifted eastward over the Red Sea. The eruption was also accompanied by a significant SO2 plume.
#https://volcano.si.edu/volcano.cfm?vn=221091

# Ash and SO₂ for Hayli Gubbi (13.51 N, 40.722 E) are emitted from 
# 08:30 to 15:30 UTC on 23 Nov 2025 via thirty‑minute snapshots.
# Each snapshot uses VerticalProfile_Suzuki with its top height linearly descending 
# from 14 km to 7 km and a scale factor that tapers from 1.0 at the start to 0.1 by the end,
# so both the plume altitude and intensity weaken steadily over the 7‑hour eruption window.
# Ash carries 0.90 Mt total mass with explicit bin fractions 
# (largest particles first), while SO₂ totals 0.22 Mt; both scenarios terminate with a 
# VerticalProfile_Zero at 15:30 UTC to stop emissions cleanly.

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
        return [staggerred_h, YEAR, MONTH, DAY, float(start_hour), DURATION, float(top_height), 4, float(scale)]

    #Ash Emissions
    ash_profiles = [(VerticalProfile_Suzuki, suzuki_args(hour, height, scale)) for hour, height, scale in zip(profile_hours, profile_tops, profile_scales)]
    ash_profiles.append((VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, END_HOUR, DURATION]))

    #Define the ash scenario
    ash_e = Emission_Ash(mass_mt=0.90, lat=LAT, lon=LON)
    #bin10 is the smallest ash particles
    #bin1 is the largest ash particles
                                     #bin10,  bin9,    bin8,   bin7,  bin6,   bin5,   bin4,   bin3,   bin2,    bin1
    ash_e.setMassFractions(np.array([0.0025, 0.0050, 0.0100, 0.0150, 0.0300, 0.2025, 0.3625, 0.1875, 0.1200, 0.0650]))
    ash_scenario = EmissionScenario(ash_e)    
    #Add the ash profiles to the ash scenario
    for p, args in ash_profiles:
        ash_scenario.add_profile(p(*args))

    #SO2 Emissions 
    so2_profiles = [(VerticalProfile_Suzuki, suzuki_args(hour, height, scale)) for hour, height, scale in zip(profile_hours, profile_tops, profile_scales)]
    so2_profiles.append((VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, END_HOUR, DURATION]))
    #Define the SO2 scenario
    so2_scenario = EmissionScenario(Emission_SO2(mass_mt=0.220,lat=LAT, lon=LON))
    #Add the SO2 profiles to the so2 scenario
    for p, args in so2_profiles:
        so2_scenario.add_profile(p(*args))

    #Passing all scenarios to the EmissionWriter
    emission_writer = EmissionWriter_UniformInTimeProfiles([ash_scenario,so2_scenario], netcdf_handler, output_interval_m=PROFILE_INTERVAL_MIN)
    emission_writer.write()

    #Plotting the scenarios
    emission_writer.plot_scenarios()
    #OR plot separately
    #ash_scenario.plot(linestyle='-', color='brown')
    #so2_scenario.plot(linestyle='-', color='blue')
    #sulfate_scenario.plot(linestyle='-', color='red')
    #watervapor_scenario.plot(linestyle='-', color='blue',marker="+")
