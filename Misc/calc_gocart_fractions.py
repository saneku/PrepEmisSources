from scipy.integrate import quad
import numpy as np

#how to get the ash mass fractions for the GOCART bins based on the lognormal distribution

class Emission_Ash():
    def __init__(self, bin_n=5, mean_r=2.4, stddev=1.8):
        self.radii = mean_r
        self.stddev = stddev
        
        self.nbin = bin_n
        self.ash_mass_factors = self.__compute_ash_mass_fractions()
        
        
    def __volume_integrand(self,r):
        mu = np.log(self.radii)
        sigma = np.log(self.stddev)
        return (r**2)*(np.exp(-(np.log(r) - mu)**2 / (2 * sigma**2))/(sigma * np.sqrt(2 * np.pi)))

    def __compute_ash_mass_fractions(self):

        rlo_sect=np.array([ 0.1, 1. , 1.8, 3. , 6. ])
        rhi_sect=np.array([ 1. , 1.8, 3. , 6., 10. ])


        total_volume, _ = quad(self.__volume_integrand, rlo_sect[0], rhi_sect[-1])
        
        xmas_sect = np.zeros(5)
        for n in range(0,self.nbin):
            xmas_sect[n], _ = quad(self.__volume_integrand, rlo_sect[n], rhi_sect[n])
            xmas_sect[n] = xmas_sect[n]/total_volume

        if not np.isclose(np.sum(xmas_sect), 1.0):
            raise ValueError(f"sum(xmas_sect)={np.sum(xmas_sect):0.2f} Should be =1.0")

        return xmas_sect
    
    
e=Emission_Ash(mean_r=2.4,stddev=1.8)
print (e.ash_mass_factors)

#SHOULD BE:
#GOCART fractions [0.001, 0.015, 0.095, 0.45, 0.439] into ash bins: