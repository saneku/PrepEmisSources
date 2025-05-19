from src import *
import numpy as np

# Example 4:
# Emisson profiles of SO2 are obtained by inversion of the satellite data
# from the eruption of the Eyjafjallajökull volcano, Iceland. (Brodtkorb et al. 2024).
# The profiles are given in the JSON format at 3 hour intervals.

if __name__ == "__main__":
    #Location of the Eyjafjallajökull volcano
    LAT, LON = 63.6314, 19.6083
    
    scenarios = [
                # No information on the total ash emission and ash size distribution,
                # therefore Pinatubo values on ash size distribution are used.
                # Internet says that the eruption of the Eyjafjallajökull volcano
                # produced 40.0 Mt of ash. So, will use this value.
                EmissionScenario_Inverted_Eyjafjallajokull(Emission_Ash(mass_mt=40.0,lat=LAT, lon=LON,bin_n=10,mean_r=2.4,stddev=1.8),
                    './scenarios/Eyjafjallajökull_Brodtkorb_2024/inversion_000_1.00000000_a_posteriori_reference.json'),
                ]
    
    netcdf_handler = WRFNetCDFWriter(source_dir="./")

    # Plot the scenarios
    scenarios[0].plot()
    #scenarios[0].plot(linestyle='--', color='grey', marker='')

    # Profiles are interpolated into the required vertical grid
    # and divided by the height of the grid cell to convert from Mt to Mt/m
    # The profiles are normalized by the total mass.
    # output interval is 3 hours (3*60)=180 minutes
    emission_writer = EmissionWriter_NonUniformInHeightProfiles(scenarios, netcdf_handler, 3*60)
    emission_writer.write()

    #for p in scenarios[0].profiles:
    #        p.plot()
    #        print (f"Mass {sum(p.values):.2f}")

    scenarios[0].plot()