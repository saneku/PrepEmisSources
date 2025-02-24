#from abc import ABC, abstractmethod
import numpy as np
import calendar
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

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
        
        if calendar.isleap(self.year):
            K = 1
        else:
            K = 2

        beg_jul = ((275 * self.month)/9) - K*((self.month+9)/12) + self.day - 30
        beg_jul = int(beg_jul)
        self.erup_beg = beg_jul * 1000. + self.hour
    
    def __str__(self):
        return self.__class__.__name__
       
    def getProfileEmittedMass(self):
        return np.sum(self.values * self.duration_sec)
    
    def setDatetime(self,d):
        self.start_datetime=d.to_pydatetime()
    #    return 
    
    def getProfileStartTimeAndDuration(self):
        return self.erup_beg,self.duration_sec/60.0
    
    def plot(self,*args, **kwargs):
            plt.plot(self.values,self.h/1000.0,'-+', label=f"{str(self)}", *args, **kwargs)
        
            axes = plt.gca()
            axes.set_ylim([0,30])
            axes.set_xlim(0,0.5)
            #plt.title("Mass Fractions")
            plt.xlabel('Mass fraction',fontsize=10)
            plt.ylabel('Altitude ,km',fontsize=10)
            plt.legend(loc="best")
            plt.grid(True)
            plt.show()
        
    def normalize_by_one(self,arr):
        return arr / np.sum(arr)

    #@abstractmethod
    #def generate_profile(self, height_levels):
    #    pass


class VerticalProfile_Uniform(VerticalProfile):
    def __init__(self, z_at_w, year, month, day, hour, duration_sec, value=1.0,h_min=5000.0,h_max=10000.0):
        profile = value * np.ones(len(z_at_w))

        if(h_max<h_min):
            raise ValueError('h_max<h_min in Uniform profile')
    
        kts=0
        kte=len(z_at_w)

        for k in range(kte-1,kts,-1):
            if(z_at_w[k] < h_max):
                k_final = k+1
                break

        for k in range(kte-1,kts,-1):
            if(z_at_w[k] < h_min):
                k_initial = k
                break
    
        profile[0:k_initial]=0.0
        profile[k_final:kte]=0.0

        profile = self.normalize_by_one(profile)
    
        super().__init__(z_at_w,profile,year,month,day,hour,duration_sec)

class VerticalProfile_Suzuki(VerticalProfile):
    def generate_profile(self, height_levels):
        return np.exp(-np.linspace(0, 1, height_levels))

class VerticalProfile_Umbrella(VerticalProfile):
    def __init__(self, z_at_w, year, month, day, hour, duration_sec, emiss_height=10000, vent_h=500, percen_mass_umbrela=0.75):
        self.percen_mass_umbrela = percen_mass_umbrela
        self.base_umbrela = 1. - percen_mass_umbrela
        self.emiss_height = emiss_height
        profile = np.zeros(len(z_at_w))
        
        if (percen_mass_umbrela>1.0 or percen_mass_umbrela<0.0):
            raise ValueError('percen_mass_umbrela should be between 0 and 1 in Umbrella profile')
        
        if(self.emiss_height<vent_h):
            raise ValueError('emiss_height<vent_h in Umbrella profile')

        #===========================================
        kts=0
        kte=len(z_at_w)

        ashz_above_vent = emiss_height - vent_h

        for k in range(kte-1,kts,-1):
            if(z_at_w[k] < emiss_height):
                k_final = k+1
                break

        for k in range(kte-1,kts,-1):
            if(z_at_w[k] < ((1.-self.base_umbrela) * ashz_above_vent) + vent_h):
                k_initial = k
                break

        #- parabolic vertical distribution between k_initial and k_final
        kk4 = k_final - k_initial+2

        for ko in range(1,kk4):
            kl = ko + k_initial - 1
            profile[kl] = 6. * percen_mass_umbrela * float(ko)/float(kk4)**2 * (1. - float(ko)/float(kk4))

        #make sure that we put percen_mass_umbrel in 'umbrella'
        if(sum(profile) != percen_mass_umbrela):
            x1= (percen_mass_umbrela - sum(profile)) /float(k_final-k_initial+1)
            for ko in range(k_initial,k_final+1):        
                profile[ko] = profile[ko]+ x1

        #linear detrainment from vent to base of umbrella
        for ko in range(0,k_initial):
            profile[ko]=float(ko)/float(k_initial-1)

        #normalisation of sum of fractions of below umbrella
        x1=sum(profile[0:k_initial])
        for ko in range(0,k_initial):
            profile[ko]=(1.-percen_mass_umbrela) * profile[ko]/x1

        #print(sum(profile)) #normalisation check
                
        super().__init__(z_at_w,profile,year,month,day,hour,duration_sec)

    def plot(self,*args, **kwargs):
        plt.plot(self.values,self.h/1000.0,'-+', \
                 label=f"Umbrella mass {self.percen_mass_umbrela:.2f}%, Base mass {self.base_umbrela:.2f}%, \
                 \nMax Emissions Height {self.emiss_height/1000.0:.2f} km", *args, **kwargs)
        
        axes = plt.gca()
        axes.set_ylim([0,30])
        axes.set_xlim(0,0.5)
        #axes.set_xscale('log')
        #plt.title("Mass Fractions")
        plt.xlabel('Mass fraction',fontsize=10)
        plt.ylabel('Altitude ,km',fontsize=10)
        plt.legend(loc="best")
        ###########################
        plt.grid(True)
        plt.show()