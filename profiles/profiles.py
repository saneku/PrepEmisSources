#from abc import ABC, abstractmethod
import numpy as np
import calendar
from datetime import datetime, timedelta

class VerticalProfile():
    def __init__(self, staggerred_h,profile,year,month,day,hour,duration_sec):
        self.h = staggerred_h
        self.values = profile
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.duration_sec = duration_sec
        
        self.start_datetime = datetime(int(self.year),int(self.month), int(self.day), 
                                int(self.hour),int((self.hour - int(self.hour))*60.0))
        #self.construct_start_datetime()
       
    def getProfileEmittedMass(self):
        return np.sum(self.values * self.duration_sec)
    
    def setDatetime(self,d):
        self.start_datetime=d.to_pydatetime()
    #    return 
    
    def getProfileStartTimeAndDuration(self):
        if calendar.isleap(self.year):
            K = 1
        else:
            K = 2

        beg_jul = ((275 * self.month)/9) - K*((self.month+9)/12) + self.day - 30
        beg_jul = int(beg_jul)
        erup_beg = beg_jul * 1000. + self.hour

        return erup_beg,self.duration_sec/60.0
    
    #@abstractmethod
    #def generate_profile(self, height_levels):
    #    pass


class VerticalProfile_Zero(VerticalProfile):
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
