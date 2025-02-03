class Eruption:
    def __init__(self):
        self.emissions = []
        self.profiles = []

    def add_emission(self, emission):
        self.emissions.append(emission)

    def add_profile(self, profile):
        self.profiles.append(profile)
