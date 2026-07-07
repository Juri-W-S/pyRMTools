import numpy as np

def rl_relation(alpha, beta, L = None):
    return 10**(beta + alpha*np.log10(L/1e44))

def structure_function(z, L, baseline):
    return 0.079*(1+z)**0.15 * (L/1e46)**(-0.2) * (510/1000) ** (-0.44) * (baseline/365.25) ** 0.246