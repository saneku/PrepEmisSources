#from abc import ABC, abstractmethod

class VerticalProfile():
    def __init__(self, staggerred_h,profile,year,month,day,hour,duration_sec):
        self.h = staggerred_h
        self.values = profile
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.duration_sec = duration_sec
        
    #@abstractmethod
    #def generate_profile(self, height_levels):
    #    pass


class VerticalProfile_Uniform(VerticalProfile):
    def generate_profile(self, height_levels):
        return np.ones(height_levels) / height_levels

class VerticalProfile_Suzuki(VerticalProfile):
    def generate_profile(self, height_levels):
        return np.exp(-np.linspace(0, 1, height_levels))

class VerticalProfile_Umbrella(VerticalProfile):
    def generate_profile(self, height_levels):
        return np.ones(height_levels) / height_levels

#class VerticalProfile_Simple(VerticalProfile):
#    def generate_profile(self, height_levels):
#        return np.flip(np.linspace(0, 1, height_levels))
