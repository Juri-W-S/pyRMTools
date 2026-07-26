from .algorithm import generate_lc, generate_observations, downsample_lc, peakcent
from .relations import  linear_rl, structure_function
import numpy as np
from .results import ScoutResult, ICCFResult, LightCurve
from ..config import SimConfig

def scout(luminosity, z, baseline, cadence, sn, save_light_curves = None, relation = linear_rl, **relation_kwargs):
    N = SimConfig.scout['N']
    lag = relation(luminosity, **relation_kwargs) * (1+z)
    rms = structure_function(z, luminosity, baseline) / np.sqrt(2)
    length = lag * 40 # Accounting for the generation of longer light curves than needed.

    recovered_lags = []
    iccf_results = np.empty(N, ICCFResult)

    
    light_curves = None
    if save_light_curves == "memory":
        light_curves = []
    elif isinstance(save_light_curves, str):
        time_save = None
        continuum = []
        line_save = []
        continuum_error = []
        line_error = []

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
                                                                                                                        line_final, SimConfig.scout['tlag_min_factor']*baseline, 
                                                                                                                        SimConfig.scout['tlag_max_factor']*baseline, 
                                                                                                                        SimConfig.scout['tunit_factor']*cadence)
        iccf_results[i] = ICCFResult(lag=ccf_pack[1], r = ccf_pack[0], centroid = tlag_centroid, peak = tlag_peak, success = status_centroid)
        if status_centroid == 1:
            recovered_lags.append(tlag_centroid / (1+z))
        lc = LightCurve(t, cont_final, line_final, error_cs, error_ls)

        if save_light_curves == 'memory':
            light_curves.append(lc)
        elif isinstance(save_light_curves, str):
            if time_save is None:
                time_save = t.copy()
            continuum.append(cont_final)
            line_save.append(line_final)
            continuum_error.append(error_cs)
            line_error.append(error_ls)
    recovered_lags = np.array(recovered_lags)
    
    if save_light_curves != 'memory' and isinstance(save_light_curves, str):
        np.savez_compressed(
            save_light_curves,
            time=time_save,
            continuum=np.asarray(continuum),
            line=np.asarray(line),
            continuum_error=np.asarray(continuum_error),
            line_error=np.asarray(line_error))


    return ScoutResult(luminosity = luminosity, z=z, expected_lag = lag / (1+z), recovered_lags = recovered_lags, iccf_results = iccf_results, 
                       parameters = dict(N = N, baseline = baseline, cadence = cadence, sn=sn, relation = relation, relation_kwargs = relation_kwargs),
                       light_curves = light_curves, light_curve_file=save_light_curves if save_light_curves != 'memory' else None)
