# Calculate the R and I0 errors via bootstrapping.
# As this is an exact solution, bootstrapping is identical to Monte Carlo simulations.

# Python module imports.
from math import exp
from minfx.generic import generic_minimise
from numpy import array, float64, std
from random import gauss


def func(params):
    """Calculate the chi-squared value."""

    global times, I_boot, errors

    # Unpack the parameters.
    R, I0 = params

    # The intensities.
    back_calc = []
    for i in range(len(times)):
        back_calc.append(I0 * exp(-R*times[i]))

    # The chi2.
    chi2 = 0.0
    for i in range(len(times)):
        chi2 += (I_boot[i] - back_calc[i])**2 / errors[i]**2

    # Return the value.
    return chi2


# The real parameters.
R = 1.0
I0 = 1000.0
params = array([R, I0], float64)

# The time points.
times = [0.0, 1.0, 2.0, 3.0, 4.0]

# The intensities for the above I0 and R.
I = [1000.0, 367.879441171, 135.335283237, 49.7870683679, 18.3156388887]

# The intensity errors.
errors = [10.0, 10.0, 10.0, 10.0, 10.0]

# Loop over the bootstrapping simulations.
SIMS = 200000
R_sim = []
I0_sim = []
for sim_index in range(SIMS):
    # Printout.
    if sim_index % 100 == 0:
        print("Simulation %i" % sim_index)

    # Randomise the data.
    I_boot = []
    for i in range(len(I)):
        I_boot.append(gauss(I[i], errors[i]))

    # Minimisation.
    xk, fk, k, f_count, g_count, h_count, warning = generic_minimise(func=func, x0=params, min_algor='simplex', print_flag=0, full_output=True)

    # Store the optimised parameters.
    R_sim.append(xk[0])
    I0_sim.append(xk[1])

# Errors.
R_err = std(array(R_sim))
I0_err = std(array(I0_sim))

# Printout.
print("\n\nParameter errors:")
print("sigma_R:   %25.20f" % R_err)
print("sigma_I0:  %25.20f" % I0_err)
