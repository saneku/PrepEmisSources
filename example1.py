from core import *
from emissions import *
from profiles import *

# Example 1: Different type profiles with the same duration DURATION = 7200 seconds

if __name__ == "__main__":
    LAT, LON = 15.1429, 120.3496
    YEAR, MONTH, DAY = 1991, 6, 15
    DURATION = 7200

    ash_scenario = EmissionScenario_MixOfProfiles(
        Emission_Ash(mass_mt=66.53, lat=LAT, lon=LON, bin_n=10, mean_r=2.4, stddev=1.8)
    )

    netcdf_handler = WRFNetCDFWriter(source_dir="./")
    j, i = netcdf_handler.findClosestGridCell(lat=LAT, lon=LON)
    staggerred_h = netcdf_handler.getColumn_H(i, j)

    profiles = [
        (VerticalProfile_Umbrella, [staggerred_h, YEAR, MONTH, DAY, 3, DURATION, 15000, 1000, 0.55]),
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 5, DURATION]),
        (VerticalProfile_Umbrella, [staggerred_h, YEAR, MONTH, DAY, 7, DURATION, 25000, 1000, 0.95]),
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 9, DURATION]),
        (VerticalProfile_Uniform, [staggerred_h, YEAR, MONTH, DAY, 11, DURATION, 1.0, 5000.0, 10000.0]),
        (VerticalProfile_Zero, [staggerred_h, YEAR, MONTH, DAY, 13, DURATION])
    ]

    for p, args in profiles:
        ash_scenario.add_profile(p(*args))

    emission_writer = EmissionWriter_UniformInTimeProfiles([ash_scenario], netcdf_handler, DURATION/60)
    emission_writer.write()

    netcdf_handler.plot_how_much_was_written()