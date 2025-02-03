import netCDF4 as nc

class NetCDFHandler:
    def __init__(self, source_dir)#, destination_file):
        self.source_dir = source_dir
        #self.destination_file = destination_file


        self.orgn_wrf_input_file="wrfinput_d01"
        self.dst_file="wrfchemv_d01"


        #===========================================
        #Read wrfinput data
        print (f'Open {self.source_dir}{orgn_wrf_input_file}')
        wrfinput=Dataset(f'{self.source_dir}{orgn_wrf_input_file}','r')
        self.xlon=wrfinput.variables['XLONG'][0,:]
        self.xlat=wrfinput.variables['XLAT'][0,:]
        MAPFAC_MX=wrfinput.variables['MAPFAC_MX'][0,:]
        MAPFAC_MY=wrfinput.variables['MAPFAC_MY'][0,:]

        dy = wrfinput.getncattr('DY')
        dx = wrfinput.getncattr('DX')
        self.surface = (dx/MAPFAC_MX)*(dy/MAPFAC_MY)       #surface in m2

        self.Z = (wrfinput.variables['PH'][0,:] + wrfinput.variables['PHB'][0,:]) / 9.81
        dz = np.diff(self.Z,axis=0)

        self.Z = self.Z[:-1]
        self.Z = self.Z + dz*0.5
        self.Z = self.Z/1000.0

        wrfinput.close()
        
        #===========================================
        #copy wrfinput to wrfchemv
        if os.path.exists(f'{self.source_dir}{dst_file}'):
            os.system(f'rm {self.source_dir}{dst_file}')

        ds = xr.open_dataset(f'{self.source_dir}{orgn_wrf_input_file}')
        ds_var = ds[['PH','PHB','T','Times']]
        ds_var.to_netcdf(f'{self.source_dir}{dst_file}')
        #===========================================
        
        #here
        wrf_volc_file = Dataset(f'{orgn_dir}{dst_file}','r+')
        add2dVar(wrf_volc_file,"ERUP_BEG","START TIME OF ERUPTION","?")
        add2dVar(wrf_volc_file,"ERUP_END","END TIME OF ERUPTION","?")
        add3dVar(wrf_volc_file,"E_VSO2","Volcanic Emissions, SO2","mol/m2/h")
        add3dVar(wrf_volc_file,"E_VSULF","Volcanic Emissions, SULF","mol/m2/h")
        add3dVar(wrf_volc_file,"E_QV","Volcanic Emissions, QV","kg/m2/s")

        for i in range(1,11):
            add3dVar(wrf_volc_file,"E_VASH"+str(i),"Volcanic Emissions, bin"+str(i),"ug/m2/s")



    def write_data(self, emissions):
        with nc.Dataset(self.destination_file, 'w', format='NETCDF4') as dataset:
            dataset.createDimension('emission', len(emissions))
            
            locations = dataset.createVariable('location', str, ('emission',))
            amounts = dataset.createVariable('amount', 'f4', ('emission',))
            durations = dataset.createVariable('duration', 'f4', ('emission',))
            start_times = dataset.createVariable('start_time', str, ('emission',))
            
            locations[:] = [e.location for e in emissions]
            amounts[:] = [e.amount for e in emissions]
            durations[:] = [e.duration for e in emissions]
            start_times[:] = [e.start_time for e in emissions]

    def prepare_file():
        dataset = nc.Dataset(self.destination_file, 'a')
        days=range(0,366)
        aux_times = np.chararray((len(days), 19), itemsize=1)
        start_date = datetime(2016, 1, 1, 0, 0)
        for i, day in enumerate(days):
            aux_date = start_date + timedelta(days=day)
            aux_times[i] = list(aux_date.strftime("%Y-%m-%d_%H:%M:%S"))
        dataset.variables['Times'][:] = aux_times
        # Loop through all variables and copy the first time step to the new time steps
        for var_name in dataset.variables:
            if var_name == 'Times':
                continue
            var = dataset.variables[var_name]
            if 'Time' in var.dimensions:
                print(var)
                for i in days:
                    var[i,:]=var[0,:]