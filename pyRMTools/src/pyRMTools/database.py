from importlib.resources import files
import json
from pymongo import MongoClient
from .agn import AGN
from .publication_view.publication_view import PublicationView
from .measurements.lag import LagCollection
from .measurements.linewidth import LineWidthCollection
from .measurements.luminosity import LuminosityCollection
from .measurements.mass import MassCollection
from .measurements.vp import VPCollection

default_database = files("pyRMTools.data") / "quasar_db.objects.json"

class Database:

    @classmethod

    def from_mongodb(cls, url='mongodb://localhost:27017', database = 'quasar_db', collection='objects'):
        client = MongoClient(url)
        db = client[database]
        data = list(db[collection].find({}))

        return cls(data)
    @classmethod
    def from_json(cls, filename = None):

        if filename is None:
            filename = files("pyRMTools.data") / "quasar_db.objects.json"
            
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
    
    def lag(self, line):

        measurements = []

        for agn in self:
            #measurements.extend([lag.entry for lag in agn.lag(line)])
            measurements.extend(agn.lag(line))
        return LagCollection(measurements)
    
    def linewidth(self, line, type, spec_type):

        measurements = []

        for agn in self:
            measurements.extend(agn.linewidth(line, type, spec_type))
        return LineWidthCollection(measurements)
    
    def mass(self, line):

        measurements = []
        
        for agn in self:
            measurements.extend(agn.mass(line))
        return MassCollection(measurements)
    
    def vp(self, line):

        measurements = []
        
        for agn in self:
            measurements.extend(agn.vp(line))
        return VPCollection(measurements)
    
    def luminosity(self, wavelength):

        measurements = []

        for agn in self:
            measurements.extend(agn.luminosity(wavelength))
        return LuminosityCollection(measurements)
    
    def publication_view(self, source):
        return PublicationView(self, source)
