from core import *
from emissions import *
from profiles import *
import numpy as np

# Example 1: Different type profiles with the same DURATION = 7200 seconds

if __name__ == "__main__":
    LAT, LON = 15.1429, 120.3496
    YEAR, MONTH, DAY = 1991, 6, 15
    DURATION = 7200    #seconds

    #Ash
    e=Emission_Ash(mass_mt=65.0, lat=LAT, lon=LON)
    e.setMassFractions(np.full(10, 0.1))
    ash_scenario = EmissionScenario_MixOfProfiles(e)

    netcdf_handler = WRFNetCDFWriter(source_dir="./")
    j, i = netcdf_handler.findClosestGridCell(lat=LAT, lon=LON)
    staggerred_h = netcdf_handler.getColumn_H(i, j)

    ash_profiles = [
        (VerticalProfile_Umbrella, [staggerred_h, YEAR, MONTH, DAY, 2, DURATION, 15000, 1000, 0.95]),
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 4, DURATION]),
    ]
    for p, args in ash_profiles:
        ash_scenario.add_profile(p(*args))

    #SO2 Emissions
    so2_scenario = EmissionScenario_MixOfProfiles(Emission_SO2(mass_mt=15.0,lat=LAT, lon=LON))
    so2_profiles = [
        (VerticalProfile_Umbrella, [staggerred_h, YEAR, MONTH, DAY, 2, DURATION, 15000, 1000, 0.95]),
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 4, DURATION]),
    ]
    
    for p, args in so2_profiles:
        so2_scenario.add_profile(p(*args))

    #Sulfate Emissions
    sulfate_scenario = EmissionScenario_MixOfProfiles(Emission_Sulfate(mass_mt=5.0,lat=LAT, lon=LON))
    sulfate_profiles = [
        (VerticalProfile_Umbrella, [staggerred_h, YEAR, MONTH, DAY, 2, DURATION, 10000, 1000, 0.95]),
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 4, DURATION]),
    ]
    for p, args in sulfate_profiles:
        sulfate_scenario.add_profile(p(*args))

    #Water vapor Emissions
    watervapor_scenario = EmissionScenario_MixOfProfiles(Emission_WaterVapor(mass_mt=50.0,lat=LAT, lon=LON))
    watervapor_profiles = [
        (VerticalProfile_Umbrella, [staggerred_h, YEAR, MONTH, DAY, 2, DURATION, 25000, 1000, 0.95]),
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 4, DURATION]),
    ]
    for p, args in watervapor_profiles:
        watervapor_scenario.add_profile(p(*args))

    #Adding all scenarios
    emission_writer = EmissionWriter_UniformInTimeProfiles([ash_scenario,so2_scenario,sulfate_scenario,watervapor_scenario], \
                                                           netcdf_handler, DURATION/60)
    emission_writer.write()


    ash_scenario.plot()
    so2_scenario.plot()
    sulfate_scenario.plot()
    watervapor_scenario.plot()    

    netcdf_handler.plot_how_much_was_written()
    
    
    #todo: add factors for profiles, so that they can be scaled up or down
    
    #plot correctly profiles
    
    #io_form_auxinput13                  = 2,  add