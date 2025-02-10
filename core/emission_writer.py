from core.netcdf_handler import NetCDFHandler
from emissions.base import Emission_Ash, Emission_SO2, Emission_Sulfate, Emission_WaterVapor

class EmissionWriter:
    def __init__(self, scenarios, netcdf_handler,output_interval=60):
        
        self.__output_interval = output_interval  #minutes
        self.__only_once=False
        
        for scenario in scenarios:
            if not isinstance(scenario, EmissionScenario):
                raise TypeError("Scenario must be an instance of EmissionScenario")
        
        self.__scenarios = scenarios

        if isinstance(netcdf_handler, NetCDFHandler):
            self.__netcdf_handler = netcdf_handler
        else:
            raise TypeError("netcdf_handler must be an instance of NetCDFHandler")
        
    def write_to_file(self):
        for scenario in self.__scenarios:           
            scenario.adjust_time() # interpoloate to new time points with 1 (<-todo) hour interval
            
            if not self.__only_once:
                netcdf_handler.prepare_file(scenario.getStartDateTime(),scenario.getEndDateTime(),
                            interval_days=0,interval_hours=0,interval_mins=self.__output_interval)  #todo: add arbitaty time intervals
                self.__only_once=True
            else:
                raise Exception("Only first scenario can create the netcdf file")
    
            ii,jj,dist0=self.__netcdf_handler.findClosestGridCell(scenario.type_of_emission.lat,
                                                                  scenario.type_of_emission.lon)
        
            # interpolate to new height levels at (ii,jj) location
            scenario.adjust_height(self.__netcdf_handler.h[:,jj,ii])             
            #scenario.plot(linestyle='-', color='blue', marker='+')
            
            #divide by dh
            #calculate total emission
            #normalize by scenario.type_of_emission.mass_Mt
            #write to netcdf file