from .base import Measurement, MeasurementCollection

class Redshift(Measurement):

    def __init__(self, entry, parent = None):
        super().__init__(entry, parent)

class RedshiftCollection(MeasurementCollection):

    measurement_class = Redshift