from .measurements.lag import Lag, LagCollection
from .measurements.linewidth import LineWidth, LineWidthCollection
from .measurements.distance import Distance, DistanceCollection
from .measurements.luminosity import Luminosity, LuminosityCollection
from .measurements.mass import Mass, MassCollection
from .measurements.vp import VP, VPCollection
from .measurements.redshift import Redshift, RedshiftCollection
from .measurements.position import RA, DEC, Position, RACollection, DECCollection, PositionCollection
from astropy.cosmology import Cosmology

class AGN:

    def __init__(self, data):
        self.data = data

    @property
    def name(self):
        return self.data['names']

    def lag(self, line):
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

        entries = self.data.get('properties', {}).get('redshift')

        return Redshift(entries[0], parent = self)

    @property
    def ra(self):

        entries = self.data.get('properties', {}).get('ra')

        return RA(entries[0], parent = self)

    @property
    def dec(self):

        entries = self.data.get('properties', {}).get('dec')

        return DEC(entries[0], parent = self)
    
    @property
    def position(self):

        entry = {'value': [self.ra.value, self.dec.value],
                 'unit': [self.ra.unit, self.dec.unit],
                 'source': [self.ra.source, self.dec.source],
                 'problematic': [self.ra.problematic, self.dec.problematic]}

        return Position(entry, parent = self)


    def luminosity(self, wavelength):

        source_dict = self.data['properties'].get(f'L{wavelength}', {})

        measurements = []

        for _, entries in source_dict.items():

            for i, entry in enumerate(entries):

                entry = entry.copy()
                entry['_match_index'] = i

                measurements.append(entry)
        return LuminosityCollection(measurements, parent=self)
    
    def distance(self, measure = None, cosmology: Cosmology | None = None):

        if cosmology is not None:
            #return cosmology.luminosity_distance(self.redshift.value)
            luminosity_distance = cosmology.luminosity_distance(self.redshift.value)
            entry = {'value': luminosity_distance.value,
                       'unit': str(luminosity_distance.unit),
                       'problematic': False}
            return Distance(entry, parent = self)
            
        else:
            entries = self.data.get('properties', {}).get('distance').get(measure, [])

        return DistanceCollection(entries, parent = self)
    