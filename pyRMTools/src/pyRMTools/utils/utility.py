import numpy as np
from ..constants import LINK_TO_REFERENCE, REFERENCE_TO_LINK

def parse_linewidth_type(note: str | None):

    if note is None:
        return None

    note = note.lower()

    if 'line dispersion' in note:
        return 'line dispersion'

    if 'fwhm' in note:
        return 'FWHM'

    return None

def combine_quantity(quantity, error_plus, error_minus, method):
    if method == 'weighted_mean':
        quantity = np.array(quantity)
        weights = np.zeros_like(error_plus)
        for i in range(len(error_plus)):
            err = 0.5 * (error_plus[i] + error_minus[i])
            weights[i] = 1/(err**2)
        mean = np.sum(quantity * weights) / np.sum(weights)
        error = np.sqrt(1 / np.sum(weights))
        return mean, error
    if method == 'envelope':
        lowest = min(np.array(quantity) - np.array(error_minus))
        highest = max(np.array(quantity) + np.array(error_plus))
        value = 0.5 * (lowest+highest)
        error = 0.5 * (highest-lowest)
        return value, error
    
def reference_finder(link: str):
    return LINK_TO_REFERENCE.get(link)

def link_finder(reference: str):
    return REFERENCE_TO_LINK.get(reference)

def convert_luminosity(z, cosmo1, cosmo2, L1, L1_error = None):
    DL1 = cosmo1.luminosity_distance(z)
    DL2 = cosmo2.luminosity_distance(z)
    L2 = L1 * DL2 ** 2 / DL1 ** 2
    if L1_error is not None:
        L2_error = L1_error * DL2 ** 2 / DL1  ** 2
    else:
        L2_error = None
    return float(L2), float(L2_error)

def luminosity_distance(z, cosmo):
    DL = cosmo.luminosity_distance(z)
    return DL