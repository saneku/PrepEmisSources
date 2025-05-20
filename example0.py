from src import *
import numpy as np

# Example 0: 
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
  
    p=VerticalProfile_Suzuki(staggerred_h, YEAR, MONTH, DAY, 6, DURATION, 25000, 10)
    p.plot()#linestyle='-', color='blue', marker='+')
    p=VerticalProfile_Umbrella(staggerred_h, YEAR, MONTH, DAY, 2, DURATION, 25000, 1000, 0.85,1)
    p.plot()
    p=VerticalProfile_Zero(staggerred_h, YEAR, MONTH, DAY, 4, DURATION)
    p.plot()
    p=VerticalProfile_Uniform(staggerred_h, YEAR, MONTH, DAY, 10, DURATION, 5000.0, 20000.0, 0.2)
    p.plot()
    #print(p)
