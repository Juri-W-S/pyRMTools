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
    
class MeasurementCollection:

    measurement_class = Measurement

    def __init__(self, entries, parent=None):
        self.parent = parent
        #self.measurements = [self.measurement_class(e, parent = parent) for e in entries]
        self.measurements = []

        for e in entries:

            if isinstance(e, Measurement):
                self.measurements.append(e)
            else:
                self.measurements.append(
                    self.measurement_class(e, parent=parent)
                )

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