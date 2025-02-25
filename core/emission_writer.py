from abc import ABC, abstractmethod
from functools import wraps
from core import *
from emissions import *

import numpy as np

class EmissionWriter():
    def __init__(self, scenarios, netcdf_handler,output_interval=60):
        
        self.__output_interval = output_interval  #minutes
        self._only_once=False
        
        for i,scenario in enumerate(scenarios):
            if not isinstance(scenario, EmissionScenario):
                raise TypeError(f"{i} scenario must be an instance of EmissionScenario")
        self.__scenarios = scenarios

        if not isinstance(netcdf_handler, WRFNetCDFWriter):
            raise TypeError("netcdf_handler must be an instance of NetCDFHandler")

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
            print (f"{self._netcdf_handler.dst_file} has been created. Added")
            for scenario in self._getScenarios():    
                print (f"\t{scenario.type_of_emission.get_name_of_material():}: {scenario.getScenarioEmittedMass()} Mt")

            print ("--------------------------")
            print ("Set the following parameters in the namelist.input: ")
            print (f"auxinput13_interval_m = {self.__output_interval}")
            #print (f"frames_per_auxinput13 = {scenario.getNumberOfProfiles()}")
            print (f"frames_per_auxinput13 = {self._getScenarios()[0].getNumberOfProfiles(  )}")
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
            scenario.interpolate_time(self.__output_interval) # minutes time intervals to interpolate to
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
            
            #compute column depending on the type of material
            #to get emission per m2. division by cell area is "inside" write_column(). 
            material_name = scenario.type_of_emission.get_name_of_material()
            self._netcdf_handler.write_material(material_name,scenario.profiles,x,y)
            
            '''
            if material_name == "ash":
                
                #Rescaled GOCART fractions [0.001 0.015 0.095 0.45  0.439] into ash bins:
                #Ash1...6=0 Ash7=0.212 Ash8=0.506 Ash9=0.251 Ash10=0.0312
                
                #"ug/m2/s"
                ash_mass_factors = np.array([0, 0, 0, 0, 0, 0, 0.212, 0.506, 0.251, 0.031])
                if not np.isclose(sum(ash_mass_factors), 1.0):
                    raise ValueError(f"sum(ash_mass_factors)={sum(ash_mass_factors)} Should be =1.0")
                
                for i in range(1,11):
                    self.__netcdf_handler.write_column("E_VASH"+str(i),1e18 * ash_mass_factors[i-1], scenario.profiles,x,y)
                
            elif material_name == "so2":
                #"ug/m2/min"
                self.__netcdf_handler.write_column("E_VSO2",60 * 1e18, scenario.profiles,x,y)
            elif material_name == "sulfate":
                #"ug/m2/min"
                self.__netcdf_handler.write_column("E_VSULF",60 * 1e18, scenario.profiles,x,y)
            elif material_name == "watervapor":
                #"kg/m2/sec"
                self.__netcdf_handler.write_column("E_QV",1e9, scenario.profiles,x,y)
            else:
                raise ValueError(f"Unknown material: {material_name}")
            '''
        #self._postAmbula()



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
            
            material_name = scenario.type_of_emission.get_name_of_material()
            self._netcdf_handler.write_material(material_name,scenario.profiles,x,y)