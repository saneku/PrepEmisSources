from abc import ABC, abstractmethod
from functools import wraps
from src import *

import numpy as np

class EmissionWriter():
    def __init__(self, scenarios, netcdf_handler,output_interval_m=60):
        
        self._output_interval = output_interval_m  #minutes        
        
        for i,scenario in enumerate(scenarios):
            if not isinstance(scenario, EmissionScenario):
                raise TypeError(f"{i} scenario must be an instance of EmissionScenario")
        self.__scenarios = scenarios

        if not isinstance(netcdf_handler, WRFNetCDFWriter):
            raise TypeError("netcdf_handler must be an instance of WRFNetCDFWriter")

        self._netcdf_handler = netcdf_handler

    def _check_vertical_compat(self, scenario, column_heights):
        """Raise a clear error if any profile exceeds the model vertical domain top.
        Interpolation with out-of-bounds heights would silently zero values; fail-fast here.
        """
        try:
            src_top = max(float(p.h.max()) for p in scenario.profiles)
        except ValueError:
            # no profiles
            return
        dom_top = float(np.max(column_heights)) if len(column_heights) > 0 else 0.0
        if src_top > dom_top+1:     # allow 1 m tolerance
            mat = scenario.type_of_emission.get_name_of_material()
            lat = scenario.type_of_emission.lat
            lon = scenario.type_of_emission.lon
            raise ValueError(
                (
                    f"{scenario.__class__.__name__}: profile top {src_top:.1f} m exceeds model domain top {dom_top:.1f} m "
                    f"at lat={lat:.4f}, lon={lon:.4f} for material '{mat}'. "
                    f"Increase WRF vertical extent or reduce the emission profile height."
                )
            )
    
    def _getScenarios(self):
        return self.__scenarios

    def plot_scenarios(self):
        for scenario in self._getScenarios():
            scenario.plot()
            #scenario.plot_profiles()#linestyle='-', color='blue')

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
            print (f"&time_control")
            print (f"\tauxinput13_interval_m = {self._output_interval}")
            print (f"\tframes_per_auxinput13 = {self._getScenarios()[0].getNumberOfProfiles()}")
            print (f"\tauxinput13_inname     = '{self._netcdf_handler.dst_file}'")
            print("&chem")
            print ("\tchem_opt               = 402")
            print ("\temiss_opt_vol          = 3")
            print ("--------------------------")
            
            history_string = " "
            for scenario in self._getScenarios():
                history_string+=str(scenario)+". \n"
            
            self._netcdf_handler.update_file_history(history_string)
            
            #Plotting the amount of mass written to the netCDF file
            #for debugging purposes
            self._netcdf_handler.check_how_much_has_been_written()
            
        return wrapper
    
    @abstractmethod    
    def write(self):
        raise NotImplementedError("Abstract method 'write' must be implemented in subclass of EmissionWriter")


# interpolate profiles in time (to uniform time intervals) 
# and height using the wrfinput vertical grid.
# NO NEED to divide by dh as the emission scenario given in [Mt/sec]
class EmissionWriter_NonUniformInTimeHeightProfiles(EmissionWriter):

    @EmissionWriter._postAmbula
    def write(self):
        for scenario in self._getScenarios():
            scenario.interpolate_time(self._output_interval) # minutes time intervals to interpolate to
            y,x = self._netcdf_handler.findClosestGridCell(scenario.type_of_emission.lat,scenario.type_of_emission.lon)

            col_h = self._netcdf_handler.getColumn_H(x,y)
            self._check_vertical_compat(scenario, col_h)
            scenario.interpolate_height(col_h)
            #divide by dh to convert from [Mt/sec] to [Mt/m/sec]
            #scenario.divide_by_dh(self._netcdf_handler.getColumn_dH(x,y))

            #scenario.plot(linestyle='-', color='blue', marker='+')
            
            self._netcdf_handler.write_material(scenario,x,y)


# interpolate only profiles height using the wrfinput vertical grid.
# no divide by dh as the profiles are already in Mt/m/s
class EmissionWriter_NonUniformInHeightProfiles(EmissionWriter):

    @EmissionWriter._postAmbula
    def write(self):
        for scenario in self._getScenarios():
            y,x = self._netcdf_handler.findClosestGridCell(scenario.type_of_emission.lat,scenario.type_of_emission.lon)

            col_h = self._netcdf_handler.getColumn_H(x,y)
            self._check_vertical_compat(scenario, col_h)
            scenario.interpolate_height(col_h)

            #scenario.plot(linestyle='-', color='blue', marker='+')
            
            self._netcdf_handler.write_material(scenario,x,y)

# no interpolation of the profiles in time and height
class EmissionWriter_UniformInTimeProfiles(EmissionWriter):

    @EmissionWriter._postAmbula
    def write(self):
        for scenario in self._getScenarios():
            y,x = self._netcdf_handler.findClosestGridCell(scenario.type_of_emission.lat,scenario.type_of_emission.lon)

            #scenario.plot(linestyle='-', color='red', marker='o')

            self._netcdf_handler.write_material(scenario,x,y)
