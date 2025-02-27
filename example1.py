from core import *
from emissions import *
from profiles import *


#example 1
#Different type profiles with the same duration

if __name__ == "__main__":
    
    ash_scenario = EmissionScenario_MixOfProfiles(\
                 Emission_Ash(mass_mt=66.53,lat=15.1429,lon=120.3496,mean=2.4,stddev=1.8))
    
    netcdf_handler = WRFNetCDFWriter(source_dir="./")
    j,i = netcdf_handler.findClosestGridCell(lat=15.1429,lon=120.3496)
    
    staggerred_h = netcdf_handler.getColumn_H(i,j)
    
    ash_scenario.add_profile(VerticalProfile_Umbrella(staggerred_h,1991,6,15,3,7200,15000,1000,0.55))    
    ash_scenario.add_profile(VerticalProfile_Zero(staggerred_h,1991,6,15,5,7200))
    ash_scenario.add_profile(VerticalProfile_Umbrella(staggerred_h,1991,6,15,7,7200,25000,1000,0.95))
    ash_scenario.add_profile(VerticalProfile_Zero(staggerred_h,1991,6,15,9,7200))
    ash_scenario.add_profile(VerticalProfile_Uniform(staggerred_h,1991,6,15,11,7200,1.0,5000.0,10000.0))
    ash_scenario.add_profile(VerticalProfile_Zero(staggerred_h,1991,6,15,13,7200))  #should be the last one

    #todo: add last profile with zero values independent of the user

    #ash_scenario.plot()

    emission_writer = EmissionWriter_UniformInTimeProfiles([ash_scenario], netcdf_handler, 120)
    emission_writer.write()
    
    netcdf_handler.plot_how_much_was_written()