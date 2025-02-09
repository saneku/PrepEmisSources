from abc import ABC, abstractmethod

class VerticalProfile(ABC):
    def __init__(self, staggerred_h,profile,year,month,day,hour,duration_sec):
        self.h = staggerred_h
        self.values = profile
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.duration_sec = duration_sec
        
    @abstractmethod
    def generate_profile(self, height_levels):
        pass
