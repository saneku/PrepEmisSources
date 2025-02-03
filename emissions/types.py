import numpy as np
from .base import EmissionDistribution

class AshEmission(EmissionDistribution):
    def generate_distribution(self):
        return np.random.normal(self.mean, self.stddev, self.size)

class SO2Emission(EmissionDistribution):
    def generate_distribution(self):
        return np.random.lognormal(np.log(self.mean), self.stddev, self.size)

class SulfateEmission(EmissionDistribution):
    def generate_distribution(self):
        return np.random.gamma(shape=self.mean, scale=self.stddev, size=self.size)

class WaterVaporEmission(EmissionDistribution):
    def generate_distribution(self):
        return np.random.uniform(self.mean - self.stddev, self.mean + self.stddev, self.size)
