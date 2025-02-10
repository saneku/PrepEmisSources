#from abc import ABC, abstractmethod

class Emission():
    def __init__(self, mass_mt,lat,lon):
        self.mass_Mt = mass_mt
        self.lat = lat
        self.lon = lon

    #@abstractmethod
    #def generate_distribution(self):
    #    pass


#todo: add 2nd constructor with 10 mass fractions
class Emission_Ash(Emission):
    def __init__(self, mass_mt,lat,lon,mean,stddev):
        super().__init__(mass_mt,lat,lon)
        self.mean = mean
        self.stddev = stddev
    
    #def generate_distribution(self):
    #    return np.random.normal(self.mean, self.stddev, self.size)

class Emission_SO2(Emission):
    pass
    #def __init__(self, mass_mt,lat,long):
    #    super().__init__(mass_mt,lat,lon)
    
    #def generate_distribution(self):
    #    return np.random.lognormal(np.log(self.mean), self.stddev, self.size)

class Emission_Sulfate(Emission):
    pass
    #def generate_distribution(self):
    #    return np.random.gamma(shape=self.mean, scale=self.stddev, size=self.size)

class Emission_WaterVapor(Emission):
    pass
    #def generate_distribution(self):
    #    return np.random.uniform(self.mean - self.stddev, self.mean + self.stddev, self.size)