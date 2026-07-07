from .base import Measurement, MeasurementCollection
from ..utils.utility import parse_linewidth_type, combine_quantity

class VP(Measurement):

    def __init__(self, entry, parent =  None):
        super().__init__(entry, parent)
        self.error_plus = entry['error +']
        self.error_minus = entry['error -']

    @property
    def spectrum_type(self):
        return self.entry.get('spectra type')
    @property
    def linewidth_type(self):
        return parse_linewidth_type(self.entry.get('note'))
    
class CombinedVP:

    def __init__(self, value, error, measurements):

        self.value = value
        self.error = error
        self.measurements = measurements

class VPCollection(MeasurementCollection):

    measurement_class = VP

    def combine(self, spectra_type=None, linewidth_type=None, method='envelope'):

        vp = self.measurements

        if spectra_type is not None:
            vp = [m for m in vp
                      if m.spectrum_type == spectra_type]

        if linewidth_type is not None:
            vp = [m for m in vp
                      if m.linewidth_type == linewidth_type]

        if len(vp) == 0:
            return None

        if len(vp) == 1:
            return vp[0]

        values = [m.value for m in vp]
        err_plus = [m.error_plus for m in vp]
        err_minus = [m.error_minus for m in vp]

        value, error = combine_quantity(values, err_plus, err_minus, method=method)

        return CombinedVP(value, error, vp)