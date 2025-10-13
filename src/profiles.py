import numpy as np
import calendar
from datetime import datetime
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from scipy.integrate import quad

class VerticalProfile():
    def __init__(self, staggerred_h,values,year,month,day,hour,duration_sec,scale=1):
        self.h = staggerred_h
        self.dh = np.array([])
        self.values = values * scale
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.duration_sec = duration_sec
        self.is_divided_by_dh = False
        
        self.start_datetime = datetime(int(self.year),int(self.month), int(self.day), 
                                int(self.hour),int((self.hour - int(self.hour))*60.0))
        
        if calendar.isleap(self.year):
            K = 1
        else:
            K = 2

        beg_jul = ((275 * self.month)/9) - K*((self.month+9)/12) + self.day - 30
        beg_jul = int(beg_jul)
        self.erup_beg = beg_jul * 1000. + self.hour
    
    @staticmethod
    def _ensure_within_domain_top(z_at_m, value, param_name, profile_name):
        domain_top = float(np.max(z_at_m)) if len(z_at_m) > 0 else 0.0
        if value > domain_top:
            raise ValueError(
                f"{profile_name} profile {param_name}={value:.1f} m exceeds vertical domain top={domain_top:.1f} m. "
                f"Reduce {param_name} or use a wrfinput with higher model top."
            )
    
    def __str__(self):
        return self.__class__.__name__
       
    def getProfileEmittedMass(self):
        if self.is_divided_by_dh == False:
            return np.sum(self.values * self.duration_sec)
        else:
            return np.sum(self.values * self.dh * self.duration_sec)
    
    def setDatetime(self,d):
        self.start_datetime=d.to_pydatetime()
    
    def getProfileStartTimeAndDuration(self):
        return self.erup_beg,self.duration_sec/60.0
    
    def plot(self,*args, **kwargs):
        plt.plot(self.values,self.h/1000.0,'-+', label=f"{str(self)}", *args, **kwargs)
        self._format_plot()
    
    def _format_plot(self):
        axes = plt.gca()
        axes.set_ylim([0,30])
        axes.set_xlim(-0.05,0.35)
        plt.xlabel('Mass fraction',fontsize=10)
        plt.ylabel('Altitude, km',fontsize=10)
        plt.legend(loc="best")
        plt.grid(True)
        plt.show()
        
    def normalize_by_one(self,arr):
        return arr / np.sum(arr)
    
    def interpoloate_height(self, new_height):        
        self.values = np.maximum(interp1d(self.h, self.values, kind='linear', bounds_error=False, fill_value=0)(new_height), 0)
        self.h = new_height

class VerticalProfile_Zero(VerticalProfile):
    def __init__(self, z_at_m, year, month, day, hour, duration_sec):
        profile = np.zeros(len(z_at_m))
        super().__init__(z_at_m,profile,year,month,day,hour,duration_sec)

class VerticalProfile_Uniform(VerticalProfile):
    def __init__(self, z_at_m, year, month, day, hour, duration_sec, h_min=5000.0, h_max=10000.0, scale=1):
        profile = np.ones(len(z_at_m))

        if(h_max<h_min):
            raise ValueError('h_max<h_min in Uniform profile')
    
        self.h_min = h_min
        self.h_max = h_max
        VerticalProfile._ensure_within_domain_top(z_at_m, self.h_max, "h_max", "Uniform")
        
        kts=0
        kte=len(z_at_m)

        for k in range(kte-1,kts,-1):
            if(z_at_m[k] < h_max):
                k_final = k+1
                break

        for k in range(kte-1,kts,-1):
            if(z_at_m[k] < h_min):
                k_initial = k
                break
    
        profile[0:k_initial]=0.0
        profile[k_final:kte]=0.0

        #profile = self.normalize_by_one(profile)
    
        super().__init__(z_at_m,profile,year,month,day,hour,duration_sec,scale)
        
    def __str__(self):
        return super().__str__()+f" min={self.h_min/1000.0:.2f}, max height {self.h_max/1000.0:.2f} km"

    def plot(self,*args, **kwargs):
        plt.plot(self.values,self.h/1000.0,'-+', label=super().__str__()+f" min={self.h_min/1000.0:.2f},\n max height {self.h_max/1000.0:.2f} km", *args, **kwargs)
        self._format_plot()

class VerticalProfile_Suzuki(VerticalProfile):
    '''
    Based on Suzuki et al. (1983) and Mastin and Van Eaton (2020)
    '''
    def __init__(self, z_at_m, year, month, day, hour, duration_sec, H=20000, k=8, scale=1):
        self.H = H   #top height of the cloud
        self.k = k
        self.h_max = H * (k-1)/k
        VerticalProfile._ensure_within_domain_top(z_at_m, self.H, "H", "Suzuki")
        
        kte=len(z_at_m)
        profile = np.zeros(kte)
    
        for i in range(0,kte-1,1):
            bs, err = quad(self.__suzuku_integrand, z_at_m[i],z_at_m[i+1])
            profile[i] = bs

        indexes=np.where(profile<0)
        profile[indexes]=1.0e-06
        #print(sum(profile)) #normalisation check
    
        super().__init__(z_at_m,profile,year,month,day,hour,duration_sec,scale)

    def __suzuku_integrand(self,z):
        return (self.k * self.k * (1-(z/self.H))*np.exp(self.k*((z/self.H)-1)))/(self.H*(1-(1+self.k)*np.exp(-self.k)))

    def plot(self,*args, **kwargs):
        plt.plot(self.values,self.h/1000.0,'-+', label=f"Suzuki K={self.k}, Max Height {self.H/1000.0:.2f} km", *args, **kwargs)
        plt.hlines(self.h_max/1000.0,-1,1, color='red', linestyle='--', label=f"Height of peak {self.h_max/1000.0:.2f} km")
        self._format_plot()
      
    def __str__(self):
        return super().__str__()+f": K={self.k}, Max Height {self.H/1000.0:.2f} km, Height of peak {self.h_max/1000.0:.2f} km"

    '''
    def original_suzuki(z):
	    return pow((1.0-(z/H))*np.exp(A*((z/H)-1.0)),lambda)

    #for original Suzuki profile
    lambda = 5.0
    A = 4.0
    H = 30.0  #top height of the cloud
    
    for i in range(0,kte-1,1):
        bs, err = original_suzuki(z_at_m[i])
        profile[i] = bs

    '''

class VerticalProfile_Umbrella(VerticalProfile):
    def __init__(self, z_at_m, year, month, day, hour, duration_sec, emiss_height=10000, vent_h=500, percen_mass_umbrela=0.75, scale=1):
        self.percen_mass_umbrela = percen_mass_umbrela
        self.base_umbrela = 1. - percen_mass_umbrela
        self.emiss_height = emiss_height
        profile = np.zeros(len(z_at_m))
        
        if (percen_mass_umbrela>1.0 or percen_mass_umbrela<0.0):
            raise ValueError('percen_mass_umbrela should be between 0 and 1 in Umbrella profile')
        
        if(self.emiss_height<vent_h):
            raise ValueError('emiss_height<vent_h in Umbrella profile')

        VerticalProfile._ensure_within_domain_top(z_at_m, self.emiss_height, "emiss_height", "Umbrella")

        #===========================================
        kts=0
        kte=len(z_at_m)

        ashz_above_vent = emiss_height - vent_h

        for k in range(kte-1,kts,-1):
            if(z_at_m[k] < emiss_height):
                k_final = k+1
                break

        for k in range(kte-1,kts,-1):
            if(z_at_m[k] < ((1.-self.base_umbrela) * ashz_above_vent) + vent_h):
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
                
        super().__init__(z_at_m,profile,year,month,day,hour,duration_sec,scale)

    def __str__(self):
        return super().__str__()+f"Umbrella mass {self.percen_mass_umbrela:.2f}%, Base mass {self.base_umbrela:.2f}%, \nMax Emissions Height {self.emiss_height/1000.0:.2f} km"

    def plot(self,*args, **kwargs):
        plt.plot(self.values,self.h/1000.0,'-+', label=f"Umbrella mass {self.percen_mass_umbrela:.2f}%, Base mass {self.base_umbrela:.2f}%, \nMax Emissions Height {self.emiss_height/1000.0:.2f} km", *args, **kwargs)
        self._format_plot()       