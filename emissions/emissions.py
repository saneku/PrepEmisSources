from abc import ABC, abstractmethod

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

#todo: add 2nd constructor with 10 mass fractions
class Emission_Ash(Emission):
    def __init__(self, mass_mt,lat,lon,mean,stddev):
        self.mean = mean
        self.stddev = stddev
        super().__init__(mass_mt,lat,lon)

    def __str__(self):
        return f'Ash {super().__str__()}. Mean={self.mean} stddev={self.stddev}.'
    
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
