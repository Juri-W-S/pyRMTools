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
            
def fit(x, a, b):                        # Basic powerlaw R-L fit
    return 10**a*x**b
        
def shaded_fit(a, a_plus, a_minus, b, b_plus, b_minus, x):    # Used to show errors of the basic powerlaw R-L fit
    a_werte = np.linspace(a-a_minus, a+a_plus, 40)
    b_werte = np.linspace(b-b_minus, b+b_plus, 40)
    Y = []
    for a_1 in a_werte:
        for b_1 in b_werte:
            Y.append(fit(x, a_1, b_1))
    Y = np.array(Y)
    y_min = Y.min(axis = 0)
    y_max = Y.max(axis =0)
    return y_min, y_max

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
Literature collection of fits. Fits using rl_model_with_errors() were fitted including intrinsic scatter,
and fits using shaded_fit() were fitted without intrinsic scatter.
'''

x = np.linspace(5e40, 1e47, 10000) / 1e44

y_min_Hu25, y_max_Hu25 = shaded_fit(1.49,0.03,0.03,0.53,0.04,0.04,x)
y_med_Shen24, y_low_Shen24, y_high_Shen24, y_s_lo_Shen24, y_s_hi_Shen24 = rl_model_with_errors(
    x, 0.41, 0.07, 0.07, 1.458, 0.038, 0.038, 0.32)
y_med_McDougall, y_low_McDougall, y_high_McDougall, y_s_lo_McDougall, y_s_hi_McDougall = rl_model_with_errors(
    x, 0.44, 0.02, 0.04, 1.43, 0.02, 0.04, 0.25)
y_med_Bentz, y_low_Bentz, y_high_Bentz, y_s_lo_Bentz, y_s_hi_Bentz = rl_model_with_errors(
    x, 0.549, 0.027, 0.028, 1.559, 0.024, 0.024, 0.13)
y_med_Woo, y_low_Woo, y_high_Woo, y_s_lo_Woo, y_s_hi_Woo = rl_model_with_errors(
    x, 0.444, 0.035, 0.036, 1.401, 0.034, 0.034, 0.177)

plt.figure(figsize = (10, 10 / 1.618))
plt.xscale('log')
plt.yscale('log')
plt.errorbar(L_McDougall2025, lag_McDougall2025 ,xerr = L_error_McDougall2025,yerr = [lag_error_minus_McDougall2025, lag_error_plus_McDougall2025] ,ls = 'None', fmt = 'o', elinewidth=1, capsize = 3, ms = 3, label = '_nolegend_', color = 'xkcd:off blue')
plt.plot([],[],'o', ms = 5, label = 'McDougall 2025', color = 'xkcd:off blue')
plt.errorbar(L_Woo2024, lag_Woo2024 ,xerr = L_error_Woo2024,yerr = [lag_error_minus_Woo2024, lag_error_plus_Woo2024] ,ls = 'None', fmt = 'o', elinewidth=1, capsize = 3, ms = 3, label = '_nolegend_',color = 'xkcd:Blue violet')
plt.plot([],[],'o', ms = 5, label = 'Woo 2024', color = 'xkcd:Blue violet')
plt.errorbar(L_Bentz2013, lag_Bentz2013 ,xerr = L_error_Bentz2013,yerr = [lag_error_minus_Bentz2013, lag_error_plus_Bentz2013] ,ls = 'None', fmt = 'o', elinewidth=1, capsize = 3, ms = 3, label = '_nolegend_', color = 'xkcd:Electric purple')
plt.plot([],[],'o', ms = 5, label = 'Bentz 2013', color = 'xkcd:Electric purple')
plt.errorbar(L_Hu2025, lag_Hu2025 ,xerr = L_error_Hu2025,yerr = [lag_error_minus_Hu2025, lag_error_plus_Hu2025] ,ls = 'None', fmt = 'o', elinewidth=1, capsize = 3, ms = 3, label = '_nolegend_', color = 'xkcd:Cool Grey')
plt.plot([],[],'o', ms = 5, label = 'Hu 2025', color = 'xkcd:Cool Grey')
plt.errorbar(L_Hu2021, lag_Hu2021 ,xerr = L_error_Hu2021,yerr = [lag_error_minus_Hu2021, lag_error_plus_Hu2021] ,ls = 'None', fmt = 'o', elinewidth=1, capsize = 3, ms = 3, label = '_nolegend_', color = 'xkcd:Charcoal Grey')
plt.plot([],[],'o', ms = 5, label = 'Hu 2021', color = 'xkcd:Charcoal Grey')
plt.errorbar(L_Grier2017, lag_Grier2017 ,xerr = L_error_Grier2017,yerr = [lag_error_minus_Grier2017, lag_error_plus_Grier2017] ,ls = 'None', fmt = 'o', elinewidth=1, capsize = 3, ms = 3, label = '_nolegend_', color = 'xkcd:Blue green')
plt.plot([],[],'o', ms = 5, label = 'Grier 2017', color = 'xkcd:Blue green')
plt.errorbar(L_Shen2024, lag_Shen2024 ,xerr = L_error_Shen2024,yerr = [lag_error_minus_Shen2024, lag_error_plus_Shen2024] ,ls = 'None', fmt = 'o', elinewidth=1, capsize = 3, ms = 3, label = '_nolegend_', color = 'xkcd:Rouge')
plt.plot([],[],'o', ms = 5, label = 'Shen 2024', color = 'xkcd:Rouge')
plt.xlabel(r'$L_{5100}$ [$10^{44}$ erg/s]')
plt.ylabel('R [light days]')
plt.title('R-L H$\\beta$')
plt.fill_between(x, y_min_Hu25, y_max_Hu25, alpha = 0.25, color = 'gray')
plt.plot(x, fit(x, 1.49, 0.53), label = 'Hu 2025 fit', color = 'gray')
plt.fill_between(x, y_low_Shen24, y_high_Shen24, color='forestgreen', alpha=0.2)
plt.plot(x, y_med_Shen24, color='forestgreen', label = 'Shen 2024 fit')
plt.plot(x, y_s_lo_Shen24, color = 'forestgreen', ls = '--', alpha = 0.5)
plt.plot(x, y_s_hi_Shen24, color = 'forestgreen', ls = '--', alpha = 0.5)
plt.fill_between(x, y_low_McDougall, y_high_McDougall, color='blue', alpha=0.2)
plt.plot(x, y_med_McDougall, color='blue', label = 'McDougall 2025 fit')
plt.plot(x, y_s_lo_McDougall, color = 'blue', ls = '--', alpha = 0.5)
plt.plot(x, y_s_hi_McDougall, color = 'blue', ls = '--', alpha = 0.5)
plt.fill_between(x, y_low_Bentz, y_high_Bentz, color='firebrick', alpha=0.2)
plt.plot(x, y_med_Bentz, color='firebrick', label = 'Bentz 2013 fit')
plt.plot(x, y_s_lo_Bentz, color = 'firebrick', ls = '--', alpha = 0.5)
plt.plot(x, y_s_hi_Bentz, color = 'firebrick', ls = '--', alpha = 0.5)
plt.fill_between(x, y_low_Woo, y_high_Woo, color='orange', alpha=0.2)
plt.plot(x, y_med_Woo, color='orange', label = 'Woo 2024 fit')
plt.plot(x, y_s_lo_Woo, color = 'orange', ls = '--', alpha = 0.5)
plt.plot(x, y_s_hi_Woo, color = 'orange', ls = '--', alpha = 0.5)
plt.legend(loc = 'upper left')
plt.tick_params(which='major', direction='in')
plt.tick_params(which='minor', direction='in')
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
Literature collection of fits. Fits using rl_model_with_errors() were fitted including intrinsic scatter,
and fits using shaded_fit() were fitted without intrinsic scatter.
'''

x = np.linspace(1e42, 1e47, 10000) / 1e44

y_med_Shen24, y_low_Shen24, y_high_Shen24, y_s_lo_Shen24, y_s_hi_Shen24 = rl_model_with_errors(
    x, 0.31, 0.06, 0.06, 2.055, 0.031, 0.030, 0.32)
y_med_McDougall, y_low_McDougall, y_high_McDougall, y_s_lo_McDougall, y_s_hi_McDougall = rl_model_with_errors(
    x, 0.34, 0.05, 0.04, 1.73, 0.03, 0.03, 0.23)
y_med_Bai, y_low_Bai, y_high_Bai, y_s_lo_Bai, y_s_hi_Bai = rl_model_with_errors(
    x, 0.24, 0.03, 0.03, 1.81, 0.02, 0.02, 0.04)

plt.figure(figsize = (10, 10 / 1.618))
plt.xscale('log')
plt.yscale('log')
plt.errorbar(L_McDougall2025, lag_McDougall2025 ,xerr = L_error_McDougall2025,yerr = [lag_error_minus_McDougall2025, lag_error_plus_McDougall2025] ,ls = 'None', fmt = 'o', elinewidth=1, capsize = 3, ms = 3, label = '_nolegend_', color = 'xkcd:off blue')
plt.plot([],[],'o', ms = 5, label = 'McDougall 2025', color = 'xkcd:off blue')
plt.errorbar(L_Shen2024, lag_Shen2024 ,xerr = L_error_Shen2024,yerr = [lag_error_minus_Shen2024, lag_error_plus_Shen2024] ,ls = 'None', fmt = 'o', elinewidth=1, capsize = 3, ms = 3, label = '_nolegend_', color = 'xkcd:Rouge')
plt.plot([],[],'o', ms = 5, label = 'Shen 2024', color = 'xkcd:Rouge')
plt.errorbar(L_Bai2025, lag_Bai2025 ,xerr = L_error_Bai2025,yerr = [lag_error_minus_Bai2025, lag_error_plus_Bai2025] ,ls = 'None', fmt = 'o', elinewidth=1, capsize = 3, ms = 3, label = '_nolegend_', color = 'xkcd:Blue green')
plt.plot([],[],'o', ms = 5, label = 'Bai 2026', color = 'xkcd:Blue green')
plt.xlabel(r'$L_{3000}$ [$10^{44}$ erg/s]')
plt.ylabel('R [light days]')
plt.title('R-L MgII')
plt.fill_between(x, y_low_Shen24, y_high_Shen24, color='firebrick', alpha=0.2)
plt.plot(x, y_med_Shen24, color='firebrick', label = 'Shen 2024 fit')
plt.plot(x, y_s_lo_Shen24, color = 'firebrick', ls = '--', alpha = 0.5)
plt.plot(x, y_s_hi_Shen24, color = 'firebrick', ls = '--', alpha = 0.5)
plt.fill_between(x, y_low_McDougall, y_high_McDougall, color='blue', alpha=0.2)
plt.plot(x, y_med_McDougall, color='blue', label = 'McDougall 2025 fit')
plt.plot(x, y_s_lo_McDougall, color = 'blue', ls = '--', alpha = 0.5)
plt.plot(x, y_s_hi_McDougall, color = 'blue', ls = '--', alpha = 0.5)
plt.fill_between(x, y_low_Bai, y_high_Bai, color='forestgreen', alpha=0.2)
plt.plot(x, y_med_Bai, color='forestgreen', label = 'Bai 2026 fit')
plt.plot(x, y_s_lo_Bai, color = 'forestgreen', ls = '--', alpha = 0.5)
plt.plot(x, y_s_hi_Bai, color = 'forestgreen', ls = '--', alpha = 0.5)
plt.legend(loc = 'upper left')
plt.tick_params(which='major', direction='in')
plt.tick_params(which='minor', direction='in')
plt.show()

'''
Plotting the CIV R-L relation using data from the RM database.
'''

cursor = objects.find({'$and':[{'properties.lags.c4': {'$exists': True}}, {'properties.L1350.Lira2018': {'$exists': True}}]})

lag_Lira2018 = []
lag_error_plus_Lira2018 = []
lag_error_minus_Lira2018 = []
lag_grade_Lira2018 = []

L_Lira2018 = []
L_error_Lira2018 = []

for object in cursor:
    lag, lag_error_plus, lag_error_minus, lag_grade = get_lag(object, 'c4', mode = 'simple',source = 'Lira2018')
    L, L_error = get_luminosity(object, 'L1350', mode = 'simple',source ='Lira2018')
    lag_Lira2018.append(lag)
    lag_error_plus_Lira2018.append(lag_error_plus)
    lag_error_minus_Lira2018.append(lag_error_minus)
    lag_grade_Lira2018.append(lag_grade)
    L_Lira2018.append(L / 1e44)
    L_error_Lira2018.append(L_error / 1e44)

cursor = objects.find({'$and':[{'properties.lags.c4': {'$exists': True}}, {'properties.L1350.Penton2025': {'$exists': True}}]})

lag_Penton2025 = []
lag_error_plus_Penton2025 = []
lag_error_minus_Penton2025 = []
lag_grade_Penton2025 = []

L_Penton2025 = []
L_error_Penton2025 = []

for object in cursor:
    lag, lag_error_plus, lag_error_minus, lag_grade = get_lag(object, 'c4',mode = 'simple', source = 'Penton2025')
    L, L_error = get_luminosity(object, 'L1350', mode = 'simple',source ='Penton2025')
    lag_Penton2025.append(lag)
    lag_error_plus_Penton2025.append(lag_error_plus)
    lag_error_minus_Penton2025.append(lag_error_minus)
    lag_grade_Penton2025.append(lag_grade)
    L_Penton2025.append(L / 1e44)
    L_error_Penton2025.append(L_error / 1e44)

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
Literature collection of fits. Fits using rl_model_with_errors() were fitted including intrinsic scatter,
and fits using shaded_fit() were fitted without intrinsic scatter.
'''

x = np.linspace(1e39, 1e48, 10000) / 1e44

y_min_Lira18, y_max_Lira18 = shaded_fit(0.80,0.21,0.21,0.46,0.08,0.08,x)
y_min_Kaspi21, y_max_Kaspi21 = shaded_fit(0.84,0.1,0.1,0.45,0.03,0.03,x)
y_med_Shen24, y_low_Shen24, y_high_Shen24, y_s_lo_Shen24, y_s_hi_Shen24 = rl_model_with_errors(
    x, 0.32, 0.11, 0.11, 1.52, 0.073, 0.075 ,0.51)
y_med_McDougall, y_low_McDougall, y_high_McDougall, y_s_lo_McDougall, y_s_hi_McDougall = rl_model_with_errors(
    x, 0.47, 0.04, 0.05, 1.65, 0.06, 0.05, 0.36)

plt.figure(figsize = (10, 10 / 1.618))
plt.xscale('log')
plt.yscale('log')
plt.errorbar(L_Lira2018, lag_Lira2018 ,xerr = L_error_Lira2018, yerr = [lag_error_minus_Lira2018, lag_error_plus_Lira2018] ,ls = 'None', fmt = 'o', elinewidth=1, capsize = 3, ms = 3, label = '_nolegend_', color = 'xkcd:Shamrock green')
plt.plot([],[],'o', ms = 5, label = 'Lira 2018', color = 'xkcd:Shamrock green')
plt.errorbar(L_Penton2025, lag_Penton2025 ,xerr = L_error_Penton2025,yerr = [lag_error_minus_Penton2025, lag_error_plus_Penton2025] ,ls = 'None', fmt = 'o', elinewidth=1, capsize = 3, ms = 3, label = '_nolegend_', color = 'xkcd:Off blue')
plt.plot([],[],'o', ms = 5, label = 'Penton 2025', color = 'xkcd:Off blue')
plt.errorbar(L_Kaspi2021, lag_Kaspi2021 ,xerr = L_error_Kaspi2021,yerr = [lag_error_minus_Kaspi2021, lag_error_plus_Kaspi2021] ,ls = 'None', fmt = 'o', elinewidth=1, capsize = 3, ms = 3, label = '_nolegend_', color = 'xkcd:Topaz')
plt.plot([],[],'o', ms = 5, label = 'Kaspi 2021', color = 'xkcd:Topaz')
plt.errorbar(L_Shen2024, lag_Shen2024 ,xerr = L_error_Shen2024,yerr = [lag_error_minus_Shen2024, lag_error_plus_Shen2024] ,ls = 'None', fmt = 'o', elinewidth=1, capsize = 3, ms = 3, label = '_nolegend_', color = 'xkcd:Rouge')
plt.plot([],[],'o', ms = 5, label = 'Shen 2024', color = 'xkcd:Rouge')
plt.xlabel(r'$L_{1350}$ [$10^{44}$ erg/s]')
plt.ylabel('R [light days]')
plt.title('R-L CIV')
plt.ylim(bottom = 1e-3)
plt.fill_between(x, y_min_Lira18, y_max_Lira18, alpha = 0.25, color = 'forestgreen')
plt.plot(x, fit(x, 0.80, 0.46), label = 'Lira 2018 fit', color = 'forestgreen')
plt.fill_between(x, y_min_Kaspi21, y_max_Kaspi21, alpha = 0.25, color = 'gray')
plt.plot(x, fit(x, 0.84, 0.45), label = 'Kaspi 2021 fit', color = 'gray')
plt.fill_between(x, y_low_Shen24, y_high_Shen24, color='firebrick', alpha=0.2)
plt.plot(x, y_med_Shen24, color='firebrick', label = 'Shen 2024 fit')
plt.plot(x, y_s_lo_Shen24, color = 'firebrick', ls = '--', alpha = 0.5)
plt.plot(x, y_s_hi_Shen24, color = 'firebrick', ls = '--', alpha = 0.5)
plt.fill_between(x, y_low_McDougall, y_high_McDougall, color='blue', alpha=0.2)
plt.plot(x, y_med_McDougall, color='blue', label = 'McDougall 2025 fit')
plt.plot(x, y_s_lo_McDougall, color = 'blue', ls = '--', alpha = 0.5)
plt.plot(x, y_s_hi_McDougall, color = 'blue', ls = '--', alpha = 0.5)
plt.legend(loc = 'upper left')
plt.tick_params(which='major', direction='in')
plt.tick_params(which='minor', direction='in')
plt.show()

