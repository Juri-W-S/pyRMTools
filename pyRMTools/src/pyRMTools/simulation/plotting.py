import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from .relations import linear_rl
from matplotlib.ticker import FuncFormatter
from .algorithm import generate_lc, generate_observations, downsample_lc
from .relations import structure_function

class ScoutPlotter:

    def __init__(self, result):
        self.result = result

    def bias_histogram(self, ax = None):

        if ax is None:
            fig, ax = plt.subplots(figsize = (10,8))
        ax.hist(self.result.bias_distribution, 100, color = '#0e48c3')
        ax.axvline(np.median(self.result.bias_distribution), label = 'Median bias', color = '#fc0cff', ls = 'dashed', lw = 1)
        ax.axvline(np.percentile(self.result.bias_distribution, 16), label = '16th percentile', color = '#ff830c', ls = 'dashed', lw = 1)
        ax.axvline(np.percentile(self.result.bias_distribution, 84), label = '84th percentile', color = '#ff830c', ls = 'dashed', lw = 1)
        ax.legend(loc = 'best')
        ax.set_xlabel('bias')
        ax.set_ylabel('Counts')
        ax.tick_params(axis = 'x', direction = 'out')
        ax.tick_params(axis = 'y', direction = 'in')
        if ax.figure.get_axes() == [ax]:
            plt.show()

    def rl_plane(self, ax = None):
        luminosities = np.linspace(self.result.luminosity/1e2, self.result.luminosity*1e2, 100)
        relation = self.result.parameters['relation']
        kwargs = self.result.parameters['relation_kwargs']
        lags = relation(luminosities, **kwargs)
        
        if ax is None:
            fig, ax = plt.subplots(figsize = (10,8))

        ax.errorbar(self.result.luminosity / 1e44, self.result.lag, yerr = [[self.result.error_minus], [self.result.error_plus]], label = 'Simulated result', fmt = 'x', elinewidth=1, capsize = 3, color = '#fc0cff')
        ax.scatter(self.result.luminosity / 1e44, self.result.expected_lag , marker = r'$\Delta$', label = 'Expected result', color = '#0e48c3', s = 100)
        ax.plot(luminosities / 1e44, lags, label = 'Reference R-L relation', color = '#0e48c3')
        ax.legend(loc = 'best')
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel(r'L$_{\rm cont}$ [erg/s]')
        ax.set_ylabel('R [light days]')
        ax.tick_params(which='major', direction='in')
        ax.tick_params(which='minor', direction='in')
        ax.xaxis.set_major_formatter(FuncFormatter(lambda val, pos: rf'$10^{{{int(np.log10(val*1e44))}}}$'))
        if ax.figure.get_axes() == [ax]:
            plt.show()

    def iccf(self, index = None):
        iccf = self.result.iccf_results
        fig, ax = plt.subplots(figsize = (10,8))
        if index is None:
            for i in range(len(iccf)):
                ax.plot(iccf[i].lag, iccf[i].r)
            ax.axvline(self.result.lag, label = 'median centroid', lw = 1)
        else:
            ax.plot(iccf[index].lag, iccf[index].r)
            ax.axvline(iccf[index].centroid, label = 'centroid')
        ax.legend(loc = 'best')
        ax.set_xlabel(r'$\tau$ [days]')
        ax.set_ylabel(r'Correlation')
        ax.tick_params(which='major', direction='in')
        plt.show()

    def light_curve(self, index = None):
        if self.result.light_curves is None:
            raise ValueError('No light curves are loaded. Load the files first, or run simulation in "memory" mode')
        fig, ax = plt.subplots(figsize = (10,8))
        if index is None:
            raise ValueError('Please provide a index to view the specific light curve')
        else:
            light_curve = self.result.light_curves[index]
            ax.plot(light_curve.t, light_curve.continuum_error, label = 'continuum', color = '#ad0ec3', marker = 'x')
            ax.plot(light_curve.t, light_curve.line_error, label = 'line', color = '#0c88ff', marker = 'x')
        ax.legend(loc = 'best')
        ax.set_xlabel('T [days]')
        ax.set_ylabel('Normalized flux')
        if ax.figure.get_axes() == [ax]:
            plt.show()

    
    def mock_light_curve(self, ax = None):
        rms = structure_function(self.result.z, self.result.luminosity, self.result.parameters['baseline']) / np.sqrt(2)
        time, cont, line = generate_lc(self.result.expected_lag*40, self.result.expected_lag, rms)
        t = generate_observations(self.result.parameters['baseline'], self.result.parameters['cadence'])
        contin = downsample_lc(t, time, cont)
        lines = downsample_lc(t, time, line)
        error_cs = np.abs(contin) / self.result.parameters['sn']   
        error_ls = np.abs(lines) / self.result.parameters['sn'] 
        if error_cs.any() == 0:
            error_cs += 1e-6
        if error_ls.any() == 0:
            error_ls += 1e-6
        cont_final = contin + np.random.normal(0,error_cs)
        line_final = lines + np.random.normal(0,error_ls)
        t_plot = generate_observations(self.result.parameters['baseline'], 0.5)
        cont_plot = downsample_lc(t_plot, time, cont)
        line_plot = downsample_lc(t_plot, time, line)
        if ax is None:
            fig, ax = plt.subplots(figsize = (10,8))
        ax.plot(t_plot, cont_plot, label = 'continuum curve', color = '#ad0ec3')
        ax.fill_between(t_plot, cont_plot - cont_plot/self.result.parameters['sn'] , cont_plot + cont_plot/self.result.parameters['sn'] , 
                        alpha = 0.3, label = 'continuum curve uncertainty', color = '#ad0ec3')
        ax.plot(t_plot, line_plot, label = 'line curve', color = '#0e48c3')
        ax.fill_between(t_plot, line_plot - line_plot/self.result.parameters['sn'] , line_plot + line_plot/self.result.parameters['sn'] , 
                        alpha = 1, label = 'line curve uncertainty', color = '#aad0f9')
        ax.scatter(t, cont_final, marker = 'x', label = 'continuum data', color = "#b40cff")
        ax.scatter(t, line_final, marker = 'x', label = 'line data', color = '#0c88ff')
        ax.set_xlabel('t [days]')
        ax.set_ylabel('Normalized flux')
        ax.legend(loc = 'best')
        if ax.figure.get_axes() == [ax]:
            plt.show()

    def view(self):
        fig = plt.figure(figsize = (10,8))

        gs = GridSpec(2, 2)
        ax1 = fig.add_subplot(gs[0,0])
        ax2 = fig.add_subplot(gs[0,1])
        ax3 = fig.add_subplot(gs[1,:])

        self.rl_plane(ax = ax1)
        self.bias_histogram(ax = ax2)
        self.mock_light_curve(ax = ax3)

        plt.tight_layout()

