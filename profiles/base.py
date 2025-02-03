from abc import ABC, abstractmethod

class VerticalProfileDistribution(ABC):
    @abstractmethod
    def generate_profile(self, height_levels):
        pass
