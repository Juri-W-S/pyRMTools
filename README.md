# Reverberation mapping database

Repository accompanying the paper:

"A simulation-based quality-control framework for the broad-line region radius--luminosity relation."

## Overview

This repository contains the open source `pyRMTools` Python package and supplementary material referred to in the manuscript.
`pyRMTools` contains the reverberation mapping database and the reverberation mapping planning tool `scout` to support the observational planning of future reverberation mapping campaigns.

## Repository Structure

| Section        | Description                                                        |
| ---------------| -------------------------------------------------------------------|
| pyRMTools      | Database contents, use examples and utility functions              |
| supplementaries| Supplementary figures and tables                                   |
| reproduction   | Codes for reproduction and RM-Scout                                |
| tutorials      | Tutorials for the use of pyRMTools and MongoDB backend installaion |

---

## Quick Navigation

* [pyRMTools](pyRMTools/)
* [Reproducibility](simulation_code/)
* [Supplementary Material](results/)
* [Tutorials](tutorials/)


---

## pyRMTools

pyRMTools is a package combining a database of ~1200 AGN studied in reverberation mapping (RM) and a simulation framework of reverberation mapping campaigns.
The database is accessed by a json archive or a MongoDB backend, the latter needing a seperate installation. It contains all the relevant measurements from RM,
such as reverberation lags and luminosities, aswell-as characteristic AGN properties such as position and redshift. The simulation framework `scout` can be used
as a forecast of RM success, aswell-as a first consistency check of published RM data. 

The API of this package is explained [here](pyRMTools/README.md) and tutorials regarding the use of the package and installation of the MongoDB backend [here](pyRMtools/installing_mongodb_backend.md).

A text file describing some assumptions from publications (e.g. cosmological parameters, host-galaxy subtraction methods, extinction corrections, and calibration choices) is located [here](database/data/readme.txt). Note that the list does not claim completeness since it relies on availability of information in the publication and may be affected by human error. When in doubt about some information, please refer to the publication itself. 

### Installation

To install the latest development version:

    git clone https://github.com/Juri-W-S/pyRMTools.git /pyRMTools
    
    cd pyRMTools
    
    pip install .

The database needs no further data downloads, since it is directly distributed with the package installation.

### Tutorials

We provide two tutorials that can be found [here](tutorials/). `pyRMTools_tutorial.ipynb` introduces the used syntax and shows examples how the `pyRMTools` package can be used. `MongoDB_tutorial.py` introduces the MongoDB backend syntax by demonstrating the compilation of these R-L figures.

<p align="center">
  <img src="results/figures/md_fig/rl_hb.png" width="300">
  <img src="results/figures/md_fig/rl_mg2.png" width="300">
</p>

---

## Reproducibility

All code used to generate the results presented in the manuscript can be found in the `simulation_code/` directory.

With `ICCF_bias.py` the optimized settings for the ICCF algorithm was configured.

`ICCF_trials.py` contains the code that explored the observational parameter space to quantify the recoverability of the ICCF algorithm.

---

## Supplementary Material

Additional figures and tables, e.g. Table B.1, not included in the manuscript in full size and length are available in `results/`.

---

## Citation

If you use this repository, please cite:

Seib et al., 2026

---

## Contact

[seib@thphys.uni-heidelberg.de](mailto:seib@thphys.uni-heidelberg.de)
