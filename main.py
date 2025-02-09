from emissions.base import Emission_Ash, Emission_SO2, Emission_Sulfate, Emission_WaterVapor
from profiles.types import VerticalProfile_Uniform, VerticalProfile_Suzuki, VerticalProfile_Simple
#from core.eruption import Eruption, InvertedPinatuboEruption
from core.netcdf_handler import NetCDFHandler
from core.writer import EmissionWriter
import numpy as np
from core.emission_scenario import EmissionScenario_InvertedPinatubo

import datetime

if __name__ == "__main__":
    
    '''
    scenario = EmissionScenario_InvertedPinatubo('./example_profiles/ash_2d_emission_profiles')
    #scenario.plot(linestyle='--', color='grey', marker='')
    #print ("BEFORE")
    scenario.adjust_time() # interpoloate to new time points
    #print ("AFTER")
    #scenario.plot(linestyle='-', color='red', marker='+')
    #print(scenario)

    h=np.array([ 273.9505, 407.21893, 574.90356, 788.33356, 1050.1624, 1419.9668, 1885.3608, 2372.2937, 2883.3193, 3634.4663, 4613.3403, 5594.8545, 6580.381, 7568.5386, 8558.1455, 9547.174, 10534.043, 11518.861, 12501.9375, 13484.473, 14454.277, 15393.3125, 16300.045, 17189.598, 18083.797, 18998.496, 19939.57, 20905.723, 21890.363, 22886.46, 23890.441, 24900.914, 25918.307, 26943.252, 27977.344, 29021.828, 30077.21, 31143.973, 32221.8, 33310.13, 34408.86, 35517.9, 36637.133, 37766.45])
    random_values = np.random.randint(-100, 101, size=h.shape)
    h += random_values
    h = h[::8]
        
    scenario.adjust_height(h)
    scenario.plot(linestyle='-', color='blue', marker='+')
    exit()
    '''
    
    emissions = [
                Emission_Ash(mass_mt=65,lat=15,lon=165,mean=2.4,stddev=1.8),
                Emission_SO2(mass_mt=15,lat=15,lon=165),
                Emission_Sulfate(mass_mt=0.1,lat=15,lon=165),
                Emission_WaterVapor(mass_mt=150,lat=15,lon=165)
                ]
    exit()

    netcdf_handler = NetCDFHandler(source_dir="./")
    print(netcdf_handler)
    #def prepare_file(self,start_time,interval_days,interval_hours,interval_mins):
    netcdf_handler.prepare_file(start_time,end_time,interval_days=0,interval_hours=0,interval_mins=60)
    exit()
    
    
    emission_writer = EmissionWriter(emissions, netcdf_handler)

    eruption = Eruption()
    for emission in emissions:
        eruption.add_emission(emission)

    eruption.add_profile(UniformProfile())
    eruption.add_profile(VerticalProfile_Suzuki())
    eruption.add_profile(VerticalProfile_Simple())

    emission_writer.write_emissions_to_netcdf()
