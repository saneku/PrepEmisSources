from abc import ABC, abstractmethod
import pickle
import numpy as np
from profiles.base import VerticalProfile
from profiles.types import VerticalProfile_Simple
import math
from scipy.interpolate import interp1d
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

class EmissionScenario(ABC):
    def __init__(self):
        self.profiles = []

    def add_profile(self, profile: VerticalProfile):
        if isinstance(profile, VerticalProfile):
            self.profiles.append(profile)
        else:
            raise TypeError("Profile must be an instance of VerticalProfileDistribution")

    def __list_profiles(self):
        
        heights_on_levels=self.profiles[0].h
        scenario_2d_array=np.array([profile.values for profile in self.profiles]).T
        
        for j in np.arange(len(heights_on_levels)-1,-1,-1):
	        self.__print_vector(scenario_2d_array[j,:],sep=' ',f='{:0.6e}')
        
        return [profile.__class__.__name__ for profile in self.profiles]

    def _clear_profiles(self):
        self.profiles = []

    def __repr__(self):
        return f"EmissionScenario(profiles={self.__list_profiles()})"
    
    def _generate_dates(self,start_year, start_month, start_day, hours_list):
        start_date = datetime(start_year, start_month, start_day)
        years, months, days = [], [], []
        for hours in hours_list:
            new_date = start_date + timedelta(hours=hours)
            years.append(new_date.year)
            months.append(new_date.month)
            days.append(new_date.day)
        
        return years, months, days
    
    def __print_vector(self,vector,sep=' ',f="{:0.6e}"):
        print((sep.join(f.format(x) for x in vector)))

    def plot(self,*args, **kwargs):
        scale_factor=2000.0#*1000.0
        hours=[profile.hour for profile in self.profiles]
        fig = plt.figure(figsize=(18,7))
        for i, profile in enumerate(self.profiles):
            x_values = scale_factor * profile.values + profile.hour
            y_values = profile.h / 1000.0
            plt.plot(x_values, y_values, *args, **kwargs)
            
        plt.ylim(0.0, 40)
        #plt.xlim(0.0,0.03)
        plt.ylabel('Altitude, $km$')#,fontsize=CB_LABEL_TEXT_SIZE)
        plt.xlabel('Decimal hour')#,fontsize=CB_LABEL_TEXT_SIZE)
        #plt.yticks(fontsize=TICKS_TEXT_SIZE)
        #plt.xticks(fontsize=TICKS_TEXT_SIZE)

        plt.axhline(y=16.5, linestyle=':',color='black',linewidth=1.0)
        plt.gca().yaxis.set_major_locator(plt.MultipleLocator(5))
        plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(1))
        plt.xticks(hours)  # Set text labels.

        plt.title(f'Start time: {self.profiles[0].year}-{self.profiles[0].month}-{self.profiles[0].day} {self.profiles[0].hour}')
        
        plt.grid(True,alpha=0.3)
        plt.show()

        
class EmissionScenario_InvertedPinatubo(EmissionScenario):
    def __init__(self, filename):
        super().__init__()
        
        staggerred_h = np.array([91.56439, 168.86765, 273.9505, 407.21893, 574.90356, 788.33356, 1050.1624, 1419.9668, 
                            1885.3608, 2372.2937, 2883.3193, 3634.4663, 4613.3403, 5594.8545, 6580.381, 7568.5386, 
                            8558.1455, 9547.174, 10534.043, 11518.861, 12501.9375, 13484.473, 14454.277, 15393.3125, 
                            16300.045, 17189.598, 18083.797, 18998.496, 19939.57, 20905.723, 21890.363, 22886.46, 
                            23890.441, 24900.914, 25918.307, 26943.252, 27977.344, 29021.828, 30077.21, 31143.973, 
                            32221.8, 33310.13, 34408.86, 35517.9, 36637.133, 37766.45, 38905.723, 40054.82, 41213.594, 
                            42381.883, 43559.504, 44746.254, 45941.914, 47146.22])

        with open(filename,'rb') as infile:
            _,_,emission_scenario,years,months,days,hours,duration_sec,_ = pickle.load(infile,encoding='latin1')

        for i in range(emission_scenario.shape[1]):
            self.add_profile(VerticalProfile_Simple(staggerred_h,emission_scenario[:,i],years[i],
                                            months[i],days[i],hours[i],duration_sec[i]))


    def adjust_time(self):
        
        hours=[profile.hour for profile in self.profiles]
        durations_hours=[profile.duration_sec/3600 for profile in self.profiles]
        
        if (math.ceil(hours[-1]) > (hours[-1] + durations_hours[-1])):
            end_hour = math.ceil(hours[-1])-1
        else:
            end_hour =  math.ceil(hours[-1])
        
        new_hours = list(range(math.ceil(hours[0]),end_hour))
        new_hours.insert(0, hours[0])  # Insert at 2nd index
        new_hours.append(end_hour)
        new_duration_hours=list(np.diff(new_hours))
        new_duration_hours.append((hours[-1] + durations_hours[-1])-end_hour)
        
        #interpolate the emission scenario into the new time points
        scenario_2d_array = np.array([profile.values for profile in self.profiles]).T
        interp_solution_emission_scenario = np.array(
            [np.maximum(interp1d(hours, scenario_2d_array[j, :], kind='linear', fill_value="extrapolate")(new_hours), 0)
            for j in range(scenario_2d_array.shape[0])])
        
        
        levels_h = self.profiles[0].h        
        new_years, new_months, new_days = self._generate_dates(self.profiles[0].year, self.profiles[0].month, self.profiles[0].day, new_hours)
        self._clear_profiles()
        
        for i in range(interp_solution_emission_scenario.shape[1]):
            self.add_profile(VerticalProfile_Simple(levels_h,interp_solution_emission_scenario[:,i],new_years[i],
                                new_months[i],new_days[i],new_hours[i],new_duration_hours[i]*3600))

    def adjust_height(self,new_height):
        
        if(np.all(new_height[1:] > new_height[:-1])==False):
            raise ValueError('new_height must be monotonically increasing')
        
        for profile in self.profiles:
            profile.values=np.maximum(interp1d(profile.h, profile.values, kind='linear', fill_value="extrapolate")(new_height), 0)
            profile.h=new_height
        
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