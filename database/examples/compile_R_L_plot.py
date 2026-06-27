from pymongo import MongoClient
import numpy as np
import matplotlib.pyplot as plt


client = MongoClient('mongodb://localhost:27017/')
db = client['quasar_db']
objects = db.objects

#function to get the source link in the DB of a short reference e.g. Shen2024
REFERENCE_TO_LINK = {
    "Shen2024": "https://iopscience.iop.org/article/10.3847/1538-4365/ad3936/pdf",
    "Kaspi2000": "https://iopscience.iop.org/article/10.1086/308704/pdf",
    "Bentz2013": "https://iopscience.iop.org/article/10.1088/0004-637X/767/2/149/pdf",
    "Peterson1998": "https://iopscience.iop.org/article/10.1086/305813",
    "Grier2012": "https://iopscience.iop.org/article/10.1088/0004-637X/755/1/60",
    "Santos-Lleo1997": "https://iopscience.iop.org/article/10.1086/313046",
    "Denney2009": "https://iopscience.iop.org/article/10.1088/0004-637X/702/2/1353",
    "Bentz2009b": "https://iopscience.iop.org/article/10.1088/0004-637X/705/1/199",
    "Stirpe1994": "https://ui.adsabs.harvard.edu/abs/1994ApJ...425..609S/abstract",
    "Bentz2006a": "https://iopscience.iop.org/article/10.1086/507417",
    "Denney2006": "https://iopscience.iop.org/article/10.1086/508533",
    "Winge1996": "https://ui.adsabs.harvard.edu/abs/1996ApJ...469..648W/abstract",
    "SantosLleo2001": "https://www.aanda.org/articles/aa/abs/2001/13/aa9537/aa9537.html",
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

def rl_model_with_errors(L, alpha, alpha_err_minus, alpha_err_plus,
    beta, beta_err_minus, beta_err_plus, sigma):
    logL = np.log10(L)
    logR = beta + alpha * logL

    logR_err_plus = np.sqrt((logL * alpha_err_plus)**2 + (beta_err_plus)**2)
    logR_err_minus = np.sqrt((logL * alpha_err_minus)**2 + (beta_err_minus)**2)

    y_med = 10**logR
    y_low = 10**(logR - logR_err_minus)
    y_high = 10**(logR + logR_err_plus)

    y_scatter_low = 10**(logR - sigma)
    y_scatter_high = 10**(logR + sigma)

    return y_med, y_low, y_high, y_scatter_low, y_scatter_high

plt.rcParams.update({
    "font.size": 8,
    "axes.labelsize": 9,
    "axes.titlesize": 9,
    "legend.fontsize": 6.5,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,

    "axes.linewidth": 0.8,
    "lines.linewidth": 1.1,
    "lines.markersize": 3.0,
    "errorbar.capsize": 1.5,

    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "xtick.minor.width": 0.6,
    "ytick.minor.width": 0.6,

    "savefig.dpi": 600,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

'''
Plotting the H_beta R-L relation using data from the RM database.
'''

cursor = objects.find({'$and':[{'properties.lags.H_beta': {'$exists': True}}, {'properties.L5100.McDougall2025': {'$exists': True}}]})

lag_McDougall2025 = []
lag_error_plus_McDougall2025 = []
lag_error_minus_McDougall2025 = []
lag_grade_McDougall2025 = []

L_McDougall2025 = []
L_error_McDougall2025 = []

for object in cursor:
    lag, lag_error_plus, lag_error_minus, lag_grade = get_lag(object, 'H_beta', mode = 'simple', source ='McDougall2025')
    L, L_error = get_luminosity(object, 'L5100',mode = 'simple', source = 'McDougall2025')
    lag_McDougall2025.append(lag)
    lag_error_plus_McDougall2025.append(lag_error_plus)
    lag_error_minus_McDougall2025.append(lag_error_minus)
    lag_grade_McDougall2025.append(lag_grade)
    L_McDougall2025.append(L / 1e44)
    L_error_McDougall2025.append(L_error / 1e44)

cursor = objects.find({'$and':[{'properties.lags.H_beta': {'$exists': True}}, {'properties.L5100.Hu2025': {'$exists': True}}]})

lag_Hu2025 = []
lag_error_plus_Hu2025 = []
lag_error_minus_Hu2025 = []
lag_grade_Hu2025 = []

L_Hu2025 = []
L_error_Hu2025 = []

for object in cursor:
    lag, lag_error_plus, lag_error_minus, lag_grade = get_lag(object, 'H_beta',mode = 'simple', source = 'Hu2025')
    L, L_error = get_luminosity(object, 'L5100',mode = 'simple', source = 'Hu2025')
    lag_Hu2025.append(lag)
    lag_error_plus_Hu2025.append(lag_error_plus)
    lag_error_minus_Hu2025.append(lag_error_minus)
    lag_grade_Hu2025.append(lag_grade)
    L_Hu2025.append(L / 1e44)
    L_error_Hu2025.append(L_error / 1e44)

cursor = objects.find({'$and':[{'properties.lags.H_beta': {'$elemMatch': {'source': link_finder('Shen2024')}}},{'properties.L5100.Shen2024': {'$exists': True}}]})

lag_Shen2024 = []
lag_error_plus_Shen2024 = []
lag_error_minus_Shen2024 = []
lag_grade_Shen2024 = []

L_Shen2024 = []
L_error_Shen2024 = []

for object in cursor:
    lag, lag_error_plus, lag_error_minus, lag_grade = get_lag(object, 'H_beta',mode = 'simple', source = 'Shen2024')
    L, L_error = get_luminosity(object, 'L5100',mode = 'simple', source = 'Shen2024')
    lag_Shen2024.append(lag)
    lag_error_plus_Shen2024.append(lag_error_plus)
    lag_error_minus_Shen2024.append(lag_error_minus)
    lag_grade_Shen2024.append(lag_grade)
    L_Shen2024.append(L / 1e44)
    L_error_Shen2024.append(L_error / 1e44)


cursor = objects.find({'$and':[{'properties.lags.H_beta': {'$exists': True}}, {'properties.L5100.Woo2024': {'$exists': True}}]})

lag_Woo2024 = []
lag_error_plus_Woo2024 = []
lag_error_minus_Woo2024 = []
lag_grade_Woo2024 = []

L_Woo2024 = []
L_error_Woo2024 = []

for object in cursor:
    lag, lag_error_plus, lag_error_minus, lag_grade = get_lag(object, 'H_beta',mode = 'simple', source = 'Woo2024')
    L, L_error = get_luminosity(object, 'L5100',mode = 'simple', source = 'Woo2024')
    lag_Woo2024.append(lag)
    lag_error_plus_Woo2024.append(lag_error_plus)
    lag_error_minus_Woo2024.append(lag_error_minus)
    lag_grade_Woo2024.append(lag_grade)
    L_Woo2024.append(L / 1e44)
    L_error_Woo2024.append(L_error / 1e44)


cursor = objects.find({'$and':[{'properties.lags.H_beta': {'$exists': True}}, {'properties.L5100.Bentz2013': {'$exists': True}}]})

lag_Bentz2013 = []
lag_error_plus_Bentz2013 = []
lag_error_minus_Bentz2013 = []
lag_grade_Bentz2013 = []

L_Bentz2013 = []
L_error_Bentz2013 = []

'''
Due to Bentz2013 being a compilation paper and correction paper at the same time
the database structure is slightly different. For each objects all measurements
are returned as a list, since Bentz2013 contains different measurements for same
objects. The lists are in the same order, such that the main reference of the
luminosity at index i is the same main reference of the lag at index i.
'''

for object in cursor:
    lag, lag_error_plus, lag_error_minus, lag_grade = get_lag(object, 'H_beta',mode = 'simple', source = 'Bentz2013')
    L, L_error = get_luminosity(object, 'L5100',mode = 'simple', source = 'Bentz2013')
    for i in range(len(lag)):
        lag_Bentz2013.append(lag[i])
        lag_error_plus_Bentz2013.append(lag_error_plus[i])
        lag_error_minus_Bentz2013.append(lag_error_minus[i])
        lag_grade_Bentz2013.append(lag_grade[i])
        L_Bentz2013.append(L[i] / 1e44)
        L_error_Bentz2013.append(L_error[i] / 1e44)

cursor = objects.find({'$and':[{'properties.lags.H_beta': {'$exists': True}}, {'properties.L5100.Hu2021': {'$exists': True}}]})

lag_Hu2021 = []
lag_error_plus_Hu2021 = []
lag_error_minus_Hu2021 = []
lag_grade_Hu2021 = []

L_Hu2021 = []
L_error_Hu2021 = []

for object in cursor:
    lag, lag_error_plus, lag_error_minus, lag_grade = get_lag(object, 'H_beta',mode = 'simple', source = 'Hu2021')
    L, L_error = get_luminosity(object, 'L5100',mode = 'simple', source = 'Hu2021')
    lag_Hu2021.append(lag)
    lag_error_plus_Hu2021.append(lag_error_plus)
    lag_error_minus_Hu2021.append(lag_error_minus)
    lag_grade_Hu2021.append(lag_grade)
    L_Hu2021.append(L / 1e44)
    L_error_Hu2021.append(L_error / 1e44)

cursor = objects.find({'$and':[{'properties.lags.H_beta': {'$elemMatch': {'source': link_finder('Grier2017')}}},{'properties.L5100.Grier2017': {'$exists': True}}]})

lag_Grier2017 = []
lag_error_plus_Grier2017 = []
lag_error_minus_Grier2017 = []
lag_grade_Grier2017 = []

L_Grier2017 = []
L_error_Grier2017 = []

for object in cursor:
    lag, lag_error_plus, lag_error_minus, lag_grade = get_lag(object, 'H_beta',mode = 'simple', source = 'Grier2017')
    L, L_error = get_luminosity(object, 'L5100',mode = 'simple', source = 'Grier2017')
    lag_Grier2017.append(lag)
    lag_error_plus_Grier2017.append(lag_error_plus)
    lag_error_minus_Grier2017.append(lag_error_minus)
    lag_grade_Grier2017.append(lag_grade)
    L_Grier2017.append(L / 1e44)
    L_error_Grier2017.append(L_error / 1e44)

'''
Literature collection of fits.
'''

x = np.linspace(5e40, 1e47, 10000) / 1e44

y_med_Shen24, y_low_Shen24, y_high_Shen24, y_s_lo_Shen24, y_s_hi_Shen24 = rl_model_with_errors(
    x, 0.41, 0.07, 0.07, 1.458, 0.038, 0.038, 0.32)
y_med_McDougall, y_low_McDougall, y_high_McDougall, y_s_lo_McDougall, y_s_hi_McDougall = rl_model_with_errors(
    x, 0.44, 0.02, 0.04, 1.43, 0.02, 0.04, 0.25)
y_med_Bentz, y_low_Bentz, y_high_Bentz, y_s_lo_Bentz, y_s_hi_Bentz = rl_model_with_errors(
    x, 0.549, 0.027, 0.028, 1.559, 0.024, 0.024, 0.13)
y_med_Woo, y_low_Woo, y_high_Woo, y_s_lo_Woo, y_s_hi_Woo = rl_model_with_errors(
    x, 0.444, 0.035, 0.036, 1.401, 0.034, 0.034, 0.177)
y_med_Hu25, y_low_Hu25, y_high_Hu25, y_s_low_Hu25, y_s_hi_Hu25 = rl_model_with_errors(
    x, 0.53, 0.04, 0.04, 1.49, 0.03, 0.03, 0
)
SINGLE_COL_FIGSIZE = (3.45, 3.4)
fig, ax = plt.subplots(figsize=SINGLE_COL_FIGSIZE, constrained_layout=True)


ax.set_xscale("log")
ax.set_yscale("log")

# -------------------------
# Data points
# -------------------------
datasets = [
    ("McDougall 2025", L_McDougall2025, lag_McDougall2025,
     L_error_McDougall2025, [lag_error_minus_McDougall2025, lag_error_plus_McDougall2025],
     "xkcd:off blue"),
    ("Woo 2024", L_Woo2024, lag_Woo2024,
     L_error_Woo2024, [lag_error_minus_Woo2024, lag_error_plus_Woo2024],
     "#5dc154"),
    ("Bentz 2013", L_Bentz2013, lag_Bentz2013,
     L_error_Bentz2013, [lag_error_minus_Bentz2013, lag_error_plus_Bentz2013],
     "#0fa8bf"),
    ("Hu 2025", L_Hu2025, lag_Hu2025,
     L_error_Hu2025, [lag_error_minus_Hu2025, lag_error_plus_Hu2025],
     "0.55"),
    ("Hu 2021", L_Hu2021, lag_Hu2021,
     L_error_Hu2021, [lag_error_minus_Hu2021, lag_error_plus_Hu2021],
     "0.25"),
    ("Grier 2017", L_Grier2017, lag_Grier2017,
     L_error_Grier2017, [lag_error_minus_Grier2017, lag_error_plus_Grier2017],
     "xkcd:Blue green"),
    ("Shen 2024", L_Shen2024, lag_Shen2024,
     L_error_Shen2024, [lag_error_minus_Shen2024, lag_error_plus_Shen2024],
     "#d80e48"),
]

for label, L, R, Lerr, Rerr, color in datasets:
    ax.errorbar(
        L, R,
        xerr=Lerr,
        yerr=Rerr,
        fmt="o",
        ms=3.5,
        mfc="white",
        mec=color,
        mew=0.8,
        ecolor=color,
        elinewidth=0.7,
        capsize=3,
        alpha=0.85,
        ls="none",
        label=label,
        zorder=3,
    )
    
fits = [
    ("Hu 2025 fit", x, y_med_Hu25, y_low_Hu25, y_high_Hu25, "0.45"),
    ("Shen 2024 fit", x, y_med_Shen24, y_low_Shen24, y_high_Shen24, "#d80e48"),
    ("McDougall 2025 fit", x, y_med_McDougall, y_low_McDougall, y_high_McDougall, "tab:blue"),
    ("Bentz 2013 fit", x, y_med_Bentz, y_low_Bentz, y_high_Bentz, "#0fa8bf"),
    ("Woo 2024 fit", x, y_med_Woo, y_low_Woo, y_high_Woo, "#5dc154"),
]

for label, xx, ymed, ylo, yhi, color in fits:
    ax.fill_between(
        xx, ylo, yhi,
        color=color,
        alpha=0.12,
        linewidth=0,
        zorder=1,
    )
    ax.plot(
        xx, ymed,
        color=color,
        lw=1.4,
        label=label,
        zorder=2,
    )
    
ax.set_xlim(5e-4, 2e2)
ax.set_ylim(3e-1, 7e2)

ax.set_xlabel(r"$\lambda L_{\lambda}(5100\,\AA)/(\mathrm{erg\,s^{-1}})$")
ax.set_ylabel(r"$R_{\mathrm{H}\beta}$ [light-days]")

ax.tick_params(which="both", direction="in", top=True, right=True)

ax.legend(
    loc="upper left",
    frameon=True,
    framealpha=0.85,
    facecolor="white",
    edgecolor="none",
    ncol=2,
    fontsize=6.5,
    handlelength=1.2,
    columnspacing=0.6,
    labelspacing=0.20,
    borderpad=0.20,
)

ax = plt.gca()
ax.xaxis.set_major_formatter(
    FuncFormatter(lambda val, pos: rf'$10^{{{int(np.log10(val*1e44))}}}$')
)
plt.show()

'''
Plotting the MgII R-L relation using data from the RM database.
'''

cursor = objects.find({'$and':[{'properties.lags.mg2': {'$exists': True}}, {'properties.L3000.McDougall2025': {'$exists': True}}]})

lag_McDougall2025 = []
lag_error_plus_McDougall2025 = []
lag_error_minus_McDougall2025 = []
lag_grade_McDougall2025 = []

L_McDougall2025 = []
L_error_McDougall2025 = []

for object in cursor:
    lag, lag_error_plus, lag_error_minus, lag_grade = get_lag(object, 'mg2', mode = 'simple', source ='McDougall2025')
    L, L_error = get_luminosity(object, 'L3000',mode = 'simple', source = 'McDougall2025')
    lag_McDougall2025.append(lag)
    lag_error_plus_McDougall2025.append(lag_error_plus)
    lag_error_minus_McDougall2025.append(lag_error_minus)
    lag_grade_McDougall2025.append(lag_grade)
    L_McDougall2025.append(L / 1e44)
    L_error_McDougall2025.append(L_error / 1e44)

cursor = objects.find({'$and':[{'properties.lags.mg2': {'$exists': True}}, {'properties.L3000.Shen2024': {'$exists': True}}]})

lag_Shen2024 = []
lag_error_plus_Shen2024 = []
lag_error_minus_Shen2024 = []
lag_grade_Shen2024 = []

L_Shen2024 = []
L_error_Shen2024 = []

for object in cursor:
    lag, lag_error_plus, lag_error_minus, lag_grade = get_lag(object, 'mg2',mode = 'simple', source = 'Shen2024')
    L, L_error = get_luminosity(object, 'L3000',mode = 'simple', source = 'Shen2024')
    lag_Shen2024.append(lag)
    lag_error_plus_Shen2024.append(lag_error_plus)
    lag_error_minus_Shen2024.append(lag_error_minus)
    lag_grade_Shen2024.append(lag_grade)
    L_Shen2024.append(L / 1e44)
    L_error_Shen2024.append(L_error / 1e44)


cursor = objects.find({'$and':[{'properties.lags.mg2': {'$exists': True}}, {'properties.L3000.Bai2025': {'$exists': True}}]})

lag_Bai2025 = []
lag_error_plus_Bai2025 = []
lag_error_minus_Bai2025 = []
lag_grade_Bai2025 = []

L_Bai2025 = []
L_error_Bai2025 = []

for object in cursor:
    lag, lag_error_plus, lag_error_minus, lag_grade = get_lag(object, 'mg2', mode = 'simple', source ='Bai2025')
    L, L_error = get_luminosity(object, 'L3000',mode = 'simple', source = 'Bai2025')
    lag_Bai2025.append(lag)
    lag_error_plus_Bai2025.append(lag_error_plus)
    lag_error_minus_Bai2025.append(lag_error_minus)
    lag_grade_Bai2025.append(lag_grade)
    L_Bai2025.append(L / 1e44)
    L_error_Bai2025.append(L_error / 1e44)

'''
Literature collection of fits.
'''

x = np.linspace(1e42, 1e47, 10000) / 1e44

y_med_Shen24, y_low_Shen24, y_high_Shen24, y_s_lo_Shen24, y_s_hi_Shen24 = rl_model_with_errors(
    x, 0.31, 0.06, 0.06, 2.055, 0.031, 0.030, 0.32)
y_med_McDougall, y_low_McDougall, y_high_McDougall, y_s_lo_McDougall, y_s_hi_McDougall = rl_model_with_errors(
    x, 0.34, 0.05, 0.04, 1.73, 0.03, 0.03, 0.23)
y_med_Bai, y_low_Bai, y_high_Bai, y_s_lo_Bai, y_s_hi_Bai = rl_model_with_errors(
    x, 0.24, 0.03, 0.03, 1.81, 0.02, 0.02, 0.04)

fig, ax = plt.subplots(figsize=SINGLE_COL_FIGSIZE, constrained_layout=True)

ax.set_xscale("log")
ax.set_yscale("log")

datasets = [
    ("McDougall 2025", L_McDougall2025, lag_McDougall2025,
     L_error_McDougall2025, [lag_error_minus_McDougall2025, lag_error_plus_McDougall2025],
     "xkcd:off blue"),
    ("Bai 2026", L_Bai2025, lag_Bai2025,
     L_error_Bai2025, [lag_error_minus_Bai2025, lag_error_plus_Bai2025],
     "#5dc154"),
    ("Shen 2024", L_Shen2024, lag_Shen2024,
     L_error_Shen2024, [lag_error_minus_Shen2024, lag_error_plus_Shen2024],
     "#d80e48"),
]

for label, L, R, Lerr, Rerr, color in datasets:
    ax.errorbar(
        L, R,
        xerr=Lerr,
        yerr=Rerr,
        fmt="o",
        ms=3.5,
        mfc="white",
        mec=color,
        mew=0.8,
        ecolor=color,
        elinewidth=0.7,
        capsize=3,
        alpha=0.85,
        ls="none",
        label=label,
        zorder=3,
    )
    
fits = [
    ("Shen 2024 fit", x, y_med_Shen24, y_low_Shen24, y_high_Shen24, "#d80e48"),
    ("McDougall 2025 fit", x, y_med_McDougall, y_low_McDougall, y_high_McDougall, "tab:blue"),
    ("Bai 2026 fit", x, y_med_Bai, y_low_Bai, y_high_Bai, "#5dc154"),
]

for label, xx, ymed, ylo, yhi, color in fits:
    ax.fill_between(
        xx, ylo, yhi,
        color=color,
        alpha=0.12,
        linewidth=0,
        zorder=1,
    )
    ax.plot(
        xx, ymed,
        color=color,
        lw=1.4,
        label=label,
        zorder=2,
    )

ax.set_xlim(1e-1, 8e2)
ax.set_ylim(3e0, 3e3)

ax.set_xlabel(r"$\lambda L_{\lambda}(3000\,\AA)/(\mathrm{erg\,s^{-1}})$")
ax.set_ylabel(r"$R_{\mathrm{Mg\,II}}$ [light-days]")

ax.tick_params(which="both", direction="in", top=True, right=True)

ax.legend(
    loc="upper left",
    frameon=True,
    framealpha=0.85,
    facecolor="white",
    edgecolor="none",
    ncol=2,
    fontsize=6,
    handlelength=1.2,
    columnspacing=0.6,
    labelspacing=0.20,
    borderpad=0.20,
)

ax = plt.gca()
ax.xaxis.set_major_formatter(
    FuncFormatter(lambda val, pos: rf'$10^{{{int(np.log10(val*1e44))}}}$')
)
plt.show()

'''
Plotting the CIV R-L relation using data from the RM database.
'''

cursor = objects.find({'$and':[{'properties.lags.c4': {'$exists': True}}, {'properties.L1350.Penton2025': {'$exists': True}}]})

lag_Penton2025 = []
lag_error_plus_Penton2025 = []
lag_error_minus_Penton2025 = []
lag_grade_Penton2025 = []

L_Penton2025 = []
L_error_Penton2025 = []

for object in cursor:
    lag, lag_error_plus, lag_error_minus, lag_grade = get_lag(object, 'c4', mode = 'simple',source = 'Penton2025')
    L, L_error = get_luminosity(object, 'L1350', mode = 'simple',source ='Penton2025')
    lag_Penton2025.append(lag)
    lag_error_plus_Penton2025.append(lag_error_plus)
    lag_error_minus_Penton2025.append(lag_error_minus)
    lag_grade_Penton2025.append(lag_grade)
    L_Penton2025.append(L / 1e44)
    L_error_Penton2025.append(L_error / 1e44)

cursor = objects.find({'$and':[{'properties.lags.c4': {'$exists': True}}, {'properties.L1350.Lira2018': {'$exists': True}}]})

lag_Lira2018 = []
lag_error_plus_Lira2018 = []
lag_error_minus_Lira2018 = []
lag_grade_Lira2018 = []

L_Lira2018 = []
L_error_Lira2018 = []

for object in cursor:
    lag, lag_error_plus, lag_error_minus, lag_grade = get_lag(object, 'c4',mode = 'simple', source = 'Lira2018')
    L, L_error = get_luminosity(object, 'L1350', mode = 'simple',source ='Lira2018')
    lag_Lira2018.append(lag)
    lag_error_plus_Lira2018.append(lag_error_plus)
    lag_error_minus_Lira2018.append(lag_error_minus)
    lag_grade_Lira2018.append(lag_grade)
    L_Lira2018.append(L / 1e44)
    L_error_Lira2018.append(L_error / 1e44)

cursor = objects.find({'$and':[{'properties.lags.c4': {'$exists': True}}, {'properties.L1350.Kaspi2021': {'$exists': True}}]})

lag_Kaspi2021 = []
lag_error_plus_Kaspi2021 = []
lag_error_minus_Kaspi2021 = []
lag_grade_Kaspi2021 = []

L_Kaspi2021 = []
L_error_Kaspi2021 = []

for object in cursor:
    lag, lag_error_plus, lag_error_minus, lag_grade = get_lag(object, 'c4',mode = 'simple', source = 'Kaspi2021')
    L, L_error = get_luminosity(object, 'L1350', mode = 'simple',source ='Kaspi2021')
    lag_Kaspi2021.append(lag)
    lag_error_plus_Kaspi2021.append(lag_error_plus)
    lag_error_minus_Kaspi2021.append(lag_error_minus)
    lag_grade_Kaspi2021.append(lag_grade)
    L_Kaspi2021.append(L / 1e44)
    L_error_Kaspi2021.append(L_error / 1e44)

cursor = objects.find({'$and':[{'properties.lags.c4': {'$exists': True}}, {'properties.L1350.Shen2024': {'$exists': True}}]})

lag_Shen2024 = []
lag_error_plus_Shen2024 = []
lag_error_minus_Shen2024 = []
lag_grade_Shen2024 = []

L_Shen2024 = []
L_error_Shen2024 = []

for object in cursor:
    lag, lag_error_plus, lag_error_minus, lag_grade = get_lag(object, 'c4',mode = 'simple', source = 'Shen2024')
    L, L_error = get_luminosity(object, 'L1350', mode = 'simple',source ='Shen2024')
    lag_Shen2024.append(lag)
    lag_error_plus_Shen2024.append(lag_error_plus)
    lag_error_minus_Shen2024.append(lag_error_minus)
    lag_grade_Shen2024.append(lag_grade)
    L_Shen2024.append(L / 1e44)
    L_error_Shen2024.append(L_error / 1e44)

'''
Literature collection of fits.
'''

x = np.linspace(1e39, 1e48, 10000) / 1e44

y_med_Shen24, y_low_Shen24, y_high_Shen24, y_s_lo_Shen24, y_s_hi_Shen24 = rl_model_with_errors(
    x, 0.32, 0.11, 0.11, 1.52, 0.073, 0.075 ,0.51)
y_med_McDougall, y_low_McDougall, y_high_McDougall, y_s_lo_McDougall, y_s_hi_McDougall = rl_model_with_errors(
    x, 0.47, 0.04, 0.05, 1.18, 0.06, 0.05, 0.36)
y_med_Lira18, y_low_Lira18, y_high_Lira18, y_s_lo_Lira18, y_s_hi_Lira18 = rl_model_with_errors(
    x, 0.46, 0.08, 0.08, 0.80, 0.21, 0.21, 0)
y_med_Kaspi21, y_low_Kaspi21, y_high_Kaspi21, y_s_lo_Kaspi21, y_s_hi_Kaspi21 = rl_model_with_errors(
    x, 0.45, 0.03, 0.03, 0.84, 0.1, 0.1, 0)

fig, ax = plt.subplots(figsize=SINGLE_COL_FIGSIZE, constrained_layout=True)

ax.set_xscale("log")
ax.set_yscale("log")

datasets = [
    ("Penton 2025", L_Penton2025, lag_Penton2025,
     L_error_Penton2025, [lag_error_minus_Penton2025, lag_error_plus_Penton2025],
     "xkcd:off blue"),
    ('Lira 2018', L_Lira2018, lag_Lira2018, 
     L_error_Lira2018, [lag_error_minus_Lira2018, lag_error_plus_Lira2018],
     '#ff830c'),
    ("Kaspi 2021", L_Kaspi2021, lag_Kaspi2021,
     L_error_Kaspi2021, [lag_error_minus_Kaspi2021, lag_error_plus_Kaspi2021],
     "#5dc154"),
    ("Shen 2024", L_Shen2024, lag_Shen2024,
     L_error_Shen2024, [lag_error_minus_Shen2024, lag_error_plus_Shen2024],
     "#d80e48"),
]

for label, L, R, Lerr, Rerr, color in datasets:
    ax.errorbar(
        L, R,
        xerr=Lerr,
        yerr=Rerr,
        fmt="o",
        ms=3.5,
        mfc="white",
        mec=color,
        mew=0.8,
        ecolor=color,
        elinewidth=0.7,
        capsize=3,
        alpha=0.85,
        ls="none",
        label=label,
        zorder=3,
    )

fits = [
    ("Shen 2024 fit", x, y_med_Shen24, y_low_Shen24, y_high_Shen24, "#d80e48"),
    ("McDougall 2025 fit", x, y_med_McDougall, y_low_McDougall, y_high_McDougall, "tab:blue"),
    ("Lira 2018 fit", x, y_med_Lira18, y_low_Lira18, y_high_Lira18, "#ff830c"),
    ('Kaspi 2021 fit', x, y_med_Kaspi21, y_low_Kaspi21, y_high_Kaspi21, '#5dc154')
]

for label, xx, ymed, ylo, yhi, color in fits:
    ax.fill_between(
        xx, ylo, yhi,
        color=color,
        alpha=0.12,
        linewidth=0,
        zorder=1,
    )
    ax.plot(
        xx, ymed,
        color=color,
        lw=1.4,
        label=label,
        zorder=2,
    )

ax.set_xlim(4e-5, 1e4)
ax.set_ylim(1e-2, 7e3)

ax.set_xlabel(r"$\lambda L_{\lambda}(1350\,\AA)/(\mathrm{erg\,s^{-1}})$")
ax.set_ylabel(r"$R_{\mathrm{C\,IV}}$ [light-days]")

ax.tick_params(which="both", direction="in", top=True, right=True)

ax.legend(
    loc="upper left",
    frameon=True,
    framealpha=0.85,
    facecolor="white",
    edgecolor="none",
    ncol=2,
    fontsize=6,
    handlelength=1.2,
    columnspacing=0.6,
    labelspacing=0.20,
    borderpad=0.20,
)

ax = plt.gca()
ax.xaxis.set_major_formatter(
    FuncFormatter(lambda val, pos: rf'$10^{{{int(np.log10(val*1e44))}}}$')
)
plt.show()
