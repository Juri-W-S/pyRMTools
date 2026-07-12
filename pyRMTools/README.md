# pyRMTools
---
## Contents
---







## API Reference

### Database
The `Database` class is the entry point to the reverberation mapping database.

**Constructors**

    import pyRMTools as qrm

    db = qrm.Database.from_json()

Load the bundled JSON database.

    db = qrm.Database.from_mongodb(
             url='mongodb://localhost:27017', 
             database = 'quasar_db', 
             collection='objects'
             )
Load the database from a MongoDB instance.

**Methods**
`get(name)`

Return the corresponding `AGN`.

    agn = db.get('NGC 5548')
    
---

`publication_view(source)` 

Return a `PublicationView` containing all measurements originating from a publication.

    view = db.publication_view(qrm.link_finder('Bentz2013'))
    
---

`lag(line)`

Return a `LagCollection` containing all lag measurements of a given emission line.

    lags = db.lag('H_beta')
    
---

`luminosity(wavelength)`

Return a `LuminosityCollection` for all continuum luminosity measurements with wavelength in Angström.

    L = db.luminosity(5100)
    
---

`linewidth(line, linewidth_type, spectrum_type)`

Return a `LineWidthCollection`.

    widths = db.linewidth(
                'H_beta',
                'FWHM',
                'rms'
                )
supported keywords are `FWHM` or `line dispersion` and `rms` or `mean`.

---

`mass(line)`

Return a `MassCollection`.

    masses = db.mass('H_beta')
    
---

`vp(line)`


Return a `VPCollection`.

    vps = db.vp('c4')
    
---

### AGN

The `AGN` class represents a single object in the database.

| Property   | Description     |
| ---------- | --------------- |
| `name`     | List of Object aliases  |
| `ra`       | `Measurement`: Right ascension  |
| `dec`      | `Measurement`: Declination     |
| `position` | `Measurement`: `(ra, dec)`     |
| `redshift` | `Measurement`: Redshift        |

---

**Methods**

`lag(line)`

Return a `LagCollection` containing all lag measurements of a given emission line.

    lags = agn.lag('H_beta')
    
---

`luminosity(wavelength)`

Return a `LuminosityCollection` for all continuum luminosity measurements with wavelength in Angström.

    L = agn.luminosity(5100)
    
---

`linewidth(line, linewidth_type, spectrum_type)`

Return a `LineWidthCollection`.

    widths = agn.linewidth(
                'H_beta',
                'FWHM',
                'rms'
                )
supported keywords are `FWHM` or `line dispersion` and `rms` or `mean`.

---

`mass(line)`

Return a `MassCollection`.

    masses = agn.mass('H_beta')
    
---

`vp(line)`


Return a `VPCollection`.

    vps = agn.vp('c4')
    
---

`distance(method=None, *cosmology)`

Return a `DistanceCollection` if method is not None, or return the luminosity distance based on `astropy.cosmology` model if *Cosmology is passed.

    distance = agn.distance('group-averaged distance')

or

    from astropy.cosmoloy import LambdaCDM
    import astropy.units as u

    new_cosmology = LambdaCDM(H0 = 67 * u.km / u.s / u.Mpc, Om0 = 0.32, Ode0 = 0.68)
    
    agn.distance(cosmology = new_cosmology)

supported arguments for `method` are 'luminosity distance', 'group-averaged distance', 'tully-fisher distance'.

---

### MeasurementCollection

Container storing multiple measurements. Individual `Measurement` classes which contain the values are accessed
by iteration.

    for measurement in agn.MeasurementCollection():
        print(measurement.property)

---

**Methods**

`filter(**kwargs)`

Filter measurements based on `Measurement` properties. Returns a `MeasurementCollection`.

        lags = agn.lag('mg2').filter(
                            source = qrm.link_finder('Bai2025'),
                            problematic = False
                            )

---

`match(measurement)`

Return the corresponding measurement from another collection. Returns a `Measurement`.

        lags = agn.lag('H_beta')
        for lag in lags:
                L = agn.luminosity(5100).match(lag)

Supports shortcuts between matching luminosities and lags.

        for lag in lags:
            L = lag.luminosity(5100)

        for lum in luminosities:
            lag = lum.lag('H_beta')

---

**MassCollection**

`combine(*spectra_type, *linewidth_type)`

Combine multiple mass estimates to one and allows to select only specific spectra and linewidth types to combine the mass.

        mass = agn.mass("H_beta").combine(
                spectra_type="rms",
                linewidth_type="FWHM",
                )

Returns `CombinedMass` class which is a special `Measurement` class, supporting

        mass.value
        mass.error
        mass.measurements

where the latter contains a `MeasurementCollection` from the masses used for the combination.

---

**VPCollection**

`combine(*spectra_type, *linewidth_type)`

Analogous to `MassCollection.combine()` and returns the analog `CombinedVP` class.

---

### Measurement

All measurement classes inherit from `Measurement`. The measurements mostly have to be accessed through
`MeasurementCollection` and have to be iterated through, see `MeasurementCollection`.

**Common properties depending on availability**

| Property         | Description                       |
| ---------------- | --------------------------------- |
| `value`          | Measured value                    |
| `unit`           | Physical unit                     |
| `source`         | Publication                       |
| `main_reference` | Original publication if available |
| `problematic`    | Quality flag                      |
| `note`           | Additional notes                  |
| `parent`         | Parent `AGN`                      |
| `name`           | Object aliases                    |
| `entry`          | Entry dictionary of the database  |

---
**Lag**

| Property      |    Description    |
| ------------- |-------------------|
| `error_plus`  |Upper error of the value |
| `error_minus` |Lower error of the value  |
| `baseline`    |Baseline of the RM observation |
| `cadence`     |Cadence of the RM observation |
| `epochs`      |Epochs of the RM observation |
| `snr`         |Estimated signal to noise ratio of the RM observation |
| `grade`       |Internally assigned lag quality grade of RM publication | 
| `method`      |Employed lag recovery algorithm |

**Methods**

    lag.luminosity(5100)

Return the matching luminosity measurement from the same publication.

---

**Luminosity**

| Property    |    Description    |
| ----------- |-------------------|
| `error`     | Error of the measurement|
| `cosmology` | `astropy.cosmology` of the publications assumed cosmology model|

**Methods**

    luminosity.convert(new_cosmology)

Convert the luminosity to another cosmology model. Argument needs to be part of `astropy.cosmology` module.

    luminosity.lag(line)

Return the matching lag measurement from the same publication.

---

**LineWidth**

| Property    |    Description    |
| ----------- |-------------------|
| `error`     | Error of the measurement|

---

**Mass**

| Property              |    Description    |
| --------------------- |-------------------|
| `error_plus`          |Upper error of the value |
| `error_minus`         |Lower error of the value |
| `virial_factor`       |Assumed virial factor to calculate the mass|
| `virial_factor_error` |Error of the assumed virial factor|
| `spectrum_type`       |Type of spectrum used to get the value|
| `linewidth_type`      |Type of linewidth measurement used to get the value|

---

**Virial Product**

| Property              |    Description    |
| --------------------- |-------------------|
| `error_plus`          |Upper error of the value |
| `error_minus`         |Lower error of the value |
| `spectrum_type`       |Type of spectrum used to get the value|
| `linewidth_type`      |Type of linewidth measurement used to get the value|

---

**Distance**

| Property    |    Description    |
| ----------- |-------------------|
| `error`     | Error of the measurement|

---

### PublicationView

Convenience interface for retrieving all measurements from a publication centered view, instead of AGN centered view.

    view = db.publication_view(qrm.link_finder('Bentz2013')

**Methods**

    view.agns()

List containing all `AGN` with measurements from the publication.

    view.measurements_by_agn(agn.name)

Return all meeasurements from the publication for one AGN.

    view.all_measurements()

Return every measurement contained in the publication.

    view.count()

Return the total number of measurements from the publication.

---

### Simulation

`scout(luminosity, z, baseline, cadence, sn, *relation, *alpha, *beta)`

    result = qrm.scout(1e44, 0.02, 400, 2, 120)

Simulation framework of RM campaigns. Returns `ScoutResult`.

---

### ScoutResult

Stores the outcome of a simulated RM campaign.

**Result properties**

    result.luminosity

Returns the input luminosity.

    result.z

Returns the input redshift.

    result.expected_lag

Returns the expected lag of the object in the rest-frame.

    result.recovered_lags

Returns the list of ICCF recovered lags.

    result.iccf_results

Returns the list of ICCF correlation results.

    result.parameters

Returns a dictionary with the simulation parameters.

    result.lag

Returns the median of recovered lags

    result.error_plus

Returns the 84th percentile of the recovered lags minus the median lag.

    result.error_minus

Returns the median lag minus the 16th percentile of the recovered lags.

    result.bias

Returns the bias defined as the fraction of recovered lag and expected lag minus 1.

    result.bias_distribution

Returns the distribution of recovered bias.

    result.outlier_fraction

Returns the fraction of lags that deviate stronger than 0.5 of the absolute bias.

    result.success

Returns the percentage of recovered lags compared to simulated lags.

---

**Plotting**

    result.plot.view()

Overview panel.

    result.plot.lightcurve()

Example simulated light curve.

    result.plot.ccf(*index)

Interpolated cross-correlation function for the 1000 light curves. No index given stacks all 1000 over each other.

    result.plot.histogram()

Recovered lag bias histogram.

    result.plot.rl_plane()

Position in the R-L plane.

---

### Config

The package allows some customization regarding the simulation.

        qrm.config.peakcent[key]

allows to modify the ICCF centroid calculation parameters. Default values are:

        peakcent = {'thres': 0.8,
                    'sigmode': 0.2,
                    'siglevel' :0.95, 
                    'imode': 0}


        qrm.config.xcor[key]

allows to modify the `imode` which is set to 0 per default. Please refer to the pyCCF package for information on this setting.


        qrm.config.scout[key]

allows to modify the ICCF lag search grid and the amount of simulated light curves N by .scout(). Default values are:

        scout = {'tlag_min_factor': -0.3,
                 'tlag_max_factor':0.5,
                 'tunit_factor': 0.8,
                 'N': 1000}

Note that is only possible to modify the factors on the lag grid. This means, that the min and max search range is still dependent on the baseline and the step size on the cadence. Setting a custom value independent on the observational parameters is not possible.
