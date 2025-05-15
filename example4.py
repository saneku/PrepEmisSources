from src import *
import numpy as np

# Example 4:
# Emisson profiles of SO2 are obtained by inversion of the satellite data
# from the eruption of the Eyjafjallajökull volcano, Iceland. (Brodtkorb et al. 2024).
# The profiles are given in the JSON format at 3 hour intervals.

if __name__ == "__main__":
    # Prescribe the location of the volcano
    LAT, LON = 15.1429, 120.3496
    
    scenarios = [
                EmissionScenario_Inverted_Eyjafjallajokull(Emission_SO2(mass_mt=15.54,lat=LAT, lon=LON),
                    './example_profiles/Eyjafjallajökull_Brodtkorb_2024/inversion_000_1.00000000_a_posteriori_reference.json'),
                ]
    
    netcdf_handler = WRFNetCDFWriter(source_dir="./")

    # Plot the scenarios
    scenarios[0].plot()
    #scenarios[0].plot(linestyle='--', color='grey', marker='')

    # Profiles are interpolated into the required vertical grid
    # and divided by the height of the grid cell to convert from Mt to Mt/m
    # The profiles are normalized by the total mass.
    emission_writer = EmissionWriter_NonUniformInTimeProfiles(scenarios, netcdf_handler, 10)
    emission_writer.write()

    #for p in scenarios[0].profiles:
    #        p.plot()
    #        print (f"Mass {sum(p.values):.2f}")

    scenarios[0].plot()