from emissions.emissions import Emission_Ash, Emission_SO2, Emission_Sulfate, Emission_WaterVapor
from core.netcdf_handler import WRFNetCDFHandler
from core.emission_scenario import EmissionScenario_InvertedPinatubo
from core.emission_writer import EmissionWriter

import numpy as np

if __name__ == "__main__":
    
    scenarios = [
                EmissionScenario_InvertedPinatubo(Emission_Ash(mass_mt=65,lat=15.1429,lon=120.3496,mean=2.4,stddev=1.8),
                                                    './example_profiles/Pinatubo_Ukhov_2023/ash_2d_emission_profiles'),

                EmissionScenario_InvertedPinatubo(Emission_SO2(mass_mt=15,lat=15.1429,lon=120.3496),
                                                     './example_profiles/Pinatubo_Ukhov_2023/so2_2d_emission_profiles')
                #Emission_Sulfate(mass_mt=0.1,lat=15,lon=165),
                #Emission_WaterVapor(mass_mt=150,lat=15,lon=165)
                ]
    #scenarios[0].plot(linestyle='--', color='grey', marker='')

    netcdf_handler = WRFNetCDFHandler(source_dir="./")
    #print(netcdf_handler)
    
    emission_writer = EmissionWriter(scenarios, netcdf_handler, 10)
    emission_writer.write_to_file()