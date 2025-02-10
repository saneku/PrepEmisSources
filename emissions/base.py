#from abc import ABC, abstractmethod

class Emission():
    def __init__(self, mass_mt,lat,lon):
        self.mass_Mt = mass_mt
        self.lat = lat
        self.lon = lon

    def __str__(self):
        return f" Emission: {self.mass_Mt} Mt, lat: {self.lat}, lon: {self.lon}"
    #@abstractmethod
    #def generate_distribution(self):
    #    pass


#todo: add 2nd constructor with 10 mass fractions
class Emission_Ash(Emission):
    def __init__(self, mass_mt,lat,lon,mean,stddev):
        super().__init__(mass_mt,lat,lon)
        
        self.mean = mean
        self.stddev = stddev

    def __str__(self):
        return f'Ash mean={self.mean} stddev={self.stddev}. {super().__str__()}'
    #def generate_distribution(self):
    #    return np.random.normal(self.mean, self.stddev, self.size)

class Emission_SO2(Emission):
    def __str__(self):
        return f'SO2 {super().__str__()}'

    #def __init__(self, mass_mt,lat,long):
    #    super().__init__(mass_mt,lat,lon)
    
    #def generate_distribution(self):
    #    return np.random.lognormal(np.log(self.mean), self.stddev, self.size)

class Emission_Sulfate(Emission):
    def __str__(self):
        return f'Sulfate {super().__str__()}'

    #def generate_distribution(self):
    #    return np.random.gamma(shape=self.mean, scale=self.stddev, size=self.size)

class Emission_WaterVapor(Emission):
        def __str__(self):
            return f'Water vapor {super().__str__()}'

    #def generate_distribution(self):
    #    return np.random.uniform(self.mean - self.stddev, self.mean + self.stddev, self.size)