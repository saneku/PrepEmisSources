import pickle
import numpy as np
import pandas as pd
import math
from scipy.interpolate import interp1d
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

from .profiles import *
from .emissions import *

class EmissionScenario():
    def __init__(self,type_of_emission):
        self.profiles = []
        self.__is_divided_by_dh = False
        self.__is_normalized_by_total_mass = False
        self.__is_height_adjusted = False
        self.__is_time_adjusted = False

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

    def __str__(self):
        return self.__class__.__name__

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
    
    def plot(self,*args, **kwargs):
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
       
        plt.title(self.__getString())
        
        plt.grid(True,alpha=0.3)
        plt.show()
        
    def __getString(self):        
        if (self.__is_divided_by_dh):
            if (self.__is_normalized_by_total_mass):
                return f'{self}. {self.getNumberOfProfiles()} profiles. \n{self.type_of_emission}. \nStart time: {self.getStartDateTime()} End time: {self.getEndDateTime()}. Units [Mt/m/s]. Normalized by total mass = {self.getScenarioEmittedMass():.2f} Mt'
            else:
                return f'{self}. {self.getNumberOfProfiles()} profiles. \n{self.type_of_emission}. \nStart time: {self.getStartDateTime()} End time: {self.getEndDateTime()}. Units [Mt/m/s]'
        else:
            return f'{self}. {self.getNumberOfProfiles()} profiles. \n{self.type_of_emission}.\nStart time: {self.getStartDateTime()} End time: {self.getEndDateTime()}. Units [Mt/s]'

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

        self.__is_time_adjusted = True

    def interpolate_height(self,new_height):        
        if (self.__is_time_adjusted == False):    
            raise ValueError('Time must be adjusted before adjusting height')
        
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
        

class EmissionScenario_InvertedPinatubo(EmissionScenario):
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

class EmissionScenario_MixOfProfiles(EmissionScenario):
    def __init__(self, type_of_emission):
        super().__init__(type_of_emission)    



'''
def read_eruption_file(self, filename):
    # Read the file
    with open(filename, 'r') as f:
        lines = f.readlines()

    # Extract dimensions from the first two lines
    self.rows = int(lines[0].strip())
    self.cols = int(lines[1].strip())
    
    self.years = int(lines[2].strip())
    self.months = int(lines[3].strip())
    self.days = int(lines[4].strip())
    self.hours = int(lines[5].strip())
    self.duration_sec = int(lines[6].strip())

    # Extract the array data starting from the 8th line (index 7) for 'rows' number of lines
    emission_scenario = []
    for line in lines[7 : 7 + self.rows]:
        row = list(map(float, line.strip().split()))
        array_data.append(row)
    # array_data is now a 2D list (rows x cols) containing the values from the file
'''