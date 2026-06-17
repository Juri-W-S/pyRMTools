import numpy as np
from stingray.simulator import simulator
import matplotlib.pyplot as plt
from scipy import signal
import scipy.stats as sst

# Transferfunction
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
    dt = 86400 * 0.5
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
half year.
'''

def generate_observations(baseline, cadence):
    # N = int(baseline / cadence)
    # t = np.linspace(1,baseline, N, endpoint = True)
    t = np.arange(0,baseline, cadence)
    gap_start = []
    gap_end = []
    n_gaps = baseline // (365.25/2) - baseline // (365.25)
    for i in range(int(n_gaps)):
        start = (i+1) * 365.25 - (365.25/2)
        gap_start.append(start)
        end = min((i+1)*365.25,baseline)
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
Input parameters of the source that is planned to be observed with RM
'''

luminosity = float(input('What is the Luminosity you want to check?'))
z = float(input('At what redshift is the source?'))
baseline = float(input('What is the baseline you plan on using?'))
cadence = float(input('What is the cadence you plan on using?'))
sn = float(input('What S/N will be achieved?'))

lag = 10**(1.5 + 0.5 * np.log10(luminosity/1e44)) * (1+z)
sf = 0.079*(1+z)**0.15 * (luminosity/1e46)**(-0.2) * (510/1000) ** (-0.44) * (baseline/365.25) ** 0.246
rms = sf / np.sqrt(2)
length = lag * 40    # Accounting for the generation of longer light curves than needed.

N = 1000
received_lags = []
outlier = 0
for i in range(N):
    time, cont, line = generate_lc(length, lag, rms)
    t = generate_observations(baseline, cadence)
    contin = downsample_lc(t, time, cont)
    lines = downsample_lc(t, time, line)
    error_cs = np.abs(contin) / sn    # Using the absolute value, such that the randomly added noise can be drawn randomly
    error_ls = np.abs(lines) / sn 
    if error_cs.any() == 0:
        error_cs += 1e-6
    if error_ls.any() == 0:
        error_ls += 1e-6
    cont_final = contin + np.random.normal(0,error_cs)
    line_final = lines + np.random.normal(0,error_ls)
    tlag_peak, status_peak, tlag_centroid, status_centroid, ccf_pack, max_rval, status_rval, peak_pvalue = peakcent(t, cont_final, t, 
                                                                                                                    line_final, -0.3 * baseline, 0.5 * baseline, 0.8 * cadence)
    if status_centroid == 1:
        received_lags.append(tlag_centroid / (1+z))
    if tlag_centroid / lag > 1.5 or tlag_centroid / lag < 0.5:
        outlier += 1

t_plot = generate_observations(baseline, 0.5)
cont_plot = downsample_lc(t_plot, time, cont)
line_plot = downsample_lc(t_plot, time, line)
plt.figure(figsize = (12,7))
plt.plot(t_plot, cont_plot, label = 'continuum curve')
plt.fill_between(t_plot, cont_plot - cont_plot/sn, cont_plot + cont_plot/sn, alpha = 0.3, label = 'continuum curve uncertainty')
plt.plot(t_plot, line_plot, label = 'line curve')
plt.fill_between(t_plot, line_plot - line_plot/sn, line_plot + line_plot/sn, alpha = 0.3, label = 'line curve uncertainty')
plt.scatter(t, cont_final, marker = 'x', label = 'continuum data')
plt.scatter(t, line_final, marker = 'x', label = 'line data')
plt.legend(loc = 'best')
plt.show()

outlier_fraction = outlier / N * 100
succes = len(received_lags) / N * 100
received_lag = np.median(received_lags)
low = np.percentile(received_lags, 16)
high = np.percentile(received_lags, 84)
lag_error_plus=(high-received_lag)
lag_error_minus=(received_lag - low)

fraction = received_lags / lag -1 # 50 is true lag
low = np.percentile(fraction, 16)
high = np.percentile(fraction, 84)


plt.figure(figsize = (10, 10 / 1.618))
#plt.title('Bias histogram for rmax = 0.8, t_unit = 0.8 * 1/24')
plt.hist(fraction, 100)
plt.axvline(np.median(fraction), label = 'Median bias', color = 'red', ls = 'dashed', lw = 1)
plt.axvline(low, label = '16th percentile', color = 'black', ls = 'dashed', lw = 1)
plt.axvline(high, label = '84th percentile', color = 'black', ls = 'dashed', lw = 1)
plt.legend(loc = 'best')
plt.xlabel('bias')
plt.ylabel('Counts')
#plt.xlim(-0.75,1.25)
plt.tick_params(axis = 'x', direction = 'out')
plt.tick_params(axis = 'y', direction = 'in')
plt.show()

luminosities = np.linspace(1e40, 1e48)
lags = 10**(1.5 + 0.5 * np.log10(luminosities/1e44))

print('value', '+', '-')
print(received_lag, lag_error_plus, lag_error_minus)
print('Succes rate:', succes, '%')
print('Outlier fraction:', outlier_fraction, '%')
plt.figure(figsize = (12,7))
plt.errorbar(luminosity / 1e44, received_lag, yerr = [[lag_error_minus], [lag_error_plus]], label = 'Simulated result', fmt = 'x', elinewidth=1, capsize = 3)
plt.scatter(luminosity / 1e44, lag / (1+z), marker = 'x', label = 'Expected result')
plt.plot(luminosities / 1e44, lags, label = 'Physical R-L relation')
plt.legend(loc = 'best')
plt.xscale('log')
plt.yscale('log')
plt.xlabel(r'Luminosity [$10^{44}$ erg/s]')
plt.ylabel('R [light days]')
plt.show()
plt.close('all')
