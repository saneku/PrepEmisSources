import numpy as np
from .base import VerticalProfileDistribution

class UniformProfile(VerticalProfileDistribution):
    def generate_profile(self, height_levels):
        return np.ones(height_levels) / height_levels

class SuzukiProfile(VerticalProfileDistribution):
    def generate_profile(self, height_levels):
        return np.exp(-np.linspace(0, 1, height_levels))

class InvertedProfile(VerticalProfileDistribution):
    def generate_profile(self, height_levels):
        return np.flip(np.linspace(0, 1, height_levels))
