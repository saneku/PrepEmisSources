import netCDF4 as nc
import numpy as np
import os
import xarray as xr
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

class WRFNetCDFWriter:
    def __init__(self, source_dir='./', wrf_input_file='./wrfinput_d01'):
        self.source_dir = source_dir
        self.orgn_wrf_input_file = wrf_input_file
        
        self.__only_once = False
        
        self.__emissions = {
                "ash": {"var": "E_VASH", "mass_factor": 1e18, "time_factor": 1, "color": 'grey'},
                "so2": {"var": "E_VSO2", "mass_factor": 1e18, "time_factor": 60, "color": 'blue'},
                "sulfate": {"var": "E_VSULF", "mass_factor": 1e18, "time_factor": 60, "color": 'red'},
                "watervapor": {"var": "E_QV", "mass_factor": 1e9, "time_factor": 1, "color": 'lightblue'}}
        
        #Read data from wrfinput data
        print (f'Open {self.source_dir}{self.orgn_wrf_input_file}')
        with nc.Dataset(f'{self.source_dir}{self.orgn_wrf_input_file}','r') as wrfinput:
            self.xlon=wrfinput.variables['XLONG'][0,:]
            self.xlat=wrfinput.variables['XLAT'][0,:]
            MAPFAC_MX=wrfinput.variables['MAPFAC_MX'][0,:]
            MAPFAC_MY=wrfinput.variables['MAPFAC_MY'][0,:]

            dy = wrfinput.getncattr('DY')
            dx = wrfinput.getncattr('DX')
            self.area = (dx/MAPFAC_MX)*(dy/MAPFAC_MY)       #m2
            self.__h = (wrfinput.variables['PH'][0,:] + wrfinput.variables['PHB'][0,:]) / 9.81
            self.__dh = np.diff(self.__h,axis=0)                #dh in m

            self.__h = self.__h[:-1]
            self.__h = self.__h + self.__dh * 0.5               #height in m
            
            #self.h and self.dh are 3d variable with dimensions (bottom_top, south_north, west_east)

    def __str__(self):
        return f"WRFNetCDFWriter(source_file='{self.source_dir}{self.orgn_wrf_input_file}', destination_file='{self.source_dir}{self.dst_file}', dimensions={self.__h.shape})"

    def prepare_file(self,suffix):
        self.dst_file = f'wrfchemv_d01.{suffix.strftime("%Y-%m-%d_%H:%M:%S")}'
        #copy wrfinput to wrfchemv
        if os.path.exists(f'{self.source_dir}{self.dst_file}'):
            os.system(f'rm {self.source_dir}{self.dst_file}')

        ds = xr.open_dataset(f'{self.source_dir}{self.orgn_wrf_input_file}')
        ds_var = ds[['T','Times']]
        
        #remove all attributes except the most important
        for atr in ds.attrs:
            if atr not in ["TITLE","START_DATE", "SIMULATION_START_DATE", "WEST-EAST_GRID_DIMENSION", "SOUTH-NORTH_GRID_DIMENSION", \
                       "BOTTOM-TOP_GRID_DIMENSION", "DX", "DY", "WEST-EAST_PATCH_START_UNSTAG", "WEST-EAST_PATCH_END_UNSTAG", \
                        "WEST-EAST_PATCH_START_STAG", "WEST-EAST_PATCH_END_STAG", "SOUTH-NORTH_PATCH_START_UNSTAG", \
                        "SOUTH-NORTH_PATCH_END_UNSTAG", "SOUTH-NORTH_PATCH_START_STAG", "SOUTH-NORTH_PATCH_END_STAG", \
                        "BOTTOM-TOP_PATCH_START_UNSTAG", "BOTTOM-TOP_PATCH_END_UNSTAG", "BOTTOM-TOP_PATCH_START_STAG", \
                        "BOTTOM-TOP_PATCH_END_STAG", "GRID_ID", "PARENT_ID", "I_PARENT_START", "J_PARENT_START", "CEN_LAT", \
                        "CEN_LON", "TRUELAT1", "TRUELAT2", "MOAD_CEN_LAT", "STAND_LON", "POLE_LAT", "POLE_LON", "JULYR", \
                        "JULDAY", "MAP_PROJ", "MAP_PROJ_CHAR"]:
                del ds_var.attrs[atr]
        
        ds_var.attrs["HISTORY"] = f"OUTPUT FROM PrepEmisSources on {datetime.datetime.utcnow()} UTC. "
        ds_var.to_netcdf(f'{self.source_dir}{self.dst_file}')
        #===========================================
        
        #add variables to wrfchemv file
        with nc.Dataset(f'{self.source_dir}{self.dst_file}','r+') as nc_file:
            self.__add4dVar(nc_file,"E_START","START TIME OF ERUPTION","?")
            self.__add4dVar(nc_file,"E_VSO2","Volcanic Emissions, SO2","mol/m2/h")
            self.__add4dVar(nc_file,"E_VSULF","Volcanic Emissions, SULF","mol/m2/h")
            self.__add4dVar(nc_file,"E_QV","Volcanic Emissions, QV","kg/m2/s")

            self.__add2dVar(nc_file,"AREA","cell area","m^2")
            nc_file.variables['AREA'][:]=self.area

            for i in range(1,11):
                self.__add4dVar(nc_file,"E_VASH"+str(i),"Volcanic Emissions, bin"+str(i),"ug/m2/s")

    def update_file_history(self, history_string):
        with nc.Dataset(f'{self.source_dir}{self.dst_file}', 'r+') as nc_file:
            if "HISTORY" in nc_file.ncattrs():
                nc_file.setncattr("HISTORY", nc_file.getncattr("HISTORY") + history_string)
            else:
                nc_file.setncattr("HISTORY", history_string)


    def __add4dVar(self,wrf_file,var_name,caption,units):
        wrf_file.createVariable(var_name, 'f4', ('Time','bottom_top','south_north', 'west_east'))
        wrf_file.variables[var_name].FieldType=104
        wrf_file.variables[var_name].MemoryOrder="XYZ"
        wrf_file.variables[var_name].description=caption
        wrf_file.variables[var_name].units=units
        wrf_file.variables[var_name].stagger = "" ;
        wrf_file.variables[var_name].coordinates = "XLONG XLAT XTIME"

        #zero field
        wrf_file.variables[var_name][:] = 0.0
        print (f"Adding {var_name} {caption} {units} into {wrf_file}")

    def __add3dVar(self, wrf_file, var_name, caption, units):
        wrf_file.createVariable(var_name, 'f4', ('Time','south_north', 'west_east'))
        wrf_file.variables[var_name].FieldType=104
        wrf_file.variables[var_name].MemoryOrder="XY"
        wrf_file.variables[var_name].description=caption
        wrf_file.variables[var_name].units=units
        wrf_file.variables[var_name].stagger = "" ;
        wrf_file.variables[var_name].coordinates = "XLONG XLAT"

        #zero field
        wrf_file.variables[var_name][:] = 0.0
        print (f"Adding {var_name} {caption} {units} into {wrf_file}")
        
    def __add2dVar(self, wrf_file, var_name, caption, units):
        wrf_file.createVariable(var_name, 'f4', ('south_north', 'west_east'))
        wrf_file.variables[var_name].FieldType=104
        wrf_file.variables[var_name].MemoryOrder="XY"
        wrf_file.variables[var_name].description=caption
        wrf_file.variables[var_name].units=units
        wrf_file.variables[var_name].stagger = "" ;
        wrf_file.variables[var_name].coordinates = "XLONG XLAT"

        #zero field
        wrf_file.variables[var_name][:] = 0.0
        print (f"Adding {var_name} {caption} {units} into {wrf_file}")

    def findClosestGridCell(self, lat, lon):
        nrow = len(self.xlat)
        ncol = len(self.xlon[0])
        dist0 = 1000.0
        ii = 0
        jj = 0
        for i in range(nrow):
            for j in range(ncol):
                dist = np.sqrt((self.xlon[i, j] - lon) ** 2 + (self.xlat[i, j] - lat) ** 2)
                if dist < dist0:
                    dist0 = dist
                    jj = j
                    ii = i
        if ii == 0 and jj == 0:
            raise ValueError("The closest grid cell is at the boundary (0,0).")
        return ii, jj

    #heights of the 'mass' points
    def getColumn_H(self, x, y):
        return np.array(self.__h[:,y,x])
    
    #heights of the grid cells
    def getColumn_dH(self, x, y):
        return np.array(self.__dh[:,y,x])
    
    def __write_column(self,var_name,factor,profiles,x,y):
        factor = factor/np.array(self.area[y,x])
        with nc.Dataset(f'{self.source_dir}{self.dst_file}','r+') as wrf_volc_file:
            for time_index,profile in enumerate(profiles):
                wrf_volc_file.variables[var_name][time_index,:,y,x] = factor * profile.values

    def write_to_cell(self,var_name,value,z,x,y):
        with nc.Dataset(f'{self.source_dir}{self.dst_file}','r+') as wrf_volc_file:
            wrf_volc_file.variables[var_name][:,z,y,x] = value
            
    #start_time,end_time,interval_days,interval_hours,interval_mins):
    def write_times(self,start_times):
        with nc.Dataset(f'{self.source_dir}{self.dst_file}','r+') as wrf_volc_file:
            #time_range = pd.date_range(start=start_time, end=end_time, 
            #                freq=pd.Timedelta(days=interval_days, hours=interval_hours, minutes=interval_mins))

            #time_range = time_range[:-1]    #crop the last
            aux_times = np.chararray((len(start_times), 19), itemsize=1)

            for i, aux_date in enumerate(start_times):
                #aux_date = start_time + datetime.timedelta(days=interval_days,hours=interval_hours,minutes=interval_mins)
                aux_times[i] = list(aux_date.strftime("%Y-%m-%d_%H:%M:%S"))
            wrf_volc_file.variables['Times'][:] = aux_times                                
            
            # Loop through all variables and create a new times
            for var_name in wrf_volc_file.variables:
                if var_name == 'Times':
                    continue
                var = wrf_volc_file.variables[var_name]
                if 'Time' in var.dimensions:
                    #print(var)
                    for i,_ in enumerate(aux_times):
                        var[i,:]=var[0,:]

    def __do_only_once(self, scenario, x, y):
        if not self.__only_once:
            self.prepare_file(scenario.getStartDateTime())
            self.write_times(scenario.get_profiles_StartDateTime())
            start_time,duration = scenario.get_profiles_Decimal_StartTimeAndDuration() # for example, s=165002, d=10 (minutes)
            self.write_to_cell("E_START",start_time,0,x,y)
            self.__only_once = True


    def write_material(self, scenario, x, y):                       
            #Rescaled from GOCART fractions [0.001 0.015 0.095 0.45  0.439] into ash bins:
                                             #0.001 0.012 0.071 0.336 0.443
            #Ash1...6=0 Ash7=0.212 Ash8=0.506 Ash9=0.251 Ash10=0.0312
            #ash_mass_factors = np.array([0, 0, 0, 0, 0, 0, 0.212, 0.506, 0.251, 0.031])
            
            #computed from parameters of the lognormal distribution
            #mu = np.log(2*2.4)  # 2.4 median radii!!!
            #sigma = np.log(1.8)
            #ash_mass_factors = np.array([0, 0, 0, 0, 0.004, 0.073, 0.326, 0.422, 0.158, 0.017])
            
            #make sure that the last profile is a zero profile
            if scenario.profiles[-1].getProfileEmittedMass()!=0.0:
                print(f"Last profile in {str(scenario)[0:40]}... has non-zero emissions. Please add VerticalProfile_Zero profile")
                exit(1)
            
            scenario.normalize_by_total_mass()
            
            self.__do_only_once(scenario, x, y)
            
            material_name = scenario.type_of_emission.get_name_of_material()
            if material_name not in self.__emissions:
                raise ValueError(f"Unknown material: {material_name}")

            mtrl = self.__emissions[material_name]
            
            #so2,sulf emissions in "ug/m2/min"
            #water vapor emissions in "kg/m2/s"
            #ash emissions in "ug/m2/s"
            
            if material_name == "ash":
                ash_mass_factors = scenario.type_of_emission.ash_mass_factors[::-1]
                for i in range(1, 11):
                    self.__write_column(f"{mtrl['var']}{i}",mtrl['time_factor'] * mtrl['mass_factor'] * ash_mass_factors[i-1], scenario.profiles, x, y)
            else:
                self.__write_column(f"{mtrl['var']}", mtrl['time_factor'] * mtrl['mass_factor'], scenario.profiles, x, y)

    def check_how_much_has_been_written(self):
        with nc.Dataset(f'{self.source_dir}{self.dst_file}','r') as wrf_volc_file:
            times = [datetime.datetime.strptime(str(b''.join(t)), "b'%Y-%m-%d_%H:%M:%S'") for t in wrf_volc_file.variables['Times'][:]]
            duration_sec = list(np.diff(times).astype('timedelta64[s]').astype(int))
            duration_sec.append(duration_sec[-1]) #add the last one, assuming all delta's are the same
            
            total = {key: [] for key in self.__emissions}
            
            for time_idx, curr_time in enumerate(times):
                #print(time_idx, curr_time)
                for key, data in self.__emissions.items():
                    if key == "ash":
                        total_emission = np.sum(np.sum(wrf_volc_file.variables[f"{data['var']}{i}"][time_idx, :] * self.area) for i in range(1, 11))
                    else:
                        total_emission = np.sum(wrf_volc_file.variables[data["var"]][time_idx, :] * self.area)
                    #for plotting
                    total[key].append(total_emission * duration_sec[time_idx] / data["time_factor"] / data["mass_factor"])

            times.append(times[-1] + datetime.timedelta(seconds=int(duration_sec[-1])))
        
        plt.title("Accumulated mass")
        print("Material Total mass")
        for key, data in total.items():
            plt.plot(times, [0]+list(np.cumsum(data)),color=self.__emissions[key]['color'], label=f"${key}$ {np.cumsum(data)[-1]:.2f} Mt",marker='o',markersize=2)
            print(f"{key}\t{np.cumsum(data)[-1]:.2f} Mt")
        print("--------------------------")
        plt.ylabel('Mass, $Mt$')
        plt.xlabel('Time, UTC')
        plt.legend(loc="best")
        plt.grid(True, alpha=0.3)
        plt.ylim([0, 80])
        plt.gca().get_xaxis().set_major_formatter(DateFormatter('%m-%d %H:%M'))
        plt.gca().get_xaxis().set_minor_locator(plt.MultipleLocator(1))
        plt.show()