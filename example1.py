from src import *
import numpy as np

# Example 1: 
# Combination of different type of profiles with the same DURATION = 7200 seconds
# Emissions of ash, SO2, sulfate, and water vapor (Emission_Ash, Emission_SO2, Emission_Sulfate, 
# and Emission_WaterVapor classes).
# This example shows how to create a scenario with different types of profiles
# and how to write them to a netCDF file. Plotting the emissions using the plot method of the 
# EmissionScenario class. Classes VerticalProfile_Umbrella, VerticalProfile_Zero, 
# and VerticalProfile_Uniform classes to create the profiles for the emissions.
# Pay attention to the fact that the last profile for each scenario is a
# 'VerticalProfile_Zero' profile. This is done to avoid emissions
# after the eruption has ended.

if __name__ == "__main__":
    # Prescribe the location of the volcano, start date, and profile's duration in seconds
    LAT, LON = 15.1429, 120.3496
    YEAR, MONTH, DAY = 1991, 6, 15
    DURATION = 7200     # seconds

    # find the location of the volcano using the information from the wrfinput file
    netcdf_handler = WRFNetCDFWriter(source_dir="./")
    j, i = netcdf_handler.findClosestGridCell(lat=LAT, lon=LON)
    #get the height of the 'mass' points in the wrfinput file
    staggerred_h = netcdf_handler.getColumn_H(i, j)
  
    #Ash Emissions
    ash_profiles = [
        (VerticalProfile_Umbrella, [staggerred_h, YEAR, MONTH, DAY, 2, DURATION, 15000, 1000, 0.55,1]),
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 4, DURATION]),
        (VerticalProfile_Suzuki, [staggerred_h, YEAR, MONTH, DAY, 6, DURATION, 25000, 4]),
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 8, DURATION]),
        (VerticalProfile_Uniform, [staggerred_h, YEAR, MONTH, DAY, 10, DURATION, 5000.0, 10000.0, 0.1]),
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 12, DURATION])
    ]

    #Define the ash scenario
    ash_e = Emission_Ash(mass_mt=65.0, lat=LAT, lon=LON)
    #define ash mass fractions. 0.1 for all bins in this case
    ash_e.setMassFractions(np.full(10, 0.1))
    ash_scenario = EmissionScenario(ash_e)    
    #Add the ash profiles to the ash scenario
    for p, args in ash_profiles:
        ash_scenario.add_profile(p(*args))

    #SO2 Emissions 
    so2_profiles = [
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 2, DURATION]),
        (VerticalProfile_Umbrella, [staggerred_h, YEAR, MONTH, DAY, 4, DURATION, 25000, 1000, 0.95]),
        (VerticalProfile_Suzuki, [staggerred_h, YEAR, MONTH, DAY, 6, DURATION, 15000, 6]),
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 8, DURATION]),
        (VerticalProfile_Umbrella, [staggerred_h, YEAR, MONTH, DAY, 10, DURATION, 10000, 1000, 0.55]),
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 12, DURATION])
    ]
    #Define the SO2 scenario
    so2_scenario = EmissionScenario(Emission_SO2(mass_mt=15.0,lat=LAT, lon=LON))
    #Add the SO2 profiles to the so2 scenario
    for p, args in so2_profiles:
        so2_scenario.add_profile(p(*args))

    #Sulfate Emissions
    sulfate_profiles = [
        (VerticalProfile_Umbrella, [staggerred_h, YEAR, MONTH, DAY, 2, DURATION, 10000, 1000, 0.95]),
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 4, DURATION]),
        (VerticalProfile_Suzuki, [staggerred_h, YEAR, MONTH, DAY, 6, DURATION, 10000, 8]),
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 8, DURATION]),
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 10, DURATION]),
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 12, DURATION])
    ]
    #Define the sulfate scenario
    sulfate_scenario = EmissionScenario(Emission_Sulfate(mass_mt=5.0,lat=LAT, lon=LON))    
    #Add the sulfate profiles to the sulfate scenario
    for p, args in sulfate_profiles:
        sulfate_scenario.add_profile(p(*args))

    #Water vapor Emissions
    watervapor_profiles = [
        (VerticalProfile_Umbrella, [staggerred_h, YEAR, MONTH, DAY, 2, DURATION, 25000, 1000, 0.95,2]),
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 4, DURATION]),
        (VerticalProfile_Suzuki, [staggerred_h, YEAR, MONTH, DAY, 6, DURATION, 20000, 12]),
        (VerticalProfile_Umbrella, [staggerred_h, YEAR, MONTH, DAY, 8, DURATION, 25000, 1000, 0.95,1]),
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 10, DURATION]),
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 12, DURATION]),
    ]
    #Define the water vapor scenario
    watervapor_scenario = EmissionScenario(Emission_WaterVapor(mass_mt=50.0,lat=LAT, lon=LON))
    #Add the water vapor profiles to the water vapor scenario
    for p, args in watervapor_profiles:
        watervapor_scenario.add_profile(p(*args))

    #Passing all scenarios to the EmissionWriter
    emission_writer = EmissionWriter_UniformInTimeProfiles([ash_scenario,so2_scenario,sulfate_scenario,watervapor_scenario], \
                                                           netcdf_handler, DURATION/60)
    emission_writer.write()

    #Plotting the scenarios
    emission_writer.plot_scenarios()
    #OR plot separately
    #ash_scenario.plot(linestyle='-', color='brown')
    #so2_scenario.plot(linestyle='-', color='blue')
    #sulfate_scenario.plot(linestyle='-', color='red')
    #watervapor_scenario.plot(linestyle='-', color='blue',marker="+")