from core.netcdf_handler import WRFNetCDFHandler
from emissions.emissions import Emission_Ash, Emission_SO2, Emission_Sulfate, Emission_WaterVapor
from core.emission_scenario import EmissionScenario

class EmissionWriter:
    def __init__(self, scenarios, netcdf_handler,output_interval=60):
        
        self.__output_interval = output_interval  #minutes
        self.__only_once=False
        
        for i,scenario in enumerate(scenarios):
            if not isinstance(scenario, EmissionScenario):
                raise TypeError(f"{i} scenario must be an instance of EmissionScenario")
        
        self.__scenarios = scenarios

        if isinstance(netcdf_handler, WRFNetCDFHandler):
            self.__netcdf_handler = netcdf_handler
        else:
            raise TypeError("netcdf_handler must be an instance of NetCDFHandler")
        
    def write_to_file(self):
        for scenario in self.__scenarios:           
            scenario.interpolate_time(self.__output_interval) # minutes time intervals to interpolate to
            
            if not self.__only_once:
                self.__netcdf_handler.prepare_file(scenario.getStartDateTime().replace(minute=0, second=0, microsecond=0))
                self.__only_once=True

            y,x,dist = self.__netcdf_handler.findClosestGridCell(scenario.type_of_emission.lat,
                                                                  scenario.type_of_emission.lon)

            #divide by dh to convert from Mt to Mt/m
            scenario.divide_by_dh(self.__netcdf_handler.getColumn_dH(x,y))
            scenario.interpolate_height(self.__netcdf_handler.getColumn_H(x,y))
            #scenario.plot(linestyle='-', color='blue', marker='+')

            scenario.normalize_by_total_mass()
            
            erup_dt = scenario.getDuration()    #whole duration of eruption in seconds
            surface = self.__netcdf_handler.getColumn_Area(x,y)     #cell area in m2
            
            self.__netcdf_handler.write_times(scenario.get_profiles_StartDateTime())
            start_time,duration = scenario.get_profiles_Decimal_StartTimeAndDuration() # for example, s=165002, d=10 (minutes)
            self.__netcdf_handler.write_to_cell("ERUP_BEG",start_time,x,y)
            self.__netcdf_handler.write_to_cell("ERUP_END",duration,x,y)
            
            #compute column depending on the type of material
            
            # look at the create_volc_emission.py in Misc folder
            #self.__netcdf_handler.write_column(self,"var_name",column_values,time_index,x,y)
            print(f"DONE writing to netcdf file {scenario}")
            
        print ("--------------------------")
        print ("Set the following parameters in namelist.input: ")
        print (f"auxinput13_interval_m = {self.__output_interval}")
        print (f"auxinput13_time_intervals = {scenario.getNumberOfProfiles()}")
        print (f"auxinput13_file_name = {self.__netcdf_handler.dst_file}")
        print ("--------------------------")