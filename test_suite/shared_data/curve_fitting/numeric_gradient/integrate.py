# Script for numerically calculating the exponential curve gradient.

# Python module imports.
from math import exp
from numpy import array, float64
from scipy.misc import derivative


def func_R(R):
    """Calculate the chi-squared value."""

    global times, I, I0, errors

    # The intensities.
    back_calc = []
    for i in range(len(times)):
        back_calc.append(I0 * exp(-R*times[i]))

    # The chi2.
    chi2 = 0.0
    for i in range(len(times)):
        chi2 += (I[i] - back_calc[i])**2 / errors[i]**2

    # Return the value.
    return chi2


def func_I(I0):
    """Calculate the chi-squared value."""

    global times, I, R, errors

    # The intensities.
    back_calc = []
    for i in range(len(times)):
        back_calc.append(I0 * exp(-R*times[i]))

    # The chi2.
    chi2 = 0.0
    for i in range(len(times)):
        chi2 += (I[i] - back_calc[i])**2 / errors[i]**2

    # Return the value.
    return chi2


# The real parameters.
R = 1.0
I0 = 1000.0

# The time points.
times = [0.0, 1.0, 2.0, 3.0, 4.0]

# The intensities for the above I0 and R.
I = [1000.0, 367.879441171, 135.335283237, 49.7870683679, 18.3156388887]

# The intensity errors.
errors = [10.0, 10.0, 10.0, 10.0, 10.0]

# The numeric gradient at the minimum.
grad_R = derivative(func_R, R, dx=1e-5, order=11)
grad_I = derivative(func_I, I0, dx=1e-5, order=11)
print("The gradient at %s is:\n    %s" % ([R, I0], [grad_R, grad_I]))

# The numeric gradient off the minimum.
R = 2.0
I0 = 500.0
grad_R = derivative(func_R, R, dx=1e-5, order=11)
grad_I = derivative(func_I, I0, dx=1e-5, order=11)
print("The gradient at %s is:\n    %s" % ([R, I0], [grad_R, grad_I]))
