# pyRMTools
---
## Contents
---







## API Reference
---
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
