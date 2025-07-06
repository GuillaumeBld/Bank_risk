"""
Manual Merton Model Solver for JPM.N 2016

This script runs the iterative Merton solver for JPM.N in 2016, printing each step.
"""
import numpy as np
from scipy.stats import norm

# Inputs for JPM.N 2016
T = 1.0
rf = 0.0020
E = 2.398077e11  # market_cap
F = 495354000.0  # debt__total
sigma_E = 0.238811  # equity_vol

tol = 1e-6
max_iter = 100

# Initial guesses
V = E + F
sigma_V = sigma_E

print(f"Initial values: V={V}, sigma_V={sigma_V}")

for i in range(max_iter):
    try:
        d1 = (np.log(V / F) + (rf + 0.5 * sigma_V ** 2) * T) / (sigma_V * np.sqrt(T))
        d2 = d1 - sigma_V * np.sqrt(T)
        E_calc = V * norm.cdf(d1) - F * np.exp(-rf * T) * norm.cdf(d2)
        sigma_E_calc = (V * norm.cdf(d1) * sigma_V) / E_calc if E_calc != 0 else np.nan
        print(f"Iter {i}: V={V:.2f}, sigma_V={sigma_V:.6f}, E_calc={E_calc:.2f}, sigma_E_calc={sigma_E_calc:.6f}")
        if np.abs(E - E_calc) < tol and np.abs(sigma_E - sigma_E_calc) < tol:
            print("Converged!")
            break
        V = V - (E_calc - E) * 0.5
        sigma_V = sigma_V - (sigma_E_calc - sigma_E) * 0.5
    except Exception as e:
        print(f"Error at iteration {i}: {e}")
        break
else:
    print("Did not converge after max iterations.")

print(f"Final: V={V}, sigma_V={sigma_V}")

# If converged, calculate DD and PD
if not (np.isnan(V) or np.isnan(sigma_V)):
    try:
        DD = (np.log(V / F) + (rf - 0.5 * sigma_V ** 2) * T) / (sigma_V * np.sqrt(T))
        PD = norm.cdf(-DD)
        print(f"Distance to Default (DD): {DD}")
        print(f"Probability of Default (PD): {PD}")
    except Exception as e:
        print(f"Error in DD/PD calculation: {e}") 