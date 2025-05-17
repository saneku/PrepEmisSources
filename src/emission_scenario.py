import pickle
import numpy as np
import pandas as pd
import json
from scipy.interpolate import interp1d
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from .profiles import *
from .emissions import *

class EmissionScenario():
    def __init__(self,type_of_emission):
        self.profiles = []
        self.__is_divided_by_dh = False
        self.__is_normalized_by_total_mass = False
        self.__is_height_adjusted = False
        #self.__is_time_adjusted = False

        if (isinstance(type_of_emission, Emission) == False):
            raise TypeError("type_of_emission must be an instance of Emission")
        
        self.type_of_emission = type_of_emission

    def add_profile(self, profile: VerticalProfile):
        if isinstance(profile, VerticalProfile):
            self.profiles.append(profile)
        else:
            raise TypeError("Profile must be an instance of VerticalProfile")

    def __list_profiles(self):
        heights_on_levels=self.profiles[0].h
        scenario_2d_array=np.array([profile.values for profile in self.profiles]).T
        
        for j in np.arange(len(heights_on_levels)-1,-1,-1):
	        self.__print_vector(scenario_2d_array[j,:],sep=' ',f='{:0.6e}')
        
        return [profile.__class__.__name__ for profile in self.profiles]

    def getNumberOfProfiles(self):
        return len(self.profiles)

    def _clear_profiles(self):
        self.profiles = []

    #def getProfiles(self):
    #    for p in self.profiles:
    #        yield p

    def __repr__(self):
        return f"EmissionScenario(profiles={self.__list_profiles()})"
    
    def __print_vector(self,vector,sep=' ',f="{:0.6e}"):
        print((sep.join(f.format(x) for x in vector)))
    
    #returns start time of eruption.
    def getStartDateTime(self):
        return self.profiles[0].start_datetime

    #returns end time of eruption.
    def getEndDateTime(self):
        return self.profiles[-1].start_datetime + timedelta(seconds=int(self.profiles[-1].duration_sec))
    
    def get_profiles_Decimal_StartTimeAndDuration(self):
        start_times = []
        duration_mins = []
        for profile in self.profiles:
            s,d = profile.getProfileStartTimeAndDuration()
            start_times.append(s)
            duration_mins.append(d)
        
        return start_times,duration_mins
    
    def get_profiles_StartDateTime(self):
        return [profile.start_datetime for profile in self.profiles]
    
    def getScenarioEmittedMass(self):
        return np.sum([profile.getProfileEmittedMass() for profile in self.profiles])

    def __scaleProfiles(self, scale):
        for profile in self.profiles:
            profile.values = profile.values * scale

    def normalize_by_total_mass(self):
        mass_before=self.getScenarioEmittedMass()
        scale = self.type_of_emission.mass_Mt/mass_before
        self.__scaleProfiles(scale)
        mass_after=self.getScenarioEmittedMass()
        print(f'\n{self.type_of_emission.get_name_of_material()} mass before: \
              {mass_before:.3f} Mt, and after: {mass_after:.3f} Mt normalisation')
        
        self.__is_normalized_by_total_mass = True
    
    def plot_profiles(self,*args, **kwargs):
        scale_factor=2000.0#*1000.0
        
        if (self.__is_divided_by_dh):
            scale_factor = scale_factor * 1000.0    #for conviniency
        
        hours=[profile.hour for profile in self.profiles]
        fig = plt.figure(figsize=(18,7))
        for i, profile in enumerate(self.profiles):
            x_values = scale_factor * profile.values + profile.hour
            y_values = profile.h / 1000.0
            plt.plot(x_values, y_values, *args, **kwargs)
            
        plt.ylim(0.0, 40)
        #plt.xlim(0.0,0.03)
        plt.ylabel('Altitude, $km$')
        plt.xlabel('Decimal hour')

        plt.axhline(y=16.5, linestyle=':',color='black',linewidth=1.0)
        plt.gca().yaxis.set_major_locator(plt.MultipleLocator(5))
        plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(1))
        plt.xticks(hours)
       
        plt.title(self)
        
        plt.grid(True,alpha=0.3)
        plt.show()
  
    def __getColorMap(self,colormap = 'stohl', bins=256):
        #taken from https://github.com/metno/VolcanicAshInversion/
        
        #If we already have a colormap
        if (not isinstance(colormap, str)):
            return colormap

        colors = [
            (0.0, (1.0, 1.0, 0.8)),
            (0.05, (0.0, 1.0, 0.0)),
            (0.4, (0.9, 1.0, 0.2)),
            (0.6, (1.0, 0.0, 0.0)),
            (1.0, (0.6, 0.2, 1.0))
        ]
        if (colormap == 'default'):
            pass
        elif (colormap == 'ippc'):
            colors = [
                (0.0/4, (1.0, 1.0, 1.0)), #0-0.2 g/m2 white
                (0.2/4, (0.498, 0.996, 0.996)), #0.2-2.0 g/m2 turquoise
                (2.0/4, (0.573, 0.58, 0.592)), #2.0-4.0 g/m2 gray
                (4.0/4, (0.875, 0.012, 0.012)) # >4.0 g/m2 red
            ]
            bins = 5
        elif (colormap == 'alternative'):
            colors = [
                (0.0, (1.0, 1.0, 0.6)),
                (0.4, (0.9, 1.0, 0.2)),
                (0.6, (1.0, 0.8, 0.0)),
                (0.7, (1.0, 0.4, 0.0)),
                (0.8, (1.0, 0.0, 0.0)),
                (0.9, (1.0, 0.2, 0.6)),
                (1.0, (0.6, 0.2, 1.0))
            ]
        elif (colormap == 'birthe'):
            colors = [
                ( 0/35, ("#ffffff")),
                ( 4/35, ("#b2e5f9")),
                (13/35, ("#538fc9")),
                (18/35, ("#47b54c")),
                (25/35, ("#f5e73c")),
                (35/35, ("#df2b24"))
            ]
        elif (colormap == 'stohl'):
            colors = [
                ( 0.00/10, ("#ffffff")),
                ( 0.35/10, ("#ffe5e2")),
                ( 0.60/10, ("#b1d9e6")),
                ( 1.00/10, ("#98e8a8")),
                ( 2.00/10, ("#fffc00")),
                ( 5.00/10, ("#ff0d00")),
                (10.00/10, ("#910000"))
            ]
        else:
            # Assume this is a standard matplotlib colormap name
            return colormap
            
        cm = LinearSegmentedColormap.from_list('ash', colors, N=bins)
        cm.set_bad(alpha = 0.0)

        return cm
  
    def plot(self,*args, **kwargs):
        
        scenario_2d_array = np.array([profile.values for profile in self.profiles]).T
        h = self.profiles[0].h
        times = [profile.start_datetime for profile in self.profiles]
        
        fig = plt.figure(figsize=(14,7))
        
        plt.pcolormesh(times, h/1000.0, scenario_2d_array,alpha=0.08, zorder=2, facecolor='none', edgecolors='grey', linewidths=0.01)
        cs=plt.pcolormesh(times, h/1000.0, scenario_2d_array,cmap=self.__getColorMap())
        
        plt.colorbar(cs,label='Emissions')

        plt.ylim(0.0, 40)
        plt.ylabel('Altitude, $km$')
        plt.xlabel('Datetime')

        plt.axhline(y=16.5, linestyle=':',color='black',linewidth=1.0)
        plt.gca().yaxis.set_major_locator(plt.MultipleLocator(5))
        plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(1))
       
        plt.title(self)
        
        #plt.grid(True,alpha=0.3)
        plt.show()
  
    def __str__(self):
        s = self.__class__.__name__+" "+f'{self.getNumberOfProfiles()} profiles. {self.type_of_emission}. \
        \nStart time: {self.getStartDateTime()} End time: {self.getEndDateTime()}. '
        
        if (self.__is_divided_by_dh):
            if (self.__is_normalized_by_total_mass):
                return s +  f'Units [Mt/m/s]. Normalized by total mass = {self.getScenarioEmittedMass():.2f} Mt'
            else:
                return s + 'Units [Mt/m/s]'
        else:
            return s + 'Units [Mt/s]'

    def interpolate_time(self, interval_minutes=60):
        dt = self.getStartDateTime()
        # Round minutes to nearest 10th
        new_minute = round(dt.minute / 10.0) * 10.0
        # Adjust datetime accordingly
        StartDateTime_rounded = dt.replace(minute=0, second=0) + timedelta(minutes=new_minute)

        new_datetime_list = pd.date_range(start=StartDateTime_rounded, end=self.getEndDateTime(), 
                           freq=pd.Timedelta(days=0, hours=0, minutes=interval_minutes))

        old_datetime_list = [profile.start_datetime for profile in self.profiles]
        
        #Generate new dates based on the new hours, keep h the same
        levels_h = self.profiles[0].h     
        new_years = new_datetime_list.year.tolist()
        new_months = new_datetime_list.month.tolist()
        new_days = new_datetime_list.day.tolist()
        new_hours = new_datetime_list.hour.tolist()
        new_minutes = new_datetime_list.minute.tolist()
        new_duration_hours = np.diff(new_datetime_list)/ np.timedelta64(1, 'h')
        new_duration_hours = np.append(new_duration_hours,0)

        # Interpolate the emission scenario into the new time points
        temp_scenario_2d_array = np.array([profile.values for profile in self.profiles]).T
        
        temp_interp_solution_emission_scenario = np.zeros([temp_scenario_2d_array.shape[0],len(new_datetime_list)])
        for j in range(temp_scenario_2d_array.shape[0]):
            df = pd.DataFrame({"datetime": old_datetime_list, "value": temp_scenario_2d_array[j, :]}).set_index("datetime")
            new_values = df.reindex(df.index.union(new_datetime_list), method='bfill').interpolate(method="time").loc[new_datetime_list]["value"].tolist()
            temp_interp_solution_emission_scenario[j,:] = np.maximum(new_values,0)
        
        # Clear existing profiles
        self._clear_profiles() 
        
        # Add new profiles with interpolated values at new time points. -1 because last time is the time, when eruption is finished.
        for i in range(temp_interp_solution_emission_scenario.shape[1]):
            p=VerticalProfile(levels_h,temp_interp_solution_emission_scenario[:,i],new_years[i],
                                            new_months[i],new_days[i],new_hours[i]+new_minutes[i]/60.0,new_duration_hours[i] * 3600)
            p.setDatetime(new_datetime_list[i])
            self.add_profile(p)

        #zero emissions for last profile
        self.profiles[-1].values *=0
        self.profiles[-1].erup_beg=0

        #self.__is_time_adjusted = True

    def interpolate_height(self,new_height):        
        #if (self.__is_time_adjusted == False):    
        #    raise ValueError('Time must be adjusted before adjusting height')
        
        if(np.all(new_height[1:] > new_height[:-1])==False):
            raise ValueError('new_height must be monotonically increasing')
        
        for profile in self.profiles:
            profile.values=np.maximum(interp1d(profile.h, profile.values, kind='linear', fill_value="extrapolate")(new_height), 0)
            profile.h=new_height
        
        self.__is_height_adjusted = True
    
    def divide_by_dh(self,dh):        
        if (self.__is_height_adjusted == False):
            raise ValueError('Height must be adjusted before dividing by dh')
        
        for profile in self.profiles:
            profile.values = profile.values / dh
        
        self.__is_divided_by_dh = True
        

class EmissionScenario_MixOfProfiles(EmissionScenario):
    def __init__(self, type_of_emission):
        super().__init__(type_of_emission)    


class EmissionScenario_Inverted_Pinatubo(EmissionScenario):
    def __init__(self, type_of_emission, filename):
        super().__init__(type_of_emission)
        
        #staggerred_h is from the paper
        staggerred_h = np.array([91.56439, 168.86765, 273.9505, 407.21893, 574.90356, 788.33356, 1050.1624, 1419.9668, 
                            1885.3608, 2372.2937, 2883.3193, 3634.4663, 4613.3403, 5594.8545, 6580.381, 7568.5386, 
                            8558.1455, 9547.174, 10534.043, 11518.861, 12501.9375, 13484.473, 14454.277, 15393.3125, 
                            16300.045, 17189.598, 18083.797, 18998.496, 19939.57, 20905.723, 21890.363, 22886.46, 
                            23890.441, 24900.914, 25918.307, 26943.252, 27977.344, 29021.828, 30077.21, 31143.973, 
                            32221.8, 33310.13, 34408.86, 35517.9, 36637.133, 37766.45, 38905.723, 40054.82, 41213.594, 
                            42381.883, 43559.504, 44746.254, 45941.914, 47146.22])

        with open(filename,'rb') as infile:
            _,_,emission_scenario,years,months,days,hours,duration_sec,_ = pickle.load(infile,encoding='latin1')
        #emission_scenario in [Mt]
        for i in range(emission_scenario.shape[1]):
            self.add_profile(VerticalProfile(staggerred_h,emission_scenario[:,i],years[i],
                                            months[i],days[i],hours[i],duration_sec[i]))


class EmissionScenario_Inverted_Eyjafjallajokull(EmissionScenario):
    def __init__(self, type_of_emission, json_filename):
        super().__init__(type_of_emission)
        
        json_data = self.__readJson(json_filename)
        years,months,days,hours = [],[],[],[]

        for ts in json_data['emission_times']:
            dt = pd.to_datetime(ts).to_pydatetime()
            years.append(dt.year)
            months.append(dt.month)
            days.append(dt.day)
            hours.append(dt.hour)
        
        #h - height of the levels
        h = np.array([a for a in np.cumsum(np.concatenate(([json_data['volcano_altitude']], json_data['level_heights'])))])
        #staggerred_h - height of the 'mass' points
        staggerred_h = h[0:-1] + 0.5 * json_data['level_heights']
        emission_scenario = np.array(json_data['a_posteriori'])
        
        emission_scenario *= 1e-9   #emission_scenario in [Mt/m/s] now
        self.__is_divided_by_dh = True
        for i in range(emission_scenario.shape[1]):
            self.add_profile(VerticalProfile(staggerred_h,emission_scenario[:,i],years[i],
                                            months[i],days[i],hours[i],3*60*60))

    def __expandVariable(self,emission_times, level_heights, ordering_index, variable):
        #Make JSON-data into 2d matrix
        x = np.ma.masked_all(ordering_index.shape)
        for t in range(len(emission_times)):
            for a in range(len(level_heights)):
                emis_index = ordering_index[a, t]
                if (emis_index >= 0):
                    x[a, t] = variable[emis_index]
        return x

    def __readJson(self,json_filename):
        #Read data
        with open(json_filename, 'r') as infile:
            json_string = infile.read()

        #Parse data
        json_data = json.loads(json_string)

        #Add metadata to json_data
        #json_data["filename"] = os.path.abspath(json_filename)
        #json_data["meta"] = json.dumps(json_data)

        #Parse data we care about
        json_data["emission_times"] = np.array(json_data["emission_times"], dtype='datetime64[ns]')
        json_data["level_heights"] = np.array(json_data["level_heights"], dtype=np.float64)
        #volcano_altitude = json_data["volcano_altitude"]

        json_data["ordering_index"] = np.array(json_data["ordering_index"], dtype=np.int64)
        #json_data["a_priori"] = np.array(json_data["a_priori_2d"], dtype=np.float64)
        json_data["a_posteriori"] = np.array(json_data["a_posteriori_2d"], dtype=np.float64)

        #json_data["residual"] = np.array(json_data["residual"], dtype=np.float64)
        #json_data["convergence"] = np.array(json_data["convergence"], dtype=np.float64)

        #json_data["run_date"] = np.array(json_data["run_date"], dtype='datetime64[ns]')

        #Make JSON-data into 2d matrix
        json_data["a_posteriori"] = self.__expandVariable(json_data["emission_times"], json_data["level_heights"], json_data["ordering_index"], json_data["a_posteriori"])
        #json_data["a_priori"] = expandVariable(json_data["emission_times"], json_data["level_heights"], json_data["ordering_index"], json_data["a_priori"])

        #Prune any unused a priori elevations and timesteps
        #if (prune):
        #    valid_elevations = max(np.flatnonzero((json_data['a_priori'].max(axis=1) + json_data['a_posteriori'].max(axis=1)) > prune_zero)) + 1
        #    valid_times = np.flatnonzero((json_data['a_priori'].max(axis=0) + json_data['a_posteriori'].max(axis=0)) > prune_zero)
        #    if valid_times_min is None:
        #        valid_times_min = min(valid_times)
        #    if valid_times_max is None:
        #        valid_times_max = max(valid_times) + 1

            #json_data['a_priori'] = json_data['a_priori'][:valid_elevations,valid_times_min:valid_times_max]
        #    json_data['a_posteriori'] = json_data['a_posteriori'][:valid_elevations,valid_times_min:valid_times_max]
        #    json_data["ordering_index"] = json_data["ordering_index"][:valid_elevations,valid_times_min:valid_times_max]
        #    json_data["emission_times"] = json_data["emission_times"][valid_times_min:valid_times_max]
        #    json_data["level_heights"] = json_data['level_heights'][:valid_elevations]

        return json_data