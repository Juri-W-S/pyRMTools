from .base import Measurement, MeasurementCollection

class Lag(Measurement):

    def __init__(self, entry, parent = None):
        super().__init__(entry, parent)

        self.error_plus = entry['error +']
        self.error_minus = entry['error -']

    @property
    def grade(self):
        return self.entry.get('grade')
    @property
    def method(self):
        return self.entry.get('method')
    @property
    def baseline(self):
        return self.entry.get('baseline')
    @property
    def cadence(self):
        return self.entry.get('cadence')
    @property
    def epochs(self):
        return self.entry.get('epochs')
    @property
    def snr(self):
        return self.entry.get('est S/N')
    
    def luminosity(self, wavelength):
        return self.parent.luminosity(wavelength).match(self)
    
class LagCollection(MeasurementCollection):
    measurement_class = Lag