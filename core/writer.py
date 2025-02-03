class EmissionWriter:
    def __init__(self, emissions, netcdf_handler):
        self.emissions = emissions
        self.netcdf_handler = netcdf_handler

    def write_emissions_to_netcdf(self):
        self.netcdf_handler.write_data(self.emissions)
