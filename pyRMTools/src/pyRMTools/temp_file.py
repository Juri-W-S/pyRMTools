import json
from pymongo import MongoClient
import numpy as np

REFERENCE_TO_LINK = {
    'Shen2024': 'https://iopscience.iop.org/article/10.3847/1538-4365/ad3936/pdf',
    'Kaspi2000': 'https://iopscience.iop.org/article/10.1086/308704/pdf',
    'Bentz2013': 'https://iopscience.iop.org/article/10.1088/0004-637X/767/2/149/pdf',
    'Peterson1998': 'https://iopscience.iop.org/article/10.1086/305813',
    'Grier2012': 'https://iopscience.iop.org/article/10.1088/0004-637X/755/1/60',
    'Santos-Lleo1997': 'https://iopscience.iop.org/article/10.1086/313046',
    'Denney2009': 'https://iopscience.iop.org/article/10.1088/0004-637X/702/2/1353',
    'Denney2010': 'https://iopscience.iop.org/article/10.1088/0004-637X/721/1/715#apj365393',
    'Bentz2009b': 'https://iopscience.iop.org/article/10.1088/0004-637X/705/1/199',
    'Stirpe1994': 'https://ui.adsabs.harvard.edu/abs/1994ApJ...425..609S/abstract',
    'Bentz2006a': 'https://iopscience.iop.org/article/10.1086/507417',
    'Denney2006': 'https://iopscience.iop.org/article/10.1086/508533',
    'Winge1996': 'https://ui.adsabs.harvard.edu/abs/1996ApJ...469..648W/abstract',
    'Santos-Lleo2001': 'https://www.aanda.org/articles/aa/abs/2001/13/aa9537/aa9537.html',
    'Peterson2002': 'https://iopscience.iop.org/article/10.1086/344197',
    'Bentz2007': 'https://iopscience.iop.org/article/10.1086/516724',
    'Dietrich1998': 'https://iopscience.iop.org/article/10.1086/313085',
    'Dietrich2012': 'https://iopscience.iop.org/article/10.1088/0004-637X/757/1/53',
    'Peterson2014': 'https://ui.adsabs.harvard.edu/abs/2014ApJ...795..149P/abstract',
    'Kaspi2021': 'https://iopscience.iop.org/article/10.3847/1538-4357/ac00aa/pdf',
    'Lira2018': 'https://iopscience.iop.org/article/10.3847/1538-4357/aada45/pdf',
    'McDougall2025': 'https://arxiv.org/pdf/2512.01261',
    'Hoormann2019': 'https://ui.adsabs.harvard.edu/abs/2019MNRAS.487.3650H/abstract',
    'Peterson2005': 'https://iopscience.iop.org/article/10.1086/444494/pdf',
    'Metzroth2006': 'https://iopscience.iop.org/article/10.1086/505525/pdf',
    'De Rosa2015': 'https://iopscience.iop.org/article/10.1088/0004-637X/806/1/128/pdf',
    'Penton2025': 'https://arxiv.org/pdf/2512.01260',
    'Hu2025': 'https://iopscience.iop.org/article/10.3847/1538-4365/add40b/pdf',
    'Woo2024': 'https://iopscience.iop.org/article/10.3847/1538-4357/ad132f/pdf',
    'Hu2021': 'https://iopscience.iop.org/article/10.3847/1538-4365/abd774/pdf',
    'Bai2025': 'https://arxiv.org/pdf/2512.08192',
    'Grier2017': 'https://iopscience.iop.org/article/10.3847/1538-4357/aa98dc/pdf'
}
LINK_TO_REFERENCE = {v: k for k, v in REFERENCE_TO_LINK.items()}

def reference_finder(link: str):
    return LINK_TO_REFERENCE.get(link)

def link_finder(reference: str):
    return REFERENCE_TO_LINK.get(reference)


def _parse_linewidth_type(note: str | None):

    if note is None:
        return None

    note = note.lower()

    if 'line dispersion' in note:
        return 'line dispersion'

    if 'fwhm' in note:
        return 'FWHM'

    return None

def combine_quantity(quantity, error_plus, error_minus, method):
    if method == 'weighted_mean':
        quantity = np.array(quantity)
        weights = np.zeros_like(error_plus)
        for i in range(len(error_plus)):
            err = 0.5 * (error_plus[i] + error_minus[i])
            weights[i] = 1/(err**2)
        mean = np.sum(quantity * weights) / np.sum(weights)
        error = np.sqrt(1 / np.sum(weights))
        return mean, error
    if method == 'envelope':
        lowest = min(np.array(quantity) - np.array(error_minus))
        highest = max(np.array(quantity) + np.array(error_plus))
        value = 0.5 * (lowest+highest)
        error = 0.5 * (highest-lowest)
        return value, error

class Database:

    @classmethod
    def from_mongodb(cls, url='mongodb://localhost:27017', database = 'quasar_db', collection='objects'):
        client = MongoClient(url)
        db = client[database]
        data = list(db[collection].find({}))

        return cls(data)
    @classmethod
    def from_json(cls, filename):
        with open(filename) as f:
            data = json.load(f)
        return cls(data)
    def __init__(self, data):

        self.data = data
        self.objects = {}
        self.agns = []

        for obj in data:
            agn = AGN(obj)
            self.agns.append(agn)

            for name in obj['names']:
                self.objects[name] = agn
    def __iter__(self):
        return iter(self.agns)
    def get(self, name):
        return self.objects[name]
    
    def publication_view(self, source):
        return PublicationReferenceView(self, source)
    

class AGN:

    def __init__(self, data):
        self.data = data

    @property
    def name(self):
        return self.data['names']

    def lags(self, line):
        entries = [
        {**entry, "_match_index": i}
        for i, entry in enumerate(
            self.data
            .get("properties", {})
            .get("lags", {})
            .get(line, []))]


        return LagCollection(entries, parent = self)
    
    def linewidth(self, line, type, spec_type):

        entries = self.data['properties']['line widths'][line][type].get(spec_type, [])

        return LineWidthCollection(entries, parent = self)

    def mass(self, line):

        entries = self.data.get('properties', {}).get('mass', {}).get('RM', {}).get(line, [])

        return MassCollection(entries, parent = self)
    
    def vp(self, line):

        entries = self.data.get('properties', {}).get('virial product', {}).get(line, [])

        return VPCollection(entries, parent = self)
    
    @property
    def redshift(self):
        return self.data['properties'].get('redshift', [])[0]

    @property
    def ra(self):
        return self.data['properties'].get('ra', [])[0]

    @property
    def dec(self):
        return self.data['properties'].get('dec', [])[0]
    
    @property
    def position(self):
        ra = self.ra
        dec = self.dec

        return [ra['value'], dec['value']]


    def luminosity(self, wavelength):

        source_dict = self.data['properties'].get(f'L{wavelength}', {})

        measurements = []

        for _, entries in source_dict.items():

            for i, entry in enumerate(entries):

                entry = entry.copy()
                entry['_match_index'] = i

                measurements.append(entry)
        return LuminosityCollection(measurements, parent=self)
    
    def distance(self, measure):

        entries = self.data.get('properties', {}).get('distance').get(measure, [])

        return DistanceCollection(entries, parent = self)


class PublicationReferenceView:

    def __init__(self, database, source):
        self.db = database
        self.source = source

        self._index = self._build_index()


    def _build_index(self):
        index = {}

        for agn in self.db:
            measurements = self._collect_measurements(agn)

            if any(measurements.values()):
                index[agn] = measurements
        return index

    def _collect_measurements(self, agn):

        result = {
            "lags": {},
            "linewidths": {},
            "masses": {},
            "vp": {},
            "luminosities": {},
            'distances': {}
        }

        for line in agn.data.get("properties", {}).get("lags", {}):

            m = agn.lags(line).filter(source=self.source)

            if len(m):
                result["lags"][line] = m.measurements

        lw = agn.data.get('properties', {}).get('line widths', {})
        displayed_lw = ['H_alpha', 'H_beta', 'H_gamma', 'mg2', 'c4']
        for line in displayed_lw:
            if line in lw:
                measurements = []
                for width_type in lw[line]:
                    for spec_type in lw[line][width_type]:
                        measurements.extend(
                            agn.linewidth(line, width_type , spec_type)
                            .filter(source=self.source)
                            .measurements
                        )
                if measurements:
                    result['linewidths'][line] = measurements

        for line in agn.data.get("properties", {}).get("mass", {}).get("RM", {}):

            m = agn.mass(line).filter(source=self.source)

            if len(m):
                result["masses"][line] = m.measurements

        for line in agn.data.get("properties", {}).get("virial product", {}):

            m = agn.vp(line).filter(source=self.source)

            if len(m):
                result["vp"][line] = m.measurements

        for key in agn.data.get("properties", {}):

            if key.startswith("L"):

                wavelength = key[1:]

                m = agn.luminosity(wavelength).filter(source=self.source)

                if len(m):
                    result["luminosities"][wavelength] = m.measurements

        for dsc_measure in agn.data.get('properties', {}).get('distance', {}):
            m = agn.distance(dsc_measure).filter(source=self.source)

            if len(m):
                result['distance'][dsc_measure] = m.measurements


        return result

    def agns(self):
        return list(self._index.keys())

    def measurements_by_agn(self, agn):
        if isinstance(agn, str):
            agn = self.db.get(agn)

        return self._index.get(agn, {})

    def all_measurements(self):
        all_m = []
        for m in self._index.values():
            for group in m.values():
                all_m.extend(group)
        return all_m

    def count(self):
        return len(self.all_measurements())

class Measurement:
    
    def __init__(self, entry, parent = None):
        self.entry = entry
        self.value = entry['value']
        self.unit = entry['unit']
        self.source = entry.get('source')
        self.problematic = entry['problematic']
        self.parent = parent
        self._match_index = entry.get('_match_index')


    @property
    def main_reference(self):
        return self.entry.get('main reference')
    @property
    def note(self):
        return self.entry.get('note')
    @property
    def name(self):
        return self.parent.name
    
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
    
class LineWidth(Measurement):

    def __init__(self, entry, parent = None):
        super().__init__(entry, parent)
    @property
    def error(self):
        return self.entry.get('error')


class Redshift(Measurement):
    
    def __init__(self, entry, parent = None):
        super().__init__(entry, parent)

class RA(Measurement):

    def __init__(self, entry, parent = None):
        super().__init__(entry, parent)

class DEC(Measurement):

    def __init__(self, entry, parent = None):
        super().__init__(entry, parent)   

class Luminosity(Measurement):

    def __init__(self, entry, parent = None):
        super().__init__(entry, parent)

    @property
    def error(self):
        return self.entry.get('error')
    
    def lag(self, line):
        return self.parent.lags(line).match(self)
    
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
        return _parse_linewidth_type(self.entry.get('note'))
    
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
        return _parse_linewidth_type(self.entry.get('note'))
    
class Distance(Measurement):

    def __init__(self, entry, parent = None):
        super().__init__(entry, parent)

    @property
    def error(self):
        return self.entry.get('error')
    
class CombinedMass:

    def __init__(self, value, error, measurements):

        self.value = value
        self.error = error
        self.measurements = measurements

class CombinedVP:

    def __init__(self, value, error, measurements):

        self.value = value
        self.error = error
        self.measurements = measurements

class MeasurementCollection:

    measurement_class = Measurement

    def __init__(self, entries, parent=None):
        self.parent = parent
        self.measurements = [self.measurement_class(e, parent = parent) for e in entries]

    def __iter__(self):
        return iter(self.measurements)
    
    def __len__(self):
        return len(self.measurements)
    
    def filter(self, **kwargs):
        result = self.measurements
        for key, value in kwargs.items():
            result = [m for m in result if getattr(m, key) == value]
        new = self.__class__([], parent = self.parent)
        new.measurements = result
        return new
    
    def from_main_reference(self, ref):

        for m in self.measurements:
            if m.main_reference == ref:
                return m
        return None
    
    def match(self, measurement):
        if measurement.main_reference is not None:
            candidates = [m for m in self.measurements if m.main_reference == measurement.main_reference]
            if len(candidates) == 1:
                return candidates[0]
            if measurement._match_index is not None:
                for m in candidates:
                    if m._match_index == measurement._match_index:
                        return m
        candidates = [m for m in self.measurements if m.source == measurement.source]

        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) == 0:
            return None
        raise ValueError('Multiple matching measurements found.')
    
class LagCollection(MeasurementCollection):
    measurement_class = Lag

class LineWidthCollection(MeasurementCollection):
    measurement_class = LineWidth

class RedshiftCollection(MeasurementCollection):
    measurement_class = Redshift

class RACollection(MeasurementCollection):
    measurement_class = RA

class DECCollection(MeasurementCollection):
    measurement_class = DEC

class LuminosityCollection(MeasurementCollection):
    measurement_class = Luminosity

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
    
class DistanceCollection(MeasurementCollection):

    measurement_class = Distance