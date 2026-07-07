from .base import Measurement, MeasurementCollection

class LineWidth(Measurement):

    def __init__(self, entry, parent = None):
        super().__init__(entry, parent)
    @property
    def error(self):
        return self.entry.get('error')
    
class LineWidthCollection(MeasurementCollection):
    measurement_class = LineWidth