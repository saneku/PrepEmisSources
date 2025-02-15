from core.netcdf_handler import WRFNetCDFHandler
from emissions.emissions import Emission_Ash, Emission_SO2, Emission_Sulfate, Emission_WaterVapor
from core.emission_scenario import EmissionScenario
import numpy as np
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
            y,x,dist = self.__netcdf_handler.findClosestGridCell(scenario.type_of_emission.lat,scenario.type_of_emission.lon)

            if not self.__only_once:
                self.__netcdf_handler.prepare_file(scenario.getStartDateTime())#.replace(minute=0, second=0, microsecond=0))

                self.__netcdf_handler.write_times(scenario.get_profiles_StartDateTime())
                start_time,duration = scenario.get_profiles_Decimal_StartTimeAndDuration() # for example, s=165002, d=10 (minutes)
                
                self.__netcdf_handler.write_to_cell("E_START",start_time,0,x,y)
                #self.__netcdf_handler.write_to_cell("E_DURM",duration,0,x,y)

                self.__only_once=True

            #divide by dh to convert from Mt to Mt/m
            scenario.divide_by_dh(self.__netcdf_handler.getColumn_dH(x,y))
            scenario.interpolate_height(self.__netcdf_handler.getColumn_H(x,y))
            #scenario.plot(linestyle='-', color='blue', marker='+')

            scenario.normalize_by_total_mass()
            
            #erup_dt = scenario.getDuration()    #whole duration of eruption in seconds
            #area = self.__netcdf_handler.getColumn_Area(x,y)     #cell area in m2
            
            #compute column depending on the type of material
            #to get emission per m2. division by cell area is "inside" write_column(). 
            match scenario.type_of_emission.get_name_of_material():
                case "ash":
                    #"ug/m2/s"
                    ash_mass_factors=np.array([0,0,0,0,0,0,0.2,0.4,0.2,0.2])
                    #todo if (sum(ash_mass_factors)!=1.0) error !
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
                case "so2":
                    #"ug/m2/min"
                    self.__netcdf_handler.write_column("E_VSO2",60 * 1e18, scenario.profiles,x,y)
                case "sulfate":
                    #"ug/m2/min"
                    self.__netcdf_handler.write_column("E_VSULF",60 * 1e18, scenario.profiles,x,y)
                case "watervapor":
                    #"kg/m2/sec"
                    self.__netcdf_handler.write_column("E_QV",1e9, scenario.profiles,x,y)
                case _:
                    raise ValueError(f"Unknown material: {material_name}")

        print ("--------------------------")
        print (f"{self.__netcdf_handler.dst_file} has been created. Added")
        for scenario in self.__scenarios:    
            print (f"\t{scenario.type_of_emission.get_name_of_material():}: {scenario.getScenarioEmittedMass()} Mt")
        print ("--------------------------")
        print ("Set the following parameters in the namelist.input: ")
        print (f"auxinput13_interval_m = {self.__output_interval}")
        print (f"frames_per_auxinput13 = {scenario.getNumberOfProfiles()}")
        print (f"auxinput13_inname = '{self.__netcdf_handler.dst_file}'")
        print ("--------------------------")