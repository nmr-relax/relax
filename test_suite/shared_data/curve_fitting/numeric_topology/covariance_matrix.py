# Script for numerically calculating the exponential curve covariance matrix via the Jacobian.
# The equation used is:  covar = inv(J^T.W.J)

# Python module imports.
from math import exp, sqrt
from numpy import array, dot, eye, float64, transpose
from numpy.linalg import inv
from numdifftools import Jacobian


def func(params):
    """Back-calculate the intensities."""

    global times, I, errors

    # Unpack the parameters.
    R, I0 = params

    # The intensities.
    back_calc = []
    for i in range(len(times)):
        back_calc.append(I0 * exp(-R*times[i]))

    # Return the back-calculated intensities.
    return array(back_calc)


# The real parameters.
R = 1.0
I0 = 1000.0

# The time points.
times = [0.0, 1.0, 2.0, 3.0, 4.0]

# The intensities for the above I0 and R.
I = [1000.0, 367.879441171, 135.335283237, 49.7870683679, 18.3156388887]

# The intensity errors.
errors = [10.0, 10.0, 10.0, 10.0, 10.0]

# The variance weighting matrix.
W = eye(len(errors))/(10.0**2)

# Set up the Jacobian function.
jacobian = Jacobian(func)

# The covariance matrix at the minimum.
print("\n\nOn-minimum:\n")
J = jacobian([R, I0])
covar = inv(dot(transpose(J), dot(W, J)))
print("The covariance matrix at %s is:\n%s" % ([R, I0], covar))
print("The parameter errors are therefore:")
print("    sigma_R:   %25.20f" % sqrt(covar[0, 0]))
print("    sigma_I0:  %25.20f" % sqrt(covar[1, 1]))

# The covariance matrix off the minimum.
print("\n\nOff-minimum:\n")
R = 2.0
I0 = 500.0
J = jacobian([R, I0])
covar = inv(dot(transpose(J), dot(W, J)))
print("The covariance matrix at %s is:\n%s" % ([R, I0], covar))
print("The parameter errors, which are rubbish as this is off-minimum, are therefore:")
print("    sigma_R:   %25.20f" % sqrt(covar[0, 0]))
print("    sigma_I0:  %25.20f" % sqrt(covar[1, 1]))
