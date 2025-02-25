from abc import ABC, abstractmethod
from functools import wraps
from core import *
from emissions import *

import numpy as np

class EmissionWriter():
    def __init__(self, scenarios, netcdf_handler,output_interval=60):
        
        self.__output_interval = output_interval  #minutes
        self.__only_once=False
        
        for i,scenario in enumerate(scenarios):
            if not isinstance(scenario, EmissionScenario):
                raise TypeError(f"{i} scenario must be an instance of EmissionScenario")
        self.__scenarios = scenarios

        if not isinstance(netcdf_handler, WRFNetCDFWriter):
            raise TypeError("netcdf_handler must be an instance of NetCDFHandler")

        self.__netcdf_handler = netcdf_handler
    
    def __getScenarios(self):
        return self.__scenarios
        #for s in self.__scenarios:
        #    yield s

    @staticmethod
    def _postAmbula(func):
        """Decorator that runs after the method execution."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)  # Execute the original method            
            print ("--------------------------")
            print (f"{self.__netcdf_handler.dst_file} has been created. Added")
            for scenario in self.__scenarios:    
                print (f"\t{scenario.type_of_emission.get_name_of_material():}: {scenario.getScenarioEmittedMass()} Mt")

            print ("--------------------------")
            print ("Set the following parameters in the namelist.input: ")
            print (f"auxinput13_interval_m = {self.__output_interval}")
            #print (f"frames_per_auxinput13 = {scenario.getNumberOfProfiles()}")
            print (f"frames_per_auxinput13 = {self.self.__scenarios[0].getNumberOfProfiles(  )}")
            print (f"auxinput13_inname = '{self.__netcdf_handler.dst_file}'")
            print ("--------------------------")
            #print(f"Method {func.__name__} executed")  # Post-execution behavior
            #return result
        return wrapper
    
    @abstractmethod    
    def write_to_file(self):
        pass

class EmissionWriter_NonUniformInTimeProfiles:
    #def __init__(self, scenarios, netcdf_handler,output_interval=60):

    @EmissionWriter._postAmbula
    def write_to_file(self):
        for scenario in self.__getScenarios():
            scenario.interpolate_time(self.__output_interval) # minutes time intervals to interpolate to
            y,x = self.__netcdf_handler.findClosestGridCell(scenario.type_of_emission.lat,scenario.type_of_emission.lon)

            if not self.__only_once:
                self.__netcdf_handler.prepare_file(scenario.getStartDateTime())#.replace(minute=0, second=0, microsecond=0))

                self.__netcdf_handler.write_times(scenario.get_profiles_StartDateTime())
                start_time,duration = scenario.get_profiles_Decimal_StartTimeAndDuration() # for example, s=165002, d=10 (minutes)
                
                self.__netcdf_handler.write_to_cell("E_START",start_time,0,x,y)
                #self.__netcdf_handler.write_to_cell("E_DURM",duration,0,x,y)

                self.__only_once=True

            #divide by dh to convert from Mt to Mt/m
            scenario.interpolate_height(self.__netcdf_handler.getColumn_H(x,y))
            scenario.divide_by_dh(self.__netcdf_handler.getColumn_dH(x,y))
            #scenario.plot(linestyle='-', color='blue', marker='+')

            scenario.normalize_by_total_mass()
            
            #erup_dt = scenario.getDuration()    #whole duration of eruption in seconds
            #area = self.__netcdf_handler.getColumn_Area(x,y)     #cell area in m2
            
            #compute column depending on the type of material
            #to get emission per m2. division by cell area is "inside" write_column(). 
            material_name = scenario.type_of_emission.get_name_of_material()
            if material_name == "ash":
                
                #Rescaled GOCART fractions [0.001 0.015 0.095 0.45  0.439] into ash bins:
                #Ash1...6=0 Ash7=0.212 Ash8=0.506 Ash9=0.251 Ash10=0.0312
                
                #"ug/m2/s"
                ash_mass_factors = np.array([0, 0, 0, 0, 0, 0, 0.212, 0.506, 0.251, 0.031])
                if not np.isclose(sum(ash_mass_factors), 1.0):
                    raise ValueError(f"sum(ash_mass_factors)={sum(ash_mass_factors)} Should be =1.0")
                
                for i in range(1,11):
                    self.__netcdf_handler.write_column("E_VASH"+str(i),1e18 * ash_mass_factors[i-1], scenario.profiles,x,y)
                
                '''
                ndust=5
                nbin_o=10
                dlo_sectm=np.array([1e-5,3.90625,7.8125,15.625,31.25,62.5,125,250,500,1000])
                dhi_sectm=np.array([3.90625,7.8125,15.625,31.25,62.5,125,250,500,1000,2000])
                dustfrc_goc10bin_ln=np.zeros((ndust,nbin_o))
                gocart_fractions = 0.01 * np.array([0.1, 1.5, 9.5, 45,43.9])
                ra_gocart=np.array([0.1,1.0,1.8,3.0,6.0])
                rb_gocart=np.array([1.0,1.8,3.0,6.0,10.0])
                for m in range(0,ndust):  # loop over dust size bins
                    dlogoc = ra_gocart[m]*2.0  # low diameter limit
                    dhigoc = rb_gocart[m]*2.0  # hi diameter limit

                    for n in range(0,4):
                        dustfrc_goc10bin_ln[m,n]=max(0.0,min(np.log(dhi_sectm[n]),np.log(dhigoc)) - max(np.log(dlogoc),np.log(dlo_sectm[n])))/(np.log(dhigoc)-np.log(dlogoc))

                #Flip dustfrc_goc10bin_ln because the smallest bin is Bin10, largset is Bin1
                dustfrc_goc10bin_ln = np.fliplr(dustfrc_goc10bin_ln)
                for m in range(0,ndust):
                    for n in range(0,nbin_o):
                        self.__netcdf_handler.write_column(f"E_VASH{n+1}",1e18 * (dustfrc_goc10bin_ln[m,n] * gocart_fractions[m]), scenario.profiles,x,y)                                        
                '''
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

        #self._postAmbula()



class EmissionWriter_UniformInTimeProfiles:
    #def __init__(self, scenarios, netcdf_handler,output_interval=60):

    @EmissionWriter._postAmbula
    def write_to_file(self):
        for scenario in self.__getScenarios():
            scenario.interpolate_time(self.__output_interval) # minutes time intervals to interpolate to
            y,x = self.__netcdf_handler.findClosestGridCell(scenario.type_of_emission.lat,scenario.type_of_emission.lon)

            if not self.__only_once:
                self.__netcdf_handler.prepare_file(scenario.getStartDateTime())#.replace(minute=0, second=0, microsecond=0))

                self.__netcdf_handler.write_times(scenario.get_profiles_StartDateTime())
                start_time,duration = scenario.get_profiles_Decimal_StartTimeAndDuration() # for example, s=165002, d=10 (minutes)
                
                self.__netcdf_handler.write_to_cell("E_START",start_time,0,x,y)
                #self.__netcdf_handler.write_to_cell("E_DURM",duration,0,x,y)

                self.__only_once=True

            #divide by dh to convert from Mt to Mt/m
            scenario.interpolate_height(self.__netcdf_handler.getColumn_H(x,y))
            scenario.divide_by_dh(self.__netcdf_handler.getColumn_dH(x,y))
            #scenario.plot(linestyle='-', color='blue', marker='+')

            scenario.normalize_by_total_mass()
            
            #erup_dt = scenario.getDuration()    #whole duration of eruption in seconds
            #area = self.__netcdf_handler.getColumn_Area(x,y)     #cell area in m2
            
            #compute column depending on the type of material
            #to get emission per m2. division by cell area is "inside" write_column(). 
            material_name = scenario.type_of_emission.get_name_of_material()
            if material_name == "ash":
                
                #Rescaled GOCART fractions [0.001 0.015 0.095 0.45  0.439] into ash bins:
                #Ash1...6=0 Ash7=0.212 Ash8=0.506 Ash9=0.251 Ash10=0.0312
                
                #"ug/m2/s"
                ash_mass_factors = np.array([0, 0, 0, 0, 0, 0, 0.212, 0.506, 0.251, 0.031])
                if not np.isclose(sum(ash_mass_factors), 1.0):
                    raise ValueError(f"sum(ash_mass_factors)={sum(ash_mass_factors)} Should be =1.0")
                
                for i in range(1,11):
                    self.__netcdf_handler.write_column("E_VASH"+str(i),1e18 * ash_mass_factors[i-1], scenario.profiles,x,y)
                
                '''
                ndust=5
                nbin_o=10
                dlo_sectm=np.array([1e-5,3.90625,7.8125,15.625,31.25,62.5,125,250,500,1000])
                dhi_sectm=np.array([3.90625,7.8125,15.625,31.25,62.5,125,250,500,1000,2000])
                dustfrc_goc10bin_ln=np.zeros((ndust,nbin_o))
                gocart_fractions = 0.01 * np.array([0.1, 1.5, 9.5, 45,43.9])
                ra_gocart=np.array([0.1,1.0,1.8,3.0,6.0])
                rb_gocart=np.array([1.0,1.8,3.0,6.0,10.0])
                for m in range(0,ndust):  # loop over dust size bins
                    dlogoc = ra_gocart[m]*2.0  # low diameter limit
                    dhigoc = rb_gocart[m]*2.0  # hi diameter limit

                    for n in range(0,4):
                        dustfrc_goc10bin_ln[m,n]=max(0.0,min(np.log(dhi_sectm[n]),np.log(dhigoc)) - max(np.log(dlogoc),np.log(dlo_sectm[n])))/(np.log(dhigoc)-np.log(dlogoc))

                #Flip dustfrc_goc10bin_ln because the smallest bin is Bin10, largset is Bin1
                dustfrc_goc10bin_ln = np.fliplr(dustfrc_goc10bin_ln)
                for m in range(0,ndust):
                    for n in range(0,nbin_o):
                        self.__netcdf_handler.write_column(f"E_VASH{n+1}",1e18 * (dustfrc_goc10bin_ln[m,n] * gocart_fractions[m]), scenario.profiles,x,y)                                        
                '''
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

        #self._postAmbula()
       