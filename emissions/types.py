import numpy as np
from .base import Emission

'''
class Emission_Ash(Emission):
    def generate_distribution(self):
        return np.random.normal(self.mean, self.stddev, self.size)

class Emission_SO2(Emission):
    def generate_distribution(self):
        return np.random.lognormal(np.log(self.mean), self.stddev, self.size)

class Emission_Sulfate(Emission):
    def generate_distribution(self):
        return np.random.gamma(shape=self.mean, scale=self.stddev, size=self.size)

class Emission_WaterVapor(Emission):
    def generate_distribution(self):
        return np.random.uniform(self.mean - self.stddev, self.mean + self.stddev, self.size)
'''
