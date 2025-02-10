import netCDF4 as nc
import numpy as np
import os
import xarray as xr
import datetime
import pandas as pd

class NetCDFHandler:
    def __init__(self, source_dir):#, destination_file):
        self.source_dir = source_dir
        #self.destination_file = destination_file

        self.orgn_wrf_input_file="wrfinput_d01"
        self.dst_file="wrfchemv_d01"

    def __str__(self):
        return f"NetCDFHandler(source_file='{self.source_dir}{self.orgn_wrf_input_file}', destination_file='{self.source_dir}{self.dst_file}', dimensions={self.Z.shape})"

    def prepare_file(self,start_time,end_time,interval_days,interval_hours,interval_mins=60):
        with nc.Dataset(f'{self.source_dir}{self.dst_file}', 'a') as dataset:
            #days=range(0,366)
            time_range = pd.date_range(start=start_time, end=end_time, 
                           freq=pd.Timedelta(days=interval_days, hours=interval_hours, minutes=interval_mins))

            aux_times = np.chararray((len(time_range), 19), itemsize=1)
            
            for i, aux_date in enumerate(time_range):
                #aux_date = start_time + datetime.timedelta(days=interval_days,hours=interval_hours,minutes=interval_mins)
                aux_times[i] = list(aux_date.strftime("%Y-%m-%d_%H:%M:%S"))
            dataset.variables['Times'][:] = aux_times
            
            # Loop through all variables and create a new times
            for var_name in dataset.variables:
                if var_name == 'Times':
                    continue
                var = dataset.variables[var_name]
                if 'Time' in var.dimensions:
                    print(var)
                    for i,_ in enumerate(aux_times):
                        var[i,:]=var[0,:]
    

        #TODO: HERE!!!
        #Read wrfinput data
        print (f'Open {self.source_dir}{self.orgn_wrf_input_file}')
        with nc.Dataset(f'{self.source_dir}{self.orgn_wrf_input_file}','r') as wrfinput:
            self.xlon=wrfinput.variables['XLONG'][0,:]
            self.xlat=wrfinput.variables['XLAT'][0,:]
            MAPFAC_MX=wrfinput.variables['MAPFAC_MX'][0,:]
            MAPFAC_MY=wrfinput.variables['MAPFAC_MY'][0,:]

            dy = wrfinput.getncattr('DY')
            dx = wrfinput.getncattr('DX')
            self.surface = (dx/MAPFAC_MX)*(dy/MAPFAC_MY)       #surface in m2

            self.Z = (wrfinput.variables['PH'][0,:] + wrfinput.variables['PHB'][0,:]) / 9.81
            self.dz = np.diff(self.Z,axis=0)

            self.Z = self.Z[:-1]
            self.Z = self.Z + self.dz * 0.5
            self.Z = self.Z/1000.0

        #===========================================
        #copy wrfinput to wrfchemv
        if os.path.exists(f'{self.source_dir}{self.dst_file}'):
            os.system(f'rm {self.source_dir}{self.dst_file}')

        ds = xr.open_dataset(f'{self.source_dir}{self.orgn_wrf_input_file}')
        ds_var = ds[['PH','PHB','T','Times']]
        ds_var.to_netcdf(f'{self.source_dir}{self.dst_file}')
        #===========================================
        
        #add variables to wrfchemv
        with nc.Dataset(f'{self.source_dir}{self.dst_file}','r+') as wrf_volc_file:
            self.__add2dVar(wrf_volc_file,"ERUP_BEG","START TIME OF ERUPTION","?")
            self.__add2dVar(wrf_volc_file,"ERUP_END","END TIME OF ERUPTION","?")
            self.__add3dVar(wrf_volc_file,"E_VSO2","Volcanic Emissions, SO2","mol/m2/h")
            self.__add3dVar(wrf_volc_file,"E_VSULF","Volcanic Emissions, SULF","mol/m2/h")
            self.__add3dVar(wrf_volc_file,"E_QV","Volcanic Emissions, QV","kg/m2/s")

            for i in range(1,11):
                self.__add3dVar(wrf_volc_file,"E_VASH"+str(i),"Volcanic Emissions, bin"+str(i),"ug/m2/s")

        #todo: add record to netcdf file about this utility
    
    
    def __add3dVar(self,wrf_file,var_name,caption,units):
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

    def __add2dVar(self, wrf_file, var_name, caption, units):
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
        
    
    def __findClosetGridPoint(self, lat, lon):
        nrow=len(self.xlat)
        ncol=len(self.xlon[0])
        dist0=1000.0
        ii=0
        jj=0
        for i in range(nrow):
            for j in range(ncol):
                dist=np.sqrt((self.xlon[i,j]-lon)**2 +(self.xlat[i,j]-lat)**2)
                if (dist<dist0):
                    dist0=dist
                    jj=j
                    ii=i
        return ii,jj,dist0
