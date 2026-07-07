from .base import Measurement, MeasurementCollection

class Distance(Measurement):

    def __init__(self, entry, parent = None):
        super().__init__(entry, parent)

    @property
    def error(self):
        return self.entry.get('error')

class DistanceCollection(MeasurementCollection):

    measurement_class = Distance