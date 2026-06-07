'''
This is one exemplatory code for the various trials with different
parameter grids we did. To extend using different simulation parameters
one can simply change the parameter grid. We also show, how we applied
detrending, which sometimes was employed, and sometimes was not. Note,
that for optimal results the peakcent parameters of tlagmin, tlagmax
should be made independent of the set baseline. In this example it is
set to a fraction of the baseline, instead of the actual length of the
light curve.
'''

import numpy as np
from stingray.simulator import simulator
import matplotlib.pyplot as plt
from scipy import signal
from glob import glob
import scipy.stats as sst
import pandas as pd
from scipy.signal import find_peaks, peak_prominences
from scipy.optimize import curve_fit

'''
Polynomial to fit longterm trends
'''

def detrend_fit(x, a, b, c):
    return a*x**2+b*x+c

'''
Transferfunction
'''

def top_hat(time, lag, width):
    t_max = lag + width/2
    t_min = lag - width/2
    psi = np.zeros_like(time, dtype = float)
    mask = (time >= t_min) & (time <= t_max)
    psi[mask] = 1.0
    psi /= np.sum(psi)
    return psi

'''
Generating light curves based on a DRW and convolving with a transferfuntion.
Light curves have a resolution of half a day per time step, and due to the
time cutting from the FFT they are generated longer than needed. A longer 
light curve does not introduce any physical issues, since the DRW parameters
are set independent of the light curve length.
'''

def generate_lc(days, lag, rms):
    dt = 86400 * 0.5 # resolution of 0.5 days
    sim = simulator.Simulator(N = int(4 * days), mean = 1, dt = dt, rms = rms)
    lc = sim.simulate(2)

    time = lc.time / (2 * dt)
    continuum = lc.counts
    window = int(4.4*lag)
    # convolute continuum to get line lc
    convolute_cont_line = top_hat(time, lag, lag / 2)
    line = signal.fftconvolve(continuum, convolute_cont_line, mode = 'full')
    line = line[:int(len(line)/2+1)]

    line = line[window:]
    time = time[window:]
    time = time - min(time)
    continuum = continuum[window:]
    return time, continuum, line

'''
Generating a observation grid, based on RM campaign parameters.
It is assumed equally spaced and implements seasonal gaps every
180 days of 180 days length.
'''

def generate_observations(baseline, cadence):
    t = np.arange(0,baseline, cadence)
    gap_start = []
    gap_end = []
    n_gaps = baseline // 180 - baseline // 360
    for i in range(n_gaps):
        start = (i+1) * 360 - 180
        gap_start.append(start)
        end = min((i+1)*360,baseline)
        gap_end.append(end)
    # apply observational gap
    if len(gap_start) !=0 and len(gap_end) != 0:
        for i in range(len(gap_start)):
            mask = ~((t >= gap_start[i]) & (t <= gap_end[i]))
            t = t[mask]
    return t

def downsample_lc(t, time, curve):
    observed_lc = np.interp(t, time, curve)
    return observed_lc

'''
Function taken from pyCCF to calculate the ICCF.
https://ui.adsabs.harvard.edu/abs/2018ascl.soft05032S
'''

def corsig(r, v):
    '''
    Calculate the p value that a random uncorrelated sample can yield a
    correlation coefficient as large as or larger than the observed absolute
    value of r, where r is the correlation coefficient of the data (using
    t test, valid if v>=4)
    Ref1: http://janda.org/c10/Lectures/topic06/L24-significanceR.htm
    Ref2: http://vassarstats.net/textbook/ch4apx.html

    Inputs:
        r -- the correlation coefficient of the data
        v -- degree of freedom when calculating r: N-2 (hence N>2!!!)
    Outputs:
        pvalue
    '''
    r = float(r)
    v = float(v)

    r2 = r*r
    tst = r*np.sqrt(v/(1-r2))
    pvalue = sst.t.sf(tst, v) # sf: survival function -- 1-CDF
    return pvalue

'''
Function taken from pyCCF to calculate the ICCF.
https://ui.adsabs.harvard.edu/abs/2018ascl.soft05032S
'''

def xcor(t1, y1, t2, y2, tlagmin, tlagmax, tunit, imode=0):
    '''
    Calculate cross-correlation function for unevenly
    sampling data.

    Inputs:
        t1 -- time for light curve 1, assume increase;
        y1 -- flux for light curve 1;
        t2 -- time for light curve 2, assume increase;
        y2 -- flux for light curve 2;
        tlagmin -- minimum time lag;
        tlagmax -- maximum time lag;
        tunit -- tau step;
        imode -- cross-correlation mode: 0, twice (default);
                 1, interpolate light curve 1;
                 2, interpolate light curve 2.

    Outputs:
        ccf -- correlation coefficient;
        tlag -- time lag (t2 - t1); positive values mean second
                  light curve lags the first light curve, as per convention.
                 (edit by kate, march 2016)
        npts -- number of data points used;
    '''
    if np.sum(np.diff(t1)<0.0)>0 or np.sum(np.diff(t2)<0.0)>0:
        raise Exception("The time of light curve 1 or light curve 2 is NOT INCREASING!!! Please check your data!!!")
    n1 = len(y1)
    n2 = len(y2)
    if n1<2 or n2<2:
        raise Exception("The light curve should contain at least 2 data points!!!")
    safe = tunit*0.1
    taulist12 = []
    taulist21 = []
    npts12 = []
    npts21 = []
    ccf12 = []  # interpolate 2
    ccf21 = []  # interpolate 1
    tau_max = tlagmax+safe
    # first interpolate 2
    if imode != 1:
        tau = tlagmin + 0.0 # if imode=1, skip the interpolate 2 step
    else:
        tau = tau_max + 0.0
    while tau < tau_max:
        t2new = t1 + tau
        selin = np.where((t2new>=np.min(t2))&(t2new<=np.max(t2)), True, False)
        knot = np.sum(selin)  # number of datapoints used
        if knot>0:
            y2new = np.interp(t2new[selin], t2, y2)

            y1sum = np.sum(y1[selin])
            y1sqsum = np.sum(y1[selin]*y1[selin])
            y2sum = np.sum(y2new)
            y2sqsum = np.sum(y2new*y2new)
            y1y2sum = np.sum(y1[selin]*y2new)

            fn = float(knot)
            rd1_sq = fn*y2sqsum - y2sum*y2sum
            rd2_sq = fn*y1sqsum - y1sum*y1sum
            if rd1_sq>0.0:
                rd1 = np.sqrt(rd1_sq)
            else:
                rd1 = 0.0
            if rd2_sq>0.0:
                rd2 = np.sqrt(rd2_sq)
            else:
                rd2 = 0.0

            if rd1*rd2==0.0:
                r = 0.0
            else:
                r = (fn*y1y2sum - y2sum*y1sum)/(rd1*rd2)
            ccf12.append(r)
            taulist12.append(tau)
            npts12.append(knot)
        tau += tunit
    # now interpolate 1
    if imode != 2:
        tau = tlagmin + 0.0
    else:
        tau = tau_max + 0.0
    while tau < tau_max:
        t1new = t2 - tau
        selin = np.where((t1new>=np.min(t1))&(t1new<=np.max(t1)), True, False)
        knot = np.sum(selin)  # number of datapoints used
        if knot>0:
            y1new = np.interp(t1new[selin], t1, y1)

            y2sum = np.sum(y2[selin])
            y2sqsum = np.sum(y2[selin]*y2[selin])
            y1sum = np.sum(y1new)
            y1sqsum = np.sum(y1new*y1new)
            y1y2sum = np.sum(y1new*y2[selin])

            fn = float(knot)
            rd1_sq = fn*y2sqsum - y2sum*y2sum
            rd2_sq = fn*y1sqsum - y1sum*y1sum
            if rd1_sq>0.0:
                rd1 = np.sqrt(rd1_sq)
            else:
                rd1 = 0.0
            if rd2_sq>0.0:
                rd2 = np.sqrt(rd2_sq)
            else:
                rd2 = 0.0

            if rd1*rd2==0.0:
                r = 0.0
            else:
                r = (fn*y1y2sum - y2sum*y1sum)/(rd1*rd2)
            ccf21.append(r)
            taulist21.append(tau)
            npts21.append(knot)
        tau += tunit

    # return results according to imode
    taulist12 = np.asarray(taulist12)
    npts12 = np.asarray(npts12)
    taulist21 = np.asarray(taulist21)
    npts21 = np.asarray(npts21)
    ccf12 = np.asarray(ccf12)
    ccf21 = np.asarray(ccf21)
    if imode==0:
        # make sure taulist12 and taulist21 have the same size!!!
        if np.array_equal(taulist12, taulist21):
            ccf = (ccf12 + ccf21)*0.5
            taulist = taulist12 + 0.0
            npts = npts12 + 0.0
        else:
            taulist = np.intersect1d(taulist12, taulist21)
            sel_cb12 = np.in1d(taulist12, taulist)
            sel_cb21 = np.in1d(taulist21, taulist)
            ccf = (ccf12[sel_cb12] + ccf21[sel_cb21])*0.5
            npts = (npts12[sel_cb12] + npts21[sel_cb21])*0.5
    elif imode==1:
        ccf = ccf21 + 0.0
        taulist = taulist21 + 0.0
        npts = npts21 + 0.0
    else:
        ccf = ccf12 + 0.0
        taulist = taulist12 + 0.0
        npts = npts12 + 0.0

    return ccf, taulist, npts

'''
Function taken from pyCCF to calculate the ICCF.
https://ui.adsabs.harvard.edu/abs/2018ascl.soft05032S
'''

def peakcent(t1, y1, t2, y2, tlagmin, tlagmax, tunit, thres=0.8, siglevel=0.95, imode=0, sigmode = 0.2):
    '''
    Calculate peak time lag and centroid based on the cross-correlation
    function for unevenly sampling data.

    Inputs:
        t1 -- time for light curve 1, assume increase;
        y1 -- flux for light curve 1;
        t2 -- time for light curve 2, assume increase;
        y2 -- flux for light curve 2;
        tlagmin -- minimum time lag;
        tlagmax -- maximum time lag;
        tunit -- tau step;
        thres -- lower limit of correlation coefficient when
                 calculate centroid, default is 0.8;
        siglevel -- the required significant level of the
                 correlation coefficient;
        imode -- cross-correlation mode: 0, twice (default);
                 1, interpolate light curve 1;
                 2, interpolate light curve 2.
        sigmode -- how to deal with significance:
                Will use r = input value as the minimum correlation coefficient to consider (default = 0.2).
                0: Will use a p-test to assign significance to peak and discard peaks that are below
                the significance threshold (depends on number of points included and r).

    Outputs:
        tlag_peak -- time lag based on the peak argument;
        status_peak -- peak status (1, constrained; 0, unconstrained);
        tlag_centroid -- time lag for centroid;
        status_centroid -- centroid status (1, constrained; 0, unconstrained);
    '''
    alpha = 1.0 - siglevel  # probability threshold to reject: no correlation hypothesis

    ccf_pack = xcor(t1, y1, t2, y2, tlagmin, tlagmax, tunit, imode)

    '''
    To add detrending the following block is used.
    '''

#     ccf_r = ccf_pack[0]
#     tau = ccf_pack[1]
#     if np.median(ccf_r) != 0:
#         ratio_ccf = np.abs(max(ccf_r) / np.median(ccf_r))
#     else:
#         ratio_ccf = 0
#     peak_ccf, _ = find_peaks(ccf_r)
#     prominences_ccf = peak_prominences(ccf_r, peak_ccf)[0] if len(peak_ccf) > 0 else np.array([0])


#     if ratio_ccf < 1.5 and prominences_ccf.max() < 1.5:
#         popt, pcov = curve_fit(detrend_fit, t1, y1)
#         y1 = y1 - detrend_fit(t1, *popt)
#         y2 = y2 - detrend_fit(t1, *popt)
#         ccf_pack = xcor(t1, y1, t2, y2, tlagmin, tlagmax, tunit, imode)
  
    max_indx = np.argmax(ccf_pack[0])
    max_rval = ccf_pack[0][max_indx]
    if ccf_pack[2][max_indx]>2.0:
        peak_pvalue = corsig(ccf_pack[0][max_indx], float(ccf_pack[2][max_indx]-2.0))
    else:
        peak_pvalue = 1.0 # significance level
    # ccf peaks --- excluding all with r < 0.2 instead of using p-value test.
    if sigmode > 0:
        #print 'Using minimum r coefficient instead of significance test.'
        #Check and see if the max r is on the edge of the CCF. Fail it if so.
        if max_rval >= sigmode and ccf_pack[1][max_indx] > tlagmin and ccf_pack[1][max_indx] < tlagmax:
            tlag_peak = ccf_pack[1][max_indx]
            max_rval = max_rval
            status_peak = 1
            status_rval = 1
            status_centroid = 0 # if lag is well determined, we will change status_centroid to 1
            tlag_centroid = -9999.0
        else:
            max_rval = -9999.0
            tlag_peak = -9999.0
            tlag_centroid = -9999.0
            status_peak = 0
            status_rval = 0
            status_centroid = 0
    else:
        # ccf peaks-- Eric's method using a p-value test (usually not using)
        #Check and see if the max r is on the edge of the CCF. Fail it if so.
        if peak_pvalue<alpha and ccf_pack[1][max_indx] > tlagmin and ccf_pack[1][max_indx] < tlagmax:
            tlag_peak = ccf_pack[1][max_indx]
            max_rval = max_rval
            status_peak = 1
            status_rval = 1
            status_centroid = 0 # if lag is well determined, we will change status_centroid to 1
            tlag_centroid = -9999.0
        else:
            max_rval = -9999.0
            tlag_peak = -9999.0
            tlag_centroid = -9999.0
            status_peak = 0
            status_rval = 0
            status_centroid = 0
    #If the peak succeeds, calculate centroid:
    if status_peak == 1:
        rcent = thres*max_rval
        # find out the range of centroid around the primary peak
        rdif_neg = np.where(ccf_pack[0]-rcent<0.0, True, False)
        tlag_rneg = ccf_pack[1][rdif_neg] - tlag_peak
        tlag_leftall = np.abs(tlag_rneg[tlag_rneg<0.0])
        tlag_rightall = np.abs(tlag_rneg[tlag_rneg>0.0])
        if len(tlag_leftall)>0 and len(tlag_rightall)>0:
            tlag_left = tlag_peak - np.min(tlag_leftall) # the left edge of the centroid around the primary peak
            tlag_right = tlag_peak + np.min(tlag_rightall) # the right edge of the centroid around the primary peak
            if tlag_left>=np.min(ccf_pack[1]) and tlag_right<=np.max(ccf_pack[1]):
                # centroids
                selcen = np.where((ccf_pack[1]>tlag_left)&(ccf_pack[1]<tlag_right),True,False)
                if np.sum(selcen)>0:
                    tlag_centroid = np.sum(ccf_pack[0][selcen]*ccf_pack[1][selcen])/np.sum(ccf_pack[0][selcen])
                    status_centroid = 1
    # end of centroid calculation
    #Now, if the centroid fails, re-set the peak status to 0 because we don't want to report a peak without a centroid!
    if status_centroid == 0:
        status_peak = 0
        tlag_peak = -9999.0
        max_rval = -9999.0
        status_rval = 0
    #print tlag_peak, status_peak, tlag_centroid, status_centroid, max_rval, status_rval
    return tlag_peak, status_peak, tlag_centroid, status_centroid, ccf_pack, max_rval, status_rval, peak_pvalue

'''
Setting the parameter space and create light curves, which are saved
in case of further needed analysis.
'''

lag = 50
rms = 0.1
length = lag * 40

N = 1000 # realizations
for i in range(N):
    time, cont, line = generate_lc(length, lag, rms)
    params = np.array([length, lag, rms]) #Parameters saved as length, lag, rms
    np.savez_compressed(f'mock_lc\\lc_{i}', time = time, continuum = cont, line = line, parameters = params)

'''
Sample the light curves and add noise.
'''

cadence = np.array([1,2,10,15,20,25]) # days
baseline = np.array([150,200,250,300,350,400,500])
X, Y = np.meshgrid(baseline, cadence)
x = X.ravel()
y = Y.ravel()
sn = np.array([20,50,100])

for i in range(N):
    data = np.load(f'mock_lc\\lc_{i}.npz')
    time = data['time']
    cont = data['continuum']
    line = data['line']
    paramet = data['parameters']
    for j in range(len(x)):
        t = generate_observations(x[j], y[j])
        contin = downsample_lc(t, time, cont)
        lines = downsample_lc(t, time, line)
        for k in range(len(sn)):
            error_cs = contin / sn[k]
            error_ls = lines / sn[k]
            cs_error = contin + np.random.normal(0,error_cs)
            ls_error = lines + np.random.normal(0,error_ls)
            params = np.array([paramet[0], paramet[1], paramet[2], x[j], y[j], sn[k]]) # Parameters saved as length, lag, rms, baseline, cadence, S/N
            np.savez_compressed(f'random_noise_lc\\lc_{i}_sample_{j}_noise_{k}', time = t, continuum = cs_error, line = ls_error, parameters = params)

'''
Employ the ICCF to retrieve the lags.
'''

for i in range(len(x)):
    for j in range(len(sn)):
        files = glob(f'random_noise_lc\\lc_*_sample_{i}_noise_{j}.npz')
        received_lags = []
        for path in files:
            data = np.load(path)
            time_1 = data['time']
            time_2 = data['time']
            cont = data['continuum']
            line = data['line']
            paramet = data['parameters']
            tlag_peak, status_peak, tlag_centroid, status_centroid, ccf_pack, max_rval, status_rval, peak_pvalue = peakcent(time_1, cont, time_2, line, -0.3 * paramet[3], 0.5 * paramet[3], 0.8 * paramet[4])
            if status_centroid == 1:
                received_lags.append(tlag_centroid)
        received_lags = np.array(received_lags)
        np.savez_compressed(f'results\\result_sample_{i}_noise_{j}', lags = received_lags, parameters = paramet)

'''
Review bias histograms for different parameter combinations and
create a csv file which contains the relevant results. This may
fill up your RAM, since it is a lot of plots.
'''

result_index = []
lag = []
lag_error_plus = []
lag_error_minus = []
fraction = []
lag_sigma = []
rel_error = []
baseline = []
cadence = []
epochs = []
sn = []
mean_bias = []
std = []
t_tau = []
T_tau = []
chi = []
bias_std = []
resolution = []
outlier_fraction = []
coverage_fraction = []
color = ['blue', 'orange',  'green']

# The ranges need to be set accordingly to the employed grid.
for i in range(42):
    plt.figure(figsize = (12,7))
    for j in range(3):
        data = np.load(f'results\\result_sample_{i}_noise_{j}.npz')
        lags = data['lags']
        paramet = data['parameters']

        median_lag = np.median(lags)
        low = np.percentile(lags, 16)
        high = np.percentile(lags, 84)

        bias_fraction = lags / 50 - 1
        fraction_low = np.percentile(bias_fraction, 16)
        fraction_high = np.percentile(bias_fraction, 84)
        # All divisions by 50 come from the set true lag of 50 days.
        # When different lags are simulated, that number has to be changed.
        t_tau.append(paramet[4] / 50)
        T_tau.append(paramet[3] / 50)
        result_index.append(f'{i},{j}')
        lag.append(median_lag)
        lag_error_plus.append(high-median_lag)
        lag_error_minus.append(median_lag - low)
        lag_sigma.append(np.abs(median_lag - 50)/(0.5*(high-low)))
        rel_error.append(np.abs(median_lag - 50) / 50)
        fraction.append(np.median(bias_fraction))
        baseline.append(paramet[3])
        cadence.append(paramet[4])
        sn.append(paramet[5])
        std.append(np.std(lags))
        bias_std.append(np.std(bias_fraction))
        resolution.append(0.5 * (fraction_high - fraction_low))
        counter = 0
        for k in range(len(bias_fraction)):
            if np.abs(bias_fraction[k]) > 0.5:
                counter += 1
        outlier_fraction.append(counter / len(bias_fraction))
        epochs.append(paramet[3] / paramet[4])
        t = np.arange(0,paramet[3], paramet[4])
        gap_start = []
        gap_end = []
        n_gaps = int(paramet[3]) // 180 - int(paramet[3]) // 360
        for l in range(n_gaps):
            start = (l+1) * 360 - 180
            gap_start.append(start)
            end = min((l+1)*360,int(paramet[3]))
            gap_end.append(end)
        # apply observational gap
        t_new = t.copy()
        if len(gap_start) !=0 and len(gap_end) != 0:
            for l in range(len(gap_start)):
                mask = ~((t_new >= gap_start[l]) & (t_new <= gap_end[l]))
                t_new = t_new[mask]
            percentage = len(t_new) / len(t)
        else:
            percentage = 1
        coverage_fraction.append(percentage)
        plt.hist(bias_fraction, bins = 100, label = f'S/N = {paramet[5]}')
        plt.text(0, 100, f'$\\delta T / \\tau$ = {paramet[4] / 50}')
        plt.text(0, 90, f'$T / \\tau$ = {paramet[3] / 50}')
        plt.axvline(np.median(bias_fraction), ls = 'dashed', color = color[j])
        print(f'Data for S/N = {paramet[5]}')
        print("Lag =", median_lag, "+", high-median_lag, "-", median_lag-low)
        print('Median fraction, 16th/84th percentile:', np.median(bias_fraction), fraction_high, fraction_low)
        print('baseline:', paramet[3])
        print('cadence:', paramet[4])
        print('t/Tau:', paramet[4] / 50)
        print('T/Tau:', paramet[3] / 50)
        print()
    plt.legend(loc = 'best')
    plt.show()


all_results = np.dstack((result_index, lag, lag_error_plus, lag_error_minus, lag_sigma, std, rel_error, baseline, cadence, sn, fraction, t_tau, T_tau, chi, bias_std, resolution, outlier_fraction, epochs, coverage_fraction))[0]
header = ['index', 'lag', 'lag_error_plus', 'lag_error_minus', 'sigma', 'std', 'relative_error', 'baseline', 'cadence', 'SN', 'bias', 't/tau', 'T/tau', 'chi', 'bias_std', 'resolution', 'outlier_fraction', 'epochs', 'coverage_fraction']

df = pd.DataFrame(data = all_results, columns = header)
df.to_csv(r'result_summary.csv', index = False)

'''
Load the csv to do further analysis.
'''

data = pd.read_csv('result_summary.csv')

data['add_bias'] =  data['bias'] - 0.0024935899964381725 # Bias of the ideal simulation to calculate additionally introduced bias
data['RMSE'] = np.sqrt(data['bias']**2 + data['bias_std']**2)
data['epochs'] = data['coverage_fraction'] * data['baseline'] / data['cadence']

'''
Analysis example of the effect of S/N on the simulation results.
'''

print('S/N', 'resolution', 'outlier fraction', 'bias')
SN100 = data.loc[data['SN'] == 100]
mean_res100 = np.mean(SN100['resolution'])
mean_outl100 = np.mean(SN100['outlier_fraction'])
mean_bias100 = np.mean(SN100['bias'])
print(100, mean_res100, mean_outl100, mean_bias100)
SN50 = data.loc[data['SN'] == 50]
mean_res50 = np.mean(SN50['resolution'])
mean_outl50 = np.mean(SN50['outlier_fraction'])
mean_bias50 = np.mean(SN50['bias'])
print(50, mean_res50, mean_outl50, mean_bias50)
SN20 = data.loc[data['SN'] == 20]
mean_res20 = np.mean(SN20['resolution'])
mean_outl20 = np.mean(SN20['outlier_fraction'])
mean_bias20 = np.mean(SN20['bias'])
print(20, mean_res20, mean_outl20, mean_bias20)

'''
Routine to create the plots shown in the paper to analyse
the observational parameter's effect on the simulation results
'''

fig = plt.figure(figsize = (10, 10 / 1.618))
ax = fig.add_subplot()
pos = plt.scatter( data['T/tau'],data['bias'] , c = data['SN'], norm = 'linear', cmap = 'viridis')
for value in np.unique(data['t/tau']):
    for v2 in np.unique(data['SN']):
        if v2 == 100:
            mask = (data['t/tau'] == value) & (data['SN'] == v2)
            
            x_group = data['T/tau'][mask]
            y_group = data['bias'][mask]
            plt.plot(
                x_group,
                y_group,
                linestyle="--",
                marker=None,
                label = f'$\delta T / \\tau =${value}'
            )
plt.legend(loc = 'best')
plt.ylabel('bias') 
plt.xlabel('$T/\\tau$')
plt.axhline(0)
fig.colorbar(pos, ax = ax, label = 'S/N')
plt.tick_params(which='major', direction='in')
plt.show()


fig = plt.figure(figsize = (10, 10 / 1.618))
ax = fig.add_subplot()
pos = plt.scatter( data['T/tau'],data['outlier_fraction'] , c = data['SN'], norm = 'linear', cmap = 'viridis')
for value in np.unique(data['t/tau']):
    for v2 in np.unique(data['SN']):
        if v2 == 100:
            mask = (data['t/tau'] == value) & (data['SN'] == v2)
            
            sorter = np.argsort(data['T/tau'][mask].to_numpy())

            x_group = data['T/tau'][mask].to_numpy()[sorter]
            y_group = data['outlier_fraction'][mask].to_numpy()[sorter]
            plt.plot(
                x_group,
                y_group,
                linestyle="--",
                marker=None,
                label = f'$\delta T / \\tau =${value}'
            )
plt.legend(loc = 'best')
plt.ylabel('outlier fraction') 
plt.xlabel('$T/\\tau$')
fig.colorbar(pos, ax = ax, label = 'S/N')
plt.tick_params(which='major', direction='in')
plt.ylim(0,1)
plt.show()


