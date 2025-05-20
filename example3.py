from src import *
import numpy as np

# Example 3: 
# Different type profiles with the same DURATION = 7200 seconds
# This example is similar to example1.py. These emissions were used in the
# simulation with periodic boundary conditions to check the mass ballance.
# See the corresponding paper for the reference.

if __name__ == "__main__":
    # Location of the Pinatubo volcano
    LAT, LON = 15.1429, 120.3496
    YEAR, MONTH, DAY = 1991, 6, 15
    DURATION = 7200    #seconds

    # find the location of the volcano using the information from the wrfinput file
    netcdf_handler = WRFNetCDFWriter(source_dir="./")
    j, i = netcdf_handler.findClosestGridCell(lat=LAT, lon=LON)
    #get the height of the 'mass' points in the wrfinput file
    staggerred_h = netcdf_handler.getColumn_H(i, j)

    #Ash Emissions    
    ash_profiles = [
        (VerticalProfile_Umbrella, [staggerred_h, YEAR, MONTH, DAY, 2, DURATION, 15000, 1000, 0.95]),
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 4, DURATION]),
    ]
    
    #Define the ash scenario
    ash_e=Emission_Ash(mass_mt=65.0, lat=LAT, lon=LON)
    #define ash mass fractions. 0.1 for all bins in this case
    ash_e.setMassFractions(np.full(10, 0.1))
    ash_scenario = EmissionScenario(ash_e)
    #Add the ash profiles to the ash scenario
    for p, args in ash_profiles:
        ash_scenario.add_profile(p(*args))

    #SO2 Emissions
    so2_profiles = [
        (VerticalProfile_Umbrella, [staggerred_h, YEAR, MONTH, DAY, 2, DURATION, 15000, 1000, 0.95]),
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 4, DURATION]),
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
    ]
    #Define the sulfate scenario
    sulfate_scenario = EmissionScenario(Emission_Sulfate(mass_mt=5.0,lat=LAT, lon=LON))
    #Add the sulfate profiles to the sulfate scenario
    for p, args in sulfate_profiles:
        sulfate_scenario.add_profile(p(*args))

    #Water vapor Emissions
    watervapor_profiles = [
        (VerticalProfile_Umbrella, [staggerred_h, YEAR, MONTH, DAY, 2, DURATION, 25000, 1000, 0.95]),
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 4, DURATION]),
    ]
    #Define the water vapor scenario
    watervapor_scenario = EmissionScenario(Emission_WaterVapor(mass_mt=50.0,lat=LAT, lon=LON))
    #Add the water vapor profiles to the water vapor scenario
    for p, args in watervapor_profiles:
        watervapor_scenario.add_profile(p(*args))

    #Passing all scenarios to the EmissionWriter. Interval between profiles is 120 minutes.
    emission_writer = EmissionWriter_UniformInTimeProfiles([ash_scenario,so2_scenario,sulfate_scenario,watervapor_scenario], \
                                                           netcdf_handler, 120)
    emission_writer.write()

    #Plotting the scenarios
    emission_writer.plot_scenarios()
    #OR plot separately
    #ash_scenario.plot(linestyle='-', color='brown')
    #so2_scenario.plot(linestyle='-', color='blue')
    #sulfate_scenario.plot(linestyle='-', color='red')
    #watervapor_scenario.plot(linestyle='-', color='blue',marker="+")