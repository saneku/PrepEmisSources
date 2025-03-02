from abc import ABC, abstractmethod
from scipy.integrate import quad
import numpy as np

class Emission(ABC):
    def __init__(self, mass_mt,lat,lon):
        self.mass_Mt = mass_mt
        
        if not (-90 <= lat <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= lon <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        
        self.lat = lat
        self.lon = lon

    def __str__(self):        
        return f" emission: {self.mass_Mt} Mt, lat: {self.lat}, lon: {self.lon}"
        
    @abstractmethod
    def get_name_of_material(self):
        pass

class Emission_Ash(Emission):
    def __init__(self, mass_mt,lat,lon,bin_n,mean_r,stddev):
        self.radii = mean_r
        self.stddev = stddev
        
        if bin_n not in [4,10]:
            ValueError("Number of ash bins must be 4 or 10")
            
        self.nbin = bin_n
        self.ash_mass_factors = self.__compute_ash_mass_fractions()
        
        print ("Ash mass redistribution (Ash1, Ash2, Ash3,...): "+(' '.join(str("{:.3f}".format(x)) for x in self.ash_mass_factors[::-1])))
        
        super().__init__(mass_mt,lat,lon)
        
    def __volume_integrand(self,r):
        mu = np.log(self.radii)
        sigma = np.log(self.stddev)
        return (r**2)*(np.exp(-(np.log(r) - mu)**2 / (2 * sigma**2))/(sigma * np.sqrt(2 * np.pi)))

    def __compute_ash_mass_fractions(self):

        #10 ash size bins
        #Ash10,Ash9,Ash8,...,Ash1
        rlo_sect = np.array([1.955e-02, 1.953125, 3.90625, 7.8125,15.625,31.25,62.5,125.,250.,500.])
        rhi_sect = np.array([1.953125, 3.90625, 7.8125,15.625,31.25,62.5,125.,250.,500.,1000.])

        if self.nbin == 4:
            rlo_sect=rlo_sect[0:4]
            rhi_sect=rhi_sect[0:4]
        
        total_volume, _ = quad(self.__volume_integrand, rlo_sect[0], rhi_sect[-1])
        
        #initialize 10 ash size bins. 
        xmas_sect = np.zeros(10)
        for n in range(0,self.nbin):
            xmas_sect[n], _ = quad(self.__volume_integrand, rlo_sect[n], rhi_sect[n])
            xmas_sect[n] = xmas_sect[n]/total_volume

        if not np.isclose(sum(xmas_sect), 1.0):
            raise ValueError(f"sum(xmas_sect)={np.sum(xmas_sect):0.2f} Should be =1.0")

        return xmas_sect

    def __str__(self):
        return f'Ash {super().__str__()}.\n Mean_r={self.radii:.2f} stddev={self.stddev:.2f}.\n Ash mass fractions={[f"{x:.3f}" for x in self.ash_mass_factors[::-1]]}'
    
    def get_name_of_material(self):
        return 'ash'

class Emission_SO2(Emission):
    def __str__(self):
        return f'SO2 {super().__str__()}'

    def get_name_of_material(self):
        return 'so2'

class Emission_Sulfate(Emission):
    def __str__(self):
        return f'Sulfate {super().__str__()}'

    def get_name_of_material(self):
        return 'sulfate'

class Emission_WaterVapor(Emission):
    def __str__(self):
        return f'Water vapor {super().__str__()}'

    def get_name_of_material(self):
        return 'watervapor'
