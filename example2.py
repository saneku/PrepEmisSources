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
    DURATION = 14*3600     # seconds
    
    netcdf_handler = WRFNetCDFWriter(source_dir="./")
    y,x = netcdf_handler.findClosestGridCell(LAT,LON)
    staggerred_h=netcdf_handler.getColumn_H(x,y)

    #Water vapor Emissions
    watervapor_profiles = [(VerticalProfile_Umbrella, [staggerred_h, YEAR, MONTH, DAY, 1.666, DURATION, 17000, 1000, 0.75,1])]
    #Define the water vapor scenario
    watervapor_scenario = EmissionScenario(Emission_WaterVapor(mass_mt=100.0,lat=LAT, lon=LON))
    #Add the water vapor profile to the water vapor scenario
    for p, args in watervapor_profiles:
        watervapor_scenario.add_profile(p(*args))

    scenarios_with_disabled_rad_feedback = [
                EmissionScenario_Inverted_Pinatubo(Emission_Ash(mass_mt=62.67,lat=LAT, lon=LON,bin_n=10,mean_r=2.4,stddev=1.8),
                                                    './scenarios/Pinatubo_Ukhov_2023/ash_2d_emission_profiles_rad_off'),

                EmissionScenario_Inverted_Pinatubo(Emission_SO2(mass_mt=16.73,lat=LAT, lon=LON),
                                                     './scenarios/Pinatubo_Ukhov_2023/so2_2d_emission_profiles_rad_off'),
                watervapor_scenario
                #EmissionScenario_Inverted_Pinatubo(Emission_WaterVapor(mass_mt=100.0,lat=LAT, lon=LON),
                #                                     './scenarios/Pinatubo_Ukhov_2023/so2_2d_emission_profiles_rad_off')
                #Emission_Sulfate(mass_mt=0.1,lat=15,lon=165),
                ]
    
    scenarios_with_enabled_rad_feedback = [
                EmissionScenario_Inverted_Pinatubo(Emission_Ash(mass_mt=66.53,lat=LAT, lon=LON,bin_n=10,mean_r=2.4,stddev=1.8),
                                                    './scenarios/Pinatubo_Ukhov_2023/ash_2d_emission_profiles_rad_on'),

                EmissionScenario_Inverted_Pinatubo(Emission_SO2(mass_mt=15.54,lat=LAT, lon=LON),
                                                     './scenarios/Pinatubo_Ukhov_2023/so2_2d_emission_profiles_rad_on'),
                
                watervapor_scenario
                #EmissionScenario_Inverted_Pinatubo(Emission_WaterVapor(mass_mt=0.01,lat=LAT, lon=LON),
                #                                     './scenarios/Pinatubo_Ukhov_2023/so2_2d_emission_profiles_rad_on')
                #Emission_Sulfate(mass_mt=0.1,lat=15,lon=165),
                ]
    
    emission_writer = EmissionWriter_NonUniformInTimeHeightProfiles(scenarios_with_enabled_rad_feedback, netcdf_handler, output_interval_m=10)
    
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