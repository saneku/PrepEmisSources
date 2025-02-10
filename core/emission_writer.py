class EmissionWriter:
    def __init__(self, scenarios, netcdf_handler):
        
        for scenario in scenarios:
            if not isinstance(scenario, EmissionScenario):
                raise TypeError("Scenario must be an instance of EmissionScenario")
        
        self.scenarios = scenarios

        if isinstance(netcdf_handler, NetCDFHandler):
            self.netcdf_handler = netcdf_handler
        else:
            raise TypeError("netcdf_handler must be an instance of NetCDFHandler")
        
    def write_emissions(self):
        
        ash_scenario.adjust_time() # interpoloate to new time points with 1 hour interval
        
        netcdf_handler.prepare_file(ash_scenario.getStartDateTime(),ash_scenario.getEndDateTime(),interval_days=0,interval_hours=0,interval_mins=60)
    
        ii,jj,dist0=self.netcdf_handler.findClosetGridPoint(15,165)
    
        #todo: get the heigth of levels from the dst netcdf file
        ash_scenario.adjust_height(h)
        ash_scenario.plot(linestyle='-', color='blue', marker='+')

        #self.netcdf_handler.write_data(self.emissions)
