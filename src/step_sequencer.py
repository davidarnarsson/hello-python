class Track:
    
    def __init__(self, generator):
        self.generator = generator
        self.markers = []

    def sample_at(self, step, t): 
      if not self.markers[step]:
        return 0
      
      return self.generator(t)

class StepSequencer:
    self.tracks = []
    
    def __init__(self, steps):
        self.steps = steps

    def add(self, track):
        self.tracks.add(track)

    