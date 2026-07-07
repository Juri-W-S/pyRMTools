from .base import Measurement, MeasurementCollection
from ..utils.utility import parse_linewidth_type, combine_quantity

class Mass(Measurement):

    def __init__(self, entry, parent = None):
        super().__init__(entry, parent)
        self.error_plus = entry['error +']
        self.error_minus = entry['error -']

    @property
    def virial_factor(self):
        return self.entry.get('virial factor f')
    @property
    def virial_factor_error(self):
        return self.entry.get('error of f')
    @property
    def spectrum_type(self):
        return self.entry.get('spectra type')
    @property
    def linewidth_type(self):
        return parse_linewidth_type(self.entry.get('note'))
    
class CombinedMass:

    def __init__(self, value, error, measurements):

        self.value = value
        self.error = error
        self.measurements = measurements

class MassCollection(MeasurementCollection):

    measurement_class = Mass

    def combine(self, spectra_type=None, linewidth_type=None, method='envelope'):

        masses = self.measurements

        if spectra_type is not None:
            masses = [m for m in masses
                      if m.spectrum_type == spectra_type]

        if linewidth_type is not None:
            masses = [m for m in masses
                      if m.linewidth_type == linewidth_type]

        if len(masses) == 0:
            return None

        values = [m.value for m in masses]
        err_plus = [m.error_plus for m in masses]
        err_minus = [m.error_minus for m in masses]

        value, error = combine_quantity(values, err_plus, err_minus, method=method)

        return CombinedMass(value, error, masses)