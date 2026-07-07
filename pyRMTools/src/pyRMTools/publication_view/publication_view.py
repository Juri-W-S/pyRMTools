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

            m = agn.lag(line).filter(source=self.source)

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
