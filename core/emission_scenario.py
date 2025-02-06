from abc import ABC, abstractmethod
import pickle
import numpy as np
from profiles.base import VerticalProfileDistribution
from profiles.types import InvertedProfile
import math
from scipy.interpolate import interp1d

class EmissionScenario(ABC):
    def __init__(self):
        self.profiles = []

    def add_profile(self, profile: VerticalProfileDistribution):
        if isinstance(profile, VerticalProfileDistribution):
            self.profiles.append(profile)
        else:
            raise TypeError("Profile must be an instance of VerticalProfileDistribution")

    def list_profiles(self):
        return [profile.__class__.__name__ for profile in self.profiles]

    def __repr__(self):
        return f"EmissionScenario(profiles={self.list_profiles()})"
    
        
class EmissionScenario_InvertedPinatubo(EmissionScenario):
    def __init__(self, filename):
        super().__init__()
        
        levels_h = np.array([91.56439, 168.86765, 273.9505, 407.21893, 574.90356, 788.33356, 1050.1624, 1419.9668, 
                            1885.3608, 2372.2937, 2883.3193, 3634.4663, 4613.3403, 5594.8545, 6580.381, 7568.5386, 
                            8558.1455, 9547.174, 10534.043, 11518.861, 12501.9375, 13484.473, 14454.277, 15393.3125, 
                            16300.045, 17189.598, 18083.797, 18998.496, 19939.57, 20905.723, 21890.363, 22886.46, 
                            23890.441, 24900.914, 25918.307, 26943.252, 27977.344, 29021.828, 30077.21, 31143.973, 
                            32221.8, 33310.13, 34408.86, 35517.9, 36637.133, 37766.45, 38905.723, 40054.82, 41213.594, 
                            42381.883, 43559.504, 44746.254, 45941.914, 47146.22])

        levels_dz = np.array([63.175426, 91.43107, 118.734634, 147.80225, 187.56696, 239.29309, 284.36438, 455.2445, 475.54382,
                            498.32178, 523.72925, 978.5652, 979.1826, 983.8462, 987.20654, 989.1084, 990.10547, 987.9502, 
                            985.78906, 983.8467, 982.3076, 982.7627, 956.8447, 921.22656, 892.2383, 886.86523, 901.53516, 
                            927.8633, 954.28516, 978.0176, 991.2637, 1000.9336, 1007.02734, 1013.9199, 1020.8633, 1029.0273, 
                            1039.1582, 1049.8066, 1060.9609, 1072.5605, 1083.0996, 1093.5547, 1103.9102, 1114.1641, 1124.3047, 
                            1134.3281, 1144.2188, 1153.9766, 1163.5742, 1173.0039, 1182.2344, 1191.2656, 1200.0508, 1208.5625])

        with open(filename,'rb') as infile:
            _,_,emission_scenario,years,months,days,hours,duration_sec,_ = pickle.load(infile,encoding='latin1')
            #or _,_,emission_scenario,years,months,days,hours,duration_sec,_ = pickle.load(infile)

        for i in range(emission_scenario.shape[1]):
            self.add_profile(InvertedProfile(levels_h,emission_scenario[:,i],years[i],
                                            months[i],days[i],hours[i],duration_sec[i]))


    def interpolate_on_time(self,time_interp):#, profile, time):
        #print(self.profiles)
        
        hours=[profile.hour for profile in self.profiles]
        scenario_2d_array=np.array([profile.values for profile in self.profiles]).T
            
        interp_solution_emission_scenario = np.array([interp1d(hours, scenario_2d_array[j, :], kind='linear', fill_value="extrapolate")(time_interp) for j in range(scenario_2d_array.shape[0])])
        #print (interp_solution_emission_scenario)

        new_hours = list(range(math.ceil(hours[0]),math.ceil(hours[-1])+1))
        new_hours.insert(0, hours[0])  # Insert at 2nd index
        
        new_duration=[np.diff(new_hours)]
        
        #interp_solution_emission_scenario = np.array([interp1d(self.profiles[:].hour
        #                                                       solution_hour, solution_emission_scenario[j, :], kind='linear', fill_value="extrapolate")(time_interp) for j in range(solution_emission_scenario.shape[0])])

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