from .base import Measurement, MeasurementCollection

class RA(Measurement):

    def __init__(self, entry, parent = None):
        super().__init__(entry, parent)

class RACollection(MeasurementCollection):

    measurement_class = RA

class DEC(Measurement):

    def __init__(self, entry, parent = None):
        super().__init__(entry, parent)

class DECCollection(MeasurementCollection):

    measurement_class = RA

class Position(Measurement):

    def __init__(self, entry, parent = None):
        super().__init__(entry, parent)

class PositionCollection(MeasurementCollection):

    measurement_class = Position