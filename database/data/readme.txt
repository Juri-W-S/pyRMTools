General notes:

Luminosity measurements where the value was given in logarithmic units have the higher error threshold in the database instead of asymetric ones. E.g. McDougall2025
error is calculated as 10^(43.31+0.01) - 10^(43.31). So in some cases, e.g. Bentz2013 the error is exaggerated towards the lower end.
Bai2026 is refered to Bai2025 because the data was put into the database before it was published in 2026



About the sources and their assumptions:

Shen2024: DB source link: https://iopscience.iop.org/article/10.3847/1538-4365/ad3936/pdf
	Assumptions:	Flat LCDM, O_L = 0.7, O_M = 0.3, H0 = 70km/s/Mpc
			flux limited sample to i_psf = 21,7
			prepspec used to combine photometrics for light curves from diff. facilities
			L5100 is host corrected using estim. fraction from 2014 spectroscopy

Kaspi2000: DB source link: https://iopscience.iop.org/article/10.1086/308704/pdf

	Assumptions:	No host correction was done for the luminosities
			f = sqrt(3)/2
			Kepler motion of Gas
			galactic extingstion done
			no cosmological constant, q0 = 0.5, H0 = 75km/s/Mpc

Bentz2013: DB source link: https://iopscience.iop.org/article/10.1088/0004-637X/767/2/149/pdf

	Assumptions:	LCDM with H0 = 72km/s/Mpc, O_L = 0.7, O_M = 0.3
			Most AGN Distances measured through redshift
			important notes on individual objects!

Peterson1998: DB source link: https://iopscience.iop.org/article/10.1086/305813

	Assumptions:	See Bentz2013 for the corrections of the measuerements

Santos-Lleo1997: DB source link: https://iopscience.iop.org/article/10.1086/313046

	Assumptions:	See Bentz2013 for the corrections of the measuerements

Denney2009: DB source link: https://iopscience.iop.org/article/10.1088/0004-637X/702/2/1353

	Assumptions:	See Bentz2013 for the corrections of the measuerements
			LCDM with H0 = 70km/s/Mpc, O_L = 0.7, O_M = 0.3

Bentz2009b: DB source link: https://iopscience.iop.org/article/10.1088/0004-637X/705/1/199

	Assumptions:	See Bentz2013 for the corrections of the measuerements

Stirpe1994: DB source link: https://ui.adsabs.harvard.edu/abs/1994ApJ...425..609S/abstract

	Assumptions:	See Bentz2013 for the corrections of the measuerements

Bentz2006a: DB source link: https://iopscience.iop.org/article/10.1086/507417

	Assumptions:	See Bentz2013 for the corrections of the measuerements

Denney2006: DB source link: https://iopscience.iop.org/article/10.1086/508533

	Assumptions:	See Bentz2013 for the corrections of the measuerements

Winge1996: DB source link: https://ui.adsabs.harvard.edu/abs/1996ApJ...469..648W/abstract

	Assumptions:	See Bentz2013 for the corrections of the measuerements

Santos-Lleo2001: DB source link: https://www.aanda.org/articles/aa/abs/2001/13/aa9537/aa9537.html

	Assumptions:	See Bentz2013 for the corrections of the measuerements

Peterson2002: DB source link: https://iopscience.iop.org/article/10.1086/344197

	Assumptions:	See Bentz2013 for the corrections of the measuerements

Bentz2007: DB source link: https://iopscience.iop.org/article/10.1086/516724

	Assumptions:	See Bentz2013 for the corrections of the measuerements

Dietrich1998: DB source link: https://iopscience.iop.org/article/10.1086/313085

	Assumptions:	See Bentz2013 for the corrections of the measuerements

Dietrich2012: DB source link: https://iopscience.iop.org/article/10.1088/0004-637X/757/1/53

	Assumptions:	See Bentz2013 for the corrections of the measuerements

Peterson2014: DB source link: https://ui.adsabs.harvard.edu/abs/2014ApJ...795..149P/abstract

	Assumptions:	See Bentz2013 for the corrections of the measuerements

Kaspi2021: DB source link: https://iopscience.iop.org/article/10.3847/1538-4357/ac00aa/pdf
	
	Assumptions: 	LCDM cosmology, H0 = 70 km/s/pc, O_L = 0.7, O_M = 0.3 
			Photometric- and spectroscopic reduction with standard IRAF procedure

Lira2018: DB source link: https://iopscience.iop.org/article/10.3847/1538-4357/aada45/pdf

	Assumptions: 	concordance cosmology; O_L = 0.7, O_M = 0.3
			Standard IRAF corrections 
			Continuum substraction of emission lines

McDougall25: DB source link: https://arxiv.org/pdf/2512.01261 (PREPRINT!!!)

	Assumptions:	local continuum substraction of flux
			removing Mg-2's iron contamination
			LCDM with H0 = 70 km/s/Mpc, O_L = 0.7, O_m = 0.3
			L5100 and other Luminosities use bolometric correction from Runnoe2012
			f = 4.31 +- 1.05
	Problem:	half year seasonal gap (Jan-Aug)
			18-25 observations, hence using 18 as minimum

Peterson2005: DB source link: https://iopscience.iop.org/article/10.1086/444494/pdf
	
	Assumptions:	f = 5.5
			correct UV luminosities for reddening
			LCDM cosmology with H0 = 70 km/s/Mpc, O_L = 0.7, O_m = 0.3

Metzroth2006: DB source link: https://iopscience.iop.org/article/10.1086/505525/pdf

	Assumptions:	f = 5.5

De Rosa2015: DB source link: https://iopscience.iop.org/article/10.1088/0004-637X/806/1/128/pdf

	Assumptions:	CalCOS pipeline for data reduction
			LCDM with H0 = 70 km/s/Mpc, O_L = 0.72, O_m = 0.28

Hoormann2019: DB source link: https://ui.adsabs.harvard.edu/abs/2019MNRAS.487.3650H/abstract

	Assumptions:	f = 4.47 +- 1.25
			LCDM with H0 = 70 km/s/Mpc, O_L = 0.7, O_m = 0.3

Penton2025: DB source link: https://arxiv.org/pdf/2512.01260 (PREPRINT!!!)

	Assumptions:	local continuum substraction of flux
			removing Mg-2's iron contamination
			LCDM with H0 = 70 km/s/Mpc, O_L = 0.7, O_m = 0.3
			L5100 and other Luminosities use bolometric correction from Runnoe2012
			f = 4.31 +- 1.05
	Problem:	half year seasonal gap (Jan-Aug)
			18-25 observations, hence using 18 as minimum

Hu2025: DB source link: https://iopscience.iop.org/article/10.3847/1538-4365/add40b/pdf

	Assumptions:	standard IRAF reduction of photometric and spectroscopic data
			corrected for galactic extinction and host contamination
			telluric correction for PG 2308+098
			f = 4.31
			LCDM with H0 = 72 km/s/Mpc, O_L = 0.7, O_m = 0.3

Woo2024: DB source link: https://iopscience.iop.org/article/10.3847/1538-4357/ad132f/pdf

	Assumptions:	LCDM with H0 = 72 km/s/Mpc, O_m = 0.3
			standard IRAF reduction and LA-Cosmic cosmic ray correction
			remove host contamination with spectral decomposition
			detrending of individual objects
			f = 4.47 +- 0.43

Grier2017: DB source link: https://iopscience.iop.org/article/10.3847/1538-4357/aa98dc/pdf

	Assumptions:	LCDM with h = 0.7, O_L = 0.7, O_M = 0.3
		photometric subtraction using ISIS
		f_sigma = 4.47 and f_FWHM = 1.12
		L5100 is host corrected

Bai2025: DB source link: https://arxiv.org/pdf/2512.08192

	Assumptions:	LCDM with H0 = 67km/s/Mpc, O_L = 0.68, O_M = 0.32
			correct spectra for cosmic rays by taking two per night
			photometry is reduced using standard IRAF procedures
			correct for galactic extinction
			neglegt host contamination
			f = 1

Hu2021: DB source link: https://iopscience.iop.org/article/10.3847/1538-4365/abd774/pdf

	Assumptions:	standard IRAF reduction
			remove host contamination
			f = 4.31

Zastrocky2024: DB source link: https://iopscience.iop.org/article/10.3847/1538-4365/ad3bad/pdf

	Assumptions:	prefer bright, northern objects with asymmetric H_beta profiles
		standard IRAF v2.16 data reduction
		spectra corrected for Galactic reddening and extinction by Cardelli1989 and Shlafly&Finkbeiner2011
		removed narrow line contamination and FeII contamination on individual objects
		likely underestimation of H_beta flux uncertainties
		ICCF for lag calculation
		f_FWHM = 1.12 f_sigma = 4.47
		masses come from rms spectrum

Cho2023: DB source link: https://iopscience.iop.org/article/10.3847/1538-4357/ace1e5/pdf

	Assumptions:	Flat LCDM cosmology H0 = 72km/s/Mpc, O_m = 0.3
		corrected telluric absorption features using PypeIt
		moved each spectra such that the peak of H_alpha matches theoretical wavelength of H_alpha
		account for FeII contamination in spectra, masked narrow lines and telluric residuals for continuum fitting, did not include stellar host continuum in the fit
		employed detrending on individual objects
		corrected L5100 for galactic extinction with Cardelli1989 and Shlafly&Finkbeiner2011
		No host correction in L5100 because insignificant

Fausnaugh2017: DB source link: https://iopscience.iop.org/article/10.3847/1538-4357/aa6d52/pdf

	Assumptions:	LCDM with H0 = 70km/s/Mpc, O_L = 0.7, O_M = 0.3
			standard IRAF corrections of the spectra
			f = 4.47 +- 1.25
			Correct for galactic extinction Shlafly&Finkbeiner2011 and Cardelli1989
			NGC 4051 distance is derived from Tully-Fischer distance
			Not sure if host contamination was removed. They employ it, but I dont think they give the values after the subtraction...

Du2015: DB source link: https://iopscience.iop.org/article/10.1088/0004-637X/806/1/22/pdf

	Assumptions:	LCDM with H0 = 67km/s/Mpc, O_L = 0.68, O_M = 0.32
			f = 1
			Correct for galaxy host contamination of L5100
			use mean spectra for masses

Grier2012: DB source link: https://iopscience.iop.org/article/10.1088/0004-637X/755/1/60

	Assumptions:	LCDM with H0 = 70km/s/Mpc, O_L = 0.7, O_M = 0.3
		follows observational and data reduction practices of Denney2010 for spectroscopic observations
		f = 5.5 and rms line dispersion
		L5100 is host corrected except Mrk 6 and Mrk 1501
	3 Objekte sind schon von Bentz in der Datenbank. Aber i guess man kann Grier einfügen und dafür die aus der Bentz Liste raushauen, unless sie hat actually die luminosity korrigiert.
