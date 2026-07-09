import numpy as np
from .plotting import ScoutPlotter

class ScoutResult:

    def __init__(self,*,luminosity,z,expected_lag,recovered_lags,iccf_results,light_curves, parameters):

        self.luminosity = luminosity
        self.z = z
        self.expected_lag = expected_lag

        self.recovered_lags = recovered_lags
        self.iccf_results = iccf_results
        self.light_curves = light_curves

        self.parameters = parameters

        self.plot = ScoutPlotter(self)

    @property
    def lag(self):
        return np.median(self.recovered_lags)
    @property
    def error_plus(self):
        return np.percentile(self.recovered_lags,84)-self.lag
    @property
    def error_minus(self):
        return self.lag-np.percentile(self.recovered_lags,16)

    @property
    def bias(self):
        return self.lag / self.expected_lag - 1

    @property
    def bias_distribution(self):
        return np.array(self.recovered_lags)/self.expected_lag - 1

    @property
    def outlier_fraction(self):
        b = np.abs(self.bias_distribution)
        return np.mean(b > 0.5)
    @property
    def success(self):
        return len(self.recovered_lags) / self.parameters['N'] * 100
    
class ICCFResult:

    def __init__(self,lag,r,centroid,peak,success):

        self.lag = lag
        self.r = r
        self.centroid = centroid
        self.peak = peak
        self.success = success

class LightCurve:

    def __init__(self,t,continuum,line,continuum_error,line_error):

        self.t = t
        self.continuum = continuum
        self.line = line

        self.continuum_error = continuum_error
        self.line_error = line_error
