import numpy as np
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['quasar_db']
objects = db.objects

REFERENCE_TO_LINK = {
    "Shen2024": "https://iopscience.iop.org/article/10.3847/1538-4365/ad3936/pdf",
    "Kaspi2000": "https://iopscience.iop.org/article/10.1086/308704/pdf",
    "Bentz2013": "https://iopscience.iop.org/article/10.1088/0004-637X/767/2/149/pdf",
    "Peterson1998": "https://iopscience.iop.org/article/10.1086/305813",
    "Grier2012": "https://iopscience.iop.org/article/10.1088/0004-637X/755/1/60",
    "Santos-Lleo1997": "https://iopscience.iop.org/article/10.1086/313046",
    "Denney2009": "https://iopscience.iop.org/article/10.1088/0004-637X/702/2/1353",
    'Denney2010': 'https://iopscience.iop.org/article/10.1088/0004-637X/721/1/715#apj365393',
    "Bentz2009b": "https://iopscience.iop.org/article/10.1088/0004-637X/705/1/199",
    "Stirpe1994": "https://ui.adsabs.harvard.edu/abs/1994ApJ...425..609S/abstract",
    "Bentz2006a": "https://iopscience.iop.org/article/10.1086/507417",
    "Denney2006": "https://iopscience.iop.org/article/10.1086/508533",
    "Winge1996": "https://ui.adsabs.harvard.edu/abs/1996ApJ...469..648W/abstract",
    "Santos-Lleo2001": "https://www.aanda.org/articles/aa/abs/2001/13/aa9537/aa9537.html",
    "Peterson2002": "https://iopscience.iop.org/article/10.1086/344197",
    "Bentz2007": "https://iopscience.iop.org/article/10.1086/516724",
    "Dietrich1998": "https://iopscience.iop.org/article/10.1086/313085",
    "Dietrich2012": "https://iopscience.iop.org/article/10.1088/0004-637X/757/1/53",
    "Peterson2014": "https://ui.adsabs.harvard.edu/abs/2014ApJ...795..149P/abstract",
    "Kaspi2021": "https://iopscience.iop.org/article/10.3847/1538-4357/ac00aa/pdf",
    "Lira2018": "https://iopscience.iop.org/article/10.3847/1538-4357/aada45/pdf",
    "McDougall2025": "https://arxiv.org/pdf/2512.01261",
    "Hoormann2019": "https://ui.adsabs.harvard.edu/abs/2019MNRAS.487.3650H/abstract",
    "Peterson2005": "https://iopscience.iop.org/article/10.1086/444494/pdf",
    "Metzroth2006": "https://iopscience.iop.org/article/10.1086/505525/pdf",
    "De Rosa2015": "https://iopscience.iop.org/article/10.1088/0004-637X/806/1/128/pdf",
    "Penton2025": "https://arxiv.org/pdf/2512.01260",
    "Hu2025": "https://iopscience.iop.org/article/10.3847/1538-4365/add40b/pdf",
    "Woo2024": "https://iopscience.iop.org/article/10.3847/1538-4357/ad132f/pdf",
    'Hu2021': 'https://iopscience.iop.org/article/10.3847/1538-4365/abd774/pdf',
    'Bai2025': 'https://arxiv.org/pdf/2512.08192',
    'Grier2017': 'https://iopscience.iop.org/article/10.3847/1538-4357/aa98dc/pdf'
}
LINK_TO_REFERENCE = {v: k for k, v in REFERENCE_TO_LINK.items()}

def reference_finder(link: str):
    return LINK_TO_REFERENCE.get(link)

def link_finder(reference: str):
    return REFERENCE_TO_LINK.get(reference)

def get_lag_from_source(object, line, short_source):
    correct_index = None
    entry = object.get('properties', {}).get('lags', {}).get(f'{line}', {})
    if short_source == 'Bentz2013' and len(entry) > 0:
        indexes = []
        for i in range(len(entry)):
            if entry[i]['source'] == link_finder(short_source):
                indexes.append(i)
                correct_index = i
        if correct_index == None:
            print(f'{short_source} has no reported {line} lag for the cursors object!')
        else:
            lag = []
            lag_error_plus = []
            lag_error_minus = []
            lag_grade = []
            for i in range(len(indexes)):
                lag.append(entry[indexes[i]]['value'])
                lag_error_plus.append(entry[indexes[i]]['error +'])
                lag_error_minus.append(entry[indexes[i]]['error -'])
                lag_grade_entry = entry[indexes[i]]['grade']
                if lag_grade_entry == 'unknown':
                    lag_grade.append(-1)
                elif lag_grade_entry in ['bronze', 'silver', 'gold']:
                    lag_grade.append(-1)
                else:
                    lag_grade.append(lag_grade_entry)
    else:
        for i in range(len(entry)):
            if entry[i]['source'] == link_finder(short_source):
                correct_index = i
        if correct_index == None:
            print(f'{short_source} has no reported {line} lag for the cursors object!')
        else:
            lag = entry[correct_index]['value']
            lag_error_plus = entry[correct_index]['error +']
            lag_error_minus = entry[correct_index]['error -']
            lag_grade = entry[correct_index]['grade']
            if lag_grade == 'unknown':
                lag_grade = -1
            if lag_grade in ['bronze', 'silver', 'gold']:
                lag_grade = -1
    return lag, lag_error_plus, lag_error_minus, lag_grade
def get_all_lags(object, line, include_problematic):
    lag_entries = object.get('properties', {}).get('lags', {}).get(f'{line}')
    lag = []
    lag_error_plus = []
    lag_error_minus = []
    combined_from = []
    if include_problematic is True:
        for i in range(len(lag_entries)):
            lag.append(lag_entries[i]['value'])
            lag_error_plus.append(lag_entries[i]['error +'])
            lag_error_minus.append(lag_entries[i]['error -'])
            link = lag_entries[i]['source']
            combined_from.append(reference_finder(link))
    if include_problematic is False:
        for i in range(len(lag_entries)):
            problematic = lag_entries[i]['problematic']
            if problematic is True:
                continue
            if problematic is False:
                lag.append(lag_entries[i]['value'])
                lag_error_plus.append(lag_entries[i]['error +'])
                lag_error_minus.append(lag_entries[i]['error -'])
                link = lag_entries[i]['source']
                combined_from.append(reference_finder(link))
    if len(lag) == 0:
        return None
    else:
        return lag, lag_error_plus, lag_error_minus, combined_from
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

def get_lag(object, line,*, 
            mode: str = 'simple', 
            source: str | None = None,
            used_id: list | None = None,
            include_problematic: bool = True,
            combine_method: str = "envelope"):
    if mode == 'simple':
        if source is None:
            raise ValueError("mode = 'simple' requires source")
        lag, lag_error_plus, lag_error_minus, lag_grade = get_lag_from_source(object, line, source)
        return lag, lag_error_plus, lag_error_minus, lag_grade
    if mode == 'simple filtered':
        if source is None:
            raise ValueError("mode = 'simple filtered' requires source")
        if used_id is None:
            raise ValueError("mode = 'simple filtered' requires used_id")
        object_id_to_be_received = object.get('_id')
        if object_id_to_be_received in used_id:
            name = object.get('names')[0]
            print('lag from ' + source + ' for ' + name + " won't be included since another source is used")
            return None
        else:
            used_id.append(object_id_to_be_received)
            lag, lag_error_plus, lag_error_minus, lag_grade = get_lag_from_source(object, line, source)
            return lag, lag_error_plus, lag_error_minus, lag_grade
    if mode == 'combine lags':
        result_get_all_lags = get_all_lags(object, line, include_problematic)
        if result_get_all_lags is not None:
            lags, lags_error_plus, lags_error_minus, combined_from = result_get_all_lags
            lag, lag_error = combine_quantity(lags, lags_error_plus, lags_error_minus, combine_method)
            return lag, lag_error, combined_from
        if result_get_all_lags is None:
            return None

def get_luminosity_from_source(object, L, short_source):
    correct_index = None
    entry = object.get('properties', {}).get(f'{L}', {}).get(f'{short_source}', {})
    if short_source == 'Bentz2013' and len(entry) > 0:
        indexes = []
        for i in range(len(entry)):
            if entry[i]['source'] == link_finder(short_source):
                indexes.append(i)
                correct_index = i
        if correct_index == None:
            print(f'{short_source} has no reported {L} measurment for the cursors object!')
        else:
            value = []
            error = []
            for i in range(len(indexes)):
                value.append(entry[indexes[i]]['value'])
                if 'error' in entry[indexes[i]].keys():
                    error.append(entry[indexes[i]]['error'])
                else:
                    error.append(0)
    else:
        for i in range(len(entry)):
            if entry[i]['source'] == link_finder(short_source):
                correct_index = i
        if correct_index == None:
            print(f'{short_source} has no reported {L} measurment for the cursors object!')
        else:
            value = entry[correct_index]['value']
            if 'error' in entry[correct_index].keys():
                error = entry[correct_index]['error']
            else:
                error = 0
    return value, error
def get_all_luminosities(object, L, include_problematic):
    lum_keys = object.get('properties', {}).get(f'{L}', {})
    lum = []
    lum_error = []
    combined_from = []
    for data_set in lum_keys.keys():
        entry = lum_keys.get(f'{data_set}', {})[0]
        if include_problematic is True:
            lum.append(entry['value'])
            if 'error' in entry.keys():
                error = entry['error']
            else:
                error = entry['value'] * 0.1
            lum_error.append(error)
            combined_from.append(reference_finder(entry['source']))
        if include_problematic is False:
            if entry['problematic'] is True:
                continue
            if entry['problematic'] is False:
                lum.append(entry['value'])
                if 'error' in entry.keys():
                    error = entry['error']
                else:
                    error = entry['value'] * 0.1
                lum_error.append(error)
                combined_from.append(reference_finder(entry['source']))
    if len(lum) == 0:
        return None
    else:
        return lum, lum_error, combined_from

def get_luminosity(object, L,*, 
            mode: str = 'simple', 
            source: str | None = None,
            used_id: list | None = None,
            include_problematic: bool = True,
            combine_method: str = "envelope"):
    if mode == 'simple':
        if source is None:
            raise ValueError("mode = 'simple' requires source")
        value, error = get_luminosity_from_source(object, L, source)
        return value, error
    if mode == 'simple filtered':
        if source is None:
            raise ValueError("mode = 'simple filtered' requires source")
        if used_id is None:
            raise ValueError("mode = 'simple filtered' requires used_id")
        object_id_to_be_received = object.get('_id')
        if object_id_to_be_received in used_id:
            name = object.get('names')[0]
            print('Luminosity from ' + source + ' for ' + name + " won't be included since another source is used")
            return None
        else:
            used_id.append(object_id_to_be_received)
            value, error = get_luminosity_from_source(object, L, source)
            return value, error
    if mode == 'combine luminosities':
        result = get_all_luminosities(object, L, include_problematic)
        if result == None:
            return None
        else:
            values, errors, combined_from = result
            value, error = combine_quantity(values, errors, errors, combine_method)
            return value, error, combined_from
