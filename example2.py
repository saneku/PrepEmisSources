from src import *
import numpy as np

# Example 2:
# Emisson profiles of ash and SO2 are obtained by inversion (Ukhov et al. 2023). 
# Water vapor emission is set to 100 Mt, with the same profile as SO2.
# Inverted profiles are interpolated to 60 minute intervals.

if __name__ == "__main__":
    # Location of the Pinatubo volcano
    LAT, LON = 15.1429, 120.3496
    
    scenarios = [
                EmissionScenario_Inverted_Pinatubo(Emission_Ash(mass_mt=66.53,lat=LAT, lon=LON,bin_n=10,mean_r=2.4,stddev=1.8),
                                                    './scenarios/Pinatubo_Ukhov_2023/ash_2d_emission_profiles'),

                EmissionScenario_Inverted_Pinatubo(Emission_SO2(mass_mt=15.54,lat=LAT, lon=LON),
                                                     './scenarios/Pinatubo_Ukhov_2023/so2_2d_emission_profiles'),
                
                EmissionScenario_Inverted_Pinatubo(Emission_WaterVapor(mass_mt=100.0,lat=LAT, lon=LON),
                                                     './scenarios/Pinatubo_Ukhov_2023/so2_2d_emission_profiles')
                #Emission_Sulfate(mass_mt=0.1,lat=15,lon=165),
                ]
    
    netcdf_handler = WRFNetCDFWriter(source_dir="./")

    # Profiles are interpolated into the required vertical grid
    # and divided by the height of the grid cell to convert from Mt to Mt/m
    # The profiles are normalized by the total mass. Interval between profiles is 60 minutes.
    emission_writer = EmissionWriter_NonUniformInTimeHeightProfiles(scenarios, netcdf_handler, 60)
    
    emission_writer.plot_scenarios()
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