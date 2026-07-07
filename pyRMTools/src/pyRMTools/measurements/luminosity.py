from .base import Measurement, MeasurementCollection
from ..constants import REFERENCE_COSMOLOGY
from ..utils.utility import reference_finder, convert_luminosity

class Luminosity(Measurement):

    def __init__(self, entry, parent = None):
        super().__init__(entry, parent)

    @property
    def error(self):
        return self.entry.get('error')
    
    @property
    def cosmology(self):
        return REFERENCE_COSMOLOGY[reference_finder(self.source)]
    
    def lag(self, line):
        return self.parent.lags(line).match(self)
    
    def convert(self, new_cosmology):
        new_luminosity = convert_luminosity(self.parent.redshift.value, self.cosmology, new_cosmology, self.value, self.error)

        new_measurement = self
        new_measurement.value = new_luminosity[0]
        if new_luminosity[1] is not None:
            new_measurement.entry['error'] = new_luminosity[1]
        new_measurement.entry['cosmology'] = new_cosmology

        return new_measurement
    
class LuminosityCollection(MeasurementCollection):
    measurement_class = Luminosity