from abc import ABC, abstractmethod

class VerticalProfileDistribution(ABC):
    #def __init__(self, heights,dz,profile,year,month,day,hour,duration_sec):
    def __init__(self, heights,profile,year,month,day,hour,duration_sec):
        self.h = heights
        #self.dz= dz
        self.values = profile
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.duration_sec = duration_sec
        
        
    @abstractmethod
    def generate_profile(self, height_levels):
        pass
