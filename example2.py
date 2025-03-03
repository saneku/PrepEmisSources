from emissions import *
from core import *
import numpy as np

#example 2
#Non uniform in time emisson profiles of ash and SO2 are taken from the Ukhov et al. (2023).

if __name__ == "__main__":
    LAT, LON = 15.1429, 120.3496
    
    scenarios = [
                EmissionScenario_InvertedPinatubo(Emission_Ash(mass_mt=66.53,lat=LAT, lon=LON,bin_n=10,mean_r=2.4,stddev=1.8),
                                                    './example_profiles/Pinatubo_Ukhov_2023/ash_2d_emission_profiles'),

                EmissionScenario_InvertedPinatubo(Emission_SO2(mass_mt=15.54,lat=LAT, lon=LON),
                                                     './example_profiles/Pinatubo_Ukhov_2023/so2_2d_emission_profiles')
                #Emission_Sulfate(mass_mt=0.1,lat=15,lon=165),
                #Emission_WaterVapor(mass_mt=150,lat=15,lon=165)
                ]
    #scenarios[0].plot(linestyle='--', color='grey', marker='')
    netcdf_handler = WRFNetCDFWriter(source_dir="./")

    scenarios[0].plot()
    scenarios[1].plot()

    emission_writer = EmissionWriter_NonUniformInTimeProfiles(scenarios, netcdf_handler, 10)
    emission_writer.write()

    #for p in scenarios[0].profiles:
    #        p.plot()
    #        print (f"Mass {sum(p.values):.2f}")


    scenarios[0].plot()
    scenarios[1].plot()

    
    netcdf_handler.plot_how_much_was_written()


#todo: add info on eruption time, duration, etc. to the netcdf file
#todo: add second constructor for ash fractions.
#todo: add suzuki profile