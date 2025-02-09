import numpy as np
from .base import VerticalProfile

class VerticalProfile_Uniform(VerticalProfile):
    def generate_profile(self, height_levels):
        return np.ones(height_levels) / height_levels

class VerticalProfile_Suzuki(VerticalProfile):
    def generate_profile(self, height_levels):
        return np.exp(-np.linspace(0, 1, height_levels))

class VerticalProfile_Simple(VerticalProfile):
    def generate_profile(self, height_levels):
        return np.flip(np.linspace(0, 1, height_levels))
