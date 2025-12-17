from src import *
import numpy as np

# Example 6:
# Emisson profiles of ash and SO2 for the Hayli Gubbi volcano eruption in 2025
# provided wrfinput file.

if __name__ == "__main__":
    # Location of the Hayli Gubbi volcano
    LAT, LON = 13.51, 40.722
    YEAR, MONTH, DAY = 2025, 11, 23
    #DURATION = 14*3600     # seconds
    
    netcdf_handler = WRFNetCDFWriter(source_dir="./")
    y,x = netcdf_handler.findClosestGridCell(LAT,LON)
    staggerred_h=netcdf_handler.getColumn_H(x,y)

    ash_e = Emission_Ash(mass_mt=1.0, lat=LAT, lon=LON, bin_n=10, mean_r=2.4, stddev=1.8)
                                    #bin10,  bin9, bin8,   bin7,  bin6, bin5,   bin4, bin3,  bin2,   bin1
    ash_e.setMassFractions(np.array([0.017, 0.158, 0.422, 0.326, 0.072, 0.005, 0.000, 0.000, 0.000, 0.000]))
    so2_e = Emission_SO2(mass_mt=0.3,lat=LAT, lon=LON)
    emission_scenarios = [ 
        # Ash emissions
        EmissionScenario_HayliGubbi(ash_e,"./scenarios/Hayli Gubbi_Ukhov_2025/ash_emissions.txt"),
        # SO2 emissions
        EmissionScenario_HayliGubbi(so2_e,"./scenarios/Hayli Gubbi_Ukhov_2025/so2_emisisons.txt")
        ]
            
    emission_writer = EmissionWriter_NonUniformInHeightProfiles(emission_scenarios, netcdf_handler, output_interval_m=30)
    
    #emission_writer.plot_scenarios()
    
    #cleaning the scenarios by removing emissions below certain heights and times
    emission_scenarios[0].set_values_by_criteria(0, height_min_m=0, height_max_m=5000)
    emission_scenarios[1].set_values_by_criteria(0, height_min_m=0, height_max_m=7500)
    emission_scenarios[1].set_values_by_criteria(0, time_start='2025-11-24T08:00')#, time_end='2025-11-24T12:00') 

    # Print brief summary to verify changes
    #for i, scen in enumerate(emission_scenarios):
    #    print(f"Scenario {i}: {scen.getNumberOfProfiles()} profiles, emitted mass (before normalization): {scen.getScenarioEmittedMass():.6f} Mt")
    
    
    emission_writer.plot_scenarios()
    #exit()

    # Plot the scenarios
    #scenarios[0].plot()
    #scenarios[1].plot()
    #scenarios[2].plot()
    #scenarios[0].plot(linestyle='--', color='grey', marker='')

    
    emission_writer.write()

    #for p in scenarios[0].profiles:
    #        p.plot()
    #        print (f"Mass {sum(p.values):.2f}")

    # SO2 mass emitted in first 2 hours
    print(emission_scenarios[1].get_emitted_mass_within(2))
    
    emission_writer.plot_scenarios()
    
    emission_scenarios[0].save_fig("ash_hayli_gubbi_ash_suzuki_approximation.png", dpi=300)
    emission_scenarios[1].save_fig("so2_hayli_gubbi_so2_suzuki_approximation.png", dpi=300)

    # Plot the scenarios
    #scenarios[0].plot()
    #scenarios[1].plot()
    #scenarios[2].plot()