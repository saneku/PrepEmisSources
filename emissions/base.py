from abc import ABC, abstractmethod

class EmissionDistribution(ABC):
    def __init__(self, mean, stddev, location, amount, duration, start_time, size=1000):
        self.mean = mean
        self.stddev = stddev
        self.location = location
        self.amount = amount
        self.duration = duration
        self.start_time = start_time
        self.size = size

    @abstractmethod
    def generate_distribution(self):
        pass
