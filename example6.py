from src import *
import numpy as np

# Example 2:
# Emisson profiles of ash and SO2 [Mt/sec] are obtained by inversion (Ukhov et al. 2023). 
# Emissions are for two scenarios: with and without radiative feedback.
# Note, masses of ash and SO2 are not the same in both scenarios.
# Water vapor emission is set to 100 Mt. Umbrella profile is used for water vapor emissions.
# Inverted profiles are interpolated to 10 minute intervals.
# Inverted ash and SO2 profiles [Mt/sec] are interpolated into the vertical grid from the 
# provided wrfinput file.

if __name__ == "__main__":
    # Location of the Pinatubo volcano
    LAT, LON = 15.1429, 120.3496
    YEAR, MONTH, DAY = 1991, 6, 15
    #DURATION = 14*3600     # seconds
    
    netcdf_handler = WRFNetCDFWriter(source_dir="./")
    y,x = netcdf_handler.findClosestGridCell(LAT,LON)
    staggerred_h=netcdf_handler.getColumn_H(x,y)

    ash_e = Emission_Ash(mass_mt=5.0, lat=LAT, lon=LON, bin_n=10, mean_r=2.4, stddev=1.8)
    so2_e = Emission_SO2(mass_mt=1.0,lat=LAT, lon=LON)
    emisison_scenarios = [ 
        # Ash emissions
        EmissionScenario_HayliGubbi(ash_e,"./scenarios/Hayli Gubbi_Ukhov_2025/ash_emissions.txt"),
        # SO2 emissions
        EmissionScenario_HayliGubbi(so2_e,"./scenarios/Hayli Gubbi_Ukhov_2025/so2_emisisons.txt")
        ]
            
    emission_writer = EmissionWriter_UniformInTimeProfiles(emisison_scenarios, netcdf_handler, output_interval_m=30)
    
    #emission_writer.plot_scenarios()
    
    #cleaning the scenarios by removing emissions below certain heights and times
    emisison_scenarios[0].set_values_by_criteria(0, height_min_m=0, height_max_m=5000)
    emisison_scenarios[1].set_values_by_criteria(0, height_min_m=0, height_max_m=7500)
    emisison_scenarios[1].set_values_by_criteria(0, time_start='2025-11-24T08:00')#, time_end='2025-11-24T12:00') 

    # Print brief summary to verify changes
    #for i, scen in enumerate(emisison_scenarios):
    #    print(f"Scenario {i}: {scen.getNumberOfProfiles()} profiles, emitted mass (before normalization): {scen.getScenarioEmittedMass():.6f} Mt")
    
    
    emission_writer.plot_scenarios()
    #exit()

    # Plot the scenarios
    #scenarios[0].plot()
    #scenarios[1].plot()
    #scenarios[2].plot()
    #scenarios[0].plot(linestyle='--', color='grey', marker='')

    
    emission_writer.write()

    #for p in scenarios[0].profiles:
    #        p.plot()
    #        print (f"Mass {sum(p.values):.2f}")

    emission_writer.plot_scenarios()
    # Plot the scenarios
    #scenarios[0].plot()
    #scenarios[1].plot()
    #scenarios[2].plot()