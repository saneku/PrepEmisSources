from abc import ABC, abstractmethod
from functools import wraps
from core import *
from emissions import *

import numpy as np

class EmissionWriter():
    def __init__(self, scenarios, netcdf_handler,output_interval=60):
        
        self._output_interval = output_interval  #minutes
        self._only_once=False
        
        for i,scenario in enumerate(scenarios):
            if not isinstance(scenario, EmissionScenario):
                raise TypeError(f"{i} scenario must be an instance of EmissionScenario")
        self.__scenarios = scenarios

        if not isinstance(netcdf_handler, WRFNetCDFWriter):
            raise TypeError("netcdf_handler must be an instance of WRFNetCDFWriter")

        self._netcdf_handler = netcdf_handler
    
    def _getScenarios(self):
        return self.__scenarios

    @staticmethod
    def _postAmbula(func):
        """Decorator that runs after the method execution."""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            print ("\n\n--------------------------")
            print (f"{self._netcdf_handler.dst_file} has been created.")
            #for scenario in self._getScenarios():    
            #    print (f"\t{scenario.type_of_emission.get_name_of_material():}: {scenario.getScenarioEmittedMass():.3f} Mt")

            print ("--------------------------")
            print ("Set the following parameters in the namelist.input: ")
            print (f"auxinput13_interval_m = {self._output_interval}")
            #print (f"frames_per_auxinput13 = {scenario.getNumberOfProfiles()}")
            print (f"frames_per_auxinput13 = {self._getScenarios()[0].getNumberOfProfiles()}")
            print (f"auxinput13_inname = '{self._netcdf_handler.dst_file}'")
            print ("--------------------------")
            #print(f"Method {func.__name__} executed")  # Post-execution behavior
            #return result
        return wrapper
    
    @abstractmethod    
    def write(self):
        raise NotImplementedError("Abstract method 'write' must be implemented in subclass of EmissionWriter")


class EmissionWriter_NonUniformInTimeProfiles(EmissionWriter):

    @EmissionWriter._postAmbula
    def write(self):
        for scenario in self._getScenarios():
            scenario.interpolate_time(self._output_interval) # minutes time intervals to interpolate to
            y,x = self._netcdf_handler.findClosestGridCell(scenario.type_of_emission.lat,scenario.type_of_emission.lon)

            if not self._only_once:
                self._netcdf_handler.prepare_file(scenario.getStartDateTime())#.replace(minute=0, second=0, microsecond=0))

                self._netcdf_handler.write_times(scenario.get_profiles_StartDateTime())
                start_time,duration = scenario.get_profiles_Decimal_StartTimeAndDuration() # for example, s=165002, d=10 (minutes)
                
                self._netcdf_handler.write_to_cell("E_START",start_time,0,x,y)
                #self.__netcdf_handler.write_to_cell("E_DURM",duration,0,x,y)

                self._only_once=True

            #divide by dh to convert from Mt to Mt/m
            scenario.interpolate_height(self._netcdf_handler.getColumn_H(x,y))
            scenario.divide_by_dh(self._netcdf_handler.getColumn_dH(x,y))

            #scenario.plot(linestyle='-', color='blue', marker='+')
            scenario.normalize_by_total_mass()
            
            self._netcdf_handler.write_material(scenario,x,y)


class EmissionWriter_UniformInTimeProfiles(EmissionWriter):

    @EmissionWriter._postAmbula
    def write(self):
        for scenario in self._getScenarios():
            y,x = self._netcdf_handler.findClosestGridCell(scenario.type_of_emission.lat,scenario.type_of_emission.lon)

            if not self._only_once:
                self._netcdf_handler.prepare_file(scenario.getStartDateTime())
                self._netcdf_handler.write_times(scenario.get_profiles_StartDateTime())
                start_time,duration = scenario.get_profiles_Decimal_StartTimeAndDuration()
                self._netcdf_handler.write_to_cell("E_START",start_time,0,x,y)
                self._only_once=True

            #scenario.plot(linestyle='-', color='blue', marker='+')
            scenario.normalize_by_total_mass()

            self._netcdf_handler.write_material(scenario,x,y)