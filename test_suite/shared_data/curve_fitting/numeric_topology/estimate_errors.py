# Calculate the R and I0 errors via bootstrapping.
# As this is an exact solution, bootstrapping is identical to Monte Carlo simulations.

# Python module imports.
from minfx.generic import generic_minimise
from numpy import array, arange, asarray, diag, dot, exp, eye, float64, log, multiply, ones, sqrt, sum, std, transpose, where
from numpy.linalg import inv, qr
from random import gauss, sample, randint, randrange
from collections import OrderedDict
#import pickle
import cPickle as pickle

# Create and ordered dict, which can be looped over.
dic = OrderedDict()

# The real parameters.
R = 1.0
I0 = 1000.0
params = array([R, I0], float64)

# Number of simulations.
sim = 10000

# Create number of timepoints. Between 3 and 10 for exponential curve fitting.
# Used in random.randint, and includes both end points.
nt_min = 3
nt_max = 10

# Produce range with all possible time points.
# Draw from this.
all_times = arange(0.1, 1.1, 0.1)

# Define error level on intensity.
# Intensity with errors at 1 % error level, which themselves fluctuates with 10%.
I_err_level = I0 / 100
I_err_std = I_err_level / 10

# Now produce range with all possible error sigmas.
all_errors = []
for j in range(len(all_times)):
    error = gauss( I_err_level, I_err_std)
    all_errors.append(error)

# Convert to numpy array.
all_errors = asarray(all_errors)

# Store to dic
dic['R'] = R
dic['I0'] = I0
dic['params'] = params
dic['sim'] = sim
dic['nt_min'] = nt_min
dic['nt_max'] = nt_max
dic['all_times'] = all_times
dic['I_err_level'] = I_err_level
dic['I_err_std'] = I_err_std
dic['all_errors'] = all_errors

########### Define functions ##################################

def func_exp(params=None, times=None):
    """Calculate the function values of exponential function."""
    # Unpack
    r2eff, i0 = params
    return i0 * exp( -times * r2eff)

def est_x0_exp(times=None, I=None):
    """Estimate starting parameter x0 = [R, I0], by converting the exponential curve to a linear problem.  Then solving by linear least squares of: ln(Intensity[j]) = ln(I0) - time[j]* R.
    """
    # Convert to linear problem.
    ln_I = log(I)
    x = - 1. * times
    n = len(times)
    # ln_I = R (-t) + ln(i0)
    # f(x) = a x + b 
    # Solve by linear least squares.
    a = (sum(x*ln_I) - 1./n * sum(x) * sum(ln_I) ) / ( sum(x**2) - 1./n * (sum(x))**2 )
    b = 1./n * sum(ln_I) - a * 1./n * sum(x)
    # Convert back from linear to exp function. Best estimate for parameter.
    R = a
    I0 = exp(b)
    # Return.
    return [R, I0]

def est_x0_exp_weight(times=None, I=None, errors=None):
    """Estimate starting parameter x0 = [R, I0], by converting the exponential curve to a linear problem.  Then solving by linear least squares of: ln(Intensity[j]) = ln(I0) - time[j]* R.
    """
    # Convert to linear problem.
    ln_I = log(I* 1. / errors)
    x = - 1. * times
    n = len(times)
    # ln_Iw = R (-t) + ln(i0 / errors)
    # f(x) = a x + b 
    # Solve by linear least squares.
    a = (sum(x*ln_I) - 1./n * sum(x) * sum(ln_I) ) / ( sum(x**2) - 1./n * (sum(x))**2 )
    b = 1./n * sum(ln_I) - a * 1./n * sum(x)
    # Convert back from linear to exp function. Best estimate for parameter.
    R = a
    I0 = exp(b) * errors
    # Return.
    return [R, I0]

def point_r2eff_err(times=None, I=None, errors=None):
    """Calculate the R2 error for relaxation time data.
                                  ______________________________________________________________________
                        1        / / sigma_I[1] \ 2     / sigma_I[2] \ 2            / sigma_I[n] \ 2
        sigma_R_i =  -------    /  | --------   |   +   | --------   |    +         | --------   | 
                     times[i] \/   \   I[1]     /       \    I[2]    /       ....   \    I[j]    /

    where n is number of time points.
    """
    sigma_R = []
    n = len(times)
    for i, time in enumerate(times):
        sigma_sum = 0
        for j in range(n):
            sigma_sum += (errors[j] / I[j])**2
        sqrt_sigma_sum = sqrt(sigma_sum)
        sigma_R_i = 1. / time * sqrt_sigma_sum
        sigma_R.append(sigma_R_i)
    return asarray(sigma_R)

def func_exp_chi2(params=None, times=None, I=None, errors=None):
    """Target function for minimising chi2 in minfx, for exponential fit."""

    # Calculate.
    back_calc = func_exp(params=params, times=times)
    # Calculate and return the chi-squared value.
    return chi2(data=I, back_calc=back_calc, errors=errors)

def chi2(data=None, back_calc=None, errors=None):
    """Function to calculate the chi-squared value."""

    # Calculate the chi-squared statistic.
    return sum((1.0 / errors * (data - back_calc))**2)

def func_exp_grad(params=None, times=None, errors=None):
    """The gradient (Jacobian matrix) of func_exp for Co-variance calculation."""

    # Unpack the parameter values.
    r2eff = params[0]
    i0 = params[1]
    # Make partial derivative, with respect to r2eff.
    d_exp_d_r2eff = -i0 * times * exp(-r2eff * times)
    # Make partial derivative, with respect to i0.
    d_exp_d_i0 = exp(-r2eff * times)
    # Define Jacobian as m rows with function derivatives and n columns of parameters.
    jacobian_matrix_exp = transpose(array( [d_exp_d_r2eff , d_exp_d_i0] ) )
    # Return Jacobian matrix.
    return jacobian_matrix_exp

def multifit_covar(J=None, weights=None):
    """This is the implementation of the multifit covariance."""
    # Make a square diagonal matrix.
    eye_mat = eye(weights.shape[0])
    # Form weight matrix.
    W = multiply(eye_mat, weights)
    # Calculate step by step, by matrix multiplication.
    Jt = transpose(J)
    Jt_W = dot(Jt, W)
    Jt_W_J = dot(Jt_W, J)
    # Invert matrix by QR decomposition.
    Q, R = qr(Jt_W_J)
    # Form the covariance matrix.
    Qxx = dot(inv(R), transpose(Q) )
    return Qxx


########### Do simulations ##################################

# Loop over sims.
for i in range(sim):
    # Create index in dic.
    dic[i] = OrderedDict()
    print("Simulation number %s"%i)

    # Create random number of timepoints. Between 3 and 10 for exponential curve fitting.
    nt = randint(nt_min, nt_max)
    dic[i]['nt'] = nt

    # Create time array, by drawing from the all time points array.
    times = asarray( sample(population=all_times, k=nt) )
    dic[i]['times'] = times

    # Get the indexes which was drawn from.
    indexes = []
    for time in times:
        indexes.append( int(where(time == all_times)[0]) )
    dic[i]['indexes'] = indexes

    # Draw errors from same indexes.
    errors = all_errors[indexes]
    dic[i]['errors'] = errors

    # Calculate the real intensity.
    I = func_exp(params=params, times=times)
    dic[i]['I'] = I

    # Now produce Intensity with errors.
    I_err = []
    for j, error in enumerate(errors):
        I_error = gauss(I[j], error)
        I_err.append(I_error)

    # Convert to numpy array.
    I_err = asarray(I_err)
    dic[i]['I_err'] = I_err

    # Now estimate with no weighting.
    R_e, I0_e = est_x0_exp(times=times, I=I_err)
    dic[i]['R_e'] = R_e
    dic[i]['I0_e'] = I0_e

    # Now estimate with weighting.
    R_ew, I0_ew = est_x0_exp_weight(times=times, I=I_err, errors=errors)
    dic[i]['R_ew'] = R_e
    dic[i]['I0_ew'] = I0_e

    # Now estimate errors for parameters.
    sigma_R = point_r2eff_err(times=times, I=I_err, errors=errors)
    dic[i]['sigma_R'] = sigma_R

    # Minimisation.
    args = (times, I_err, errors)
    min_algor = 'simplex'
    x0 = array([R_e, I0_e])

    params_minfx, chi2_minfx, iter_count, f_count, g_count, h_count, warning = generic_minimise(func=func_exp_chi2, args=args, x0=x0, min_algor=min_algor, full_output=True, print_flag=0)
    R_m, I0_m = params_minfx
    dic[i]['R_m'] = R_m
    dic[i]['I0_m'] = I0_m

    # Estimate errors from Jacobian
    jacobian = func_exp_grad(params=params, times=times, errors=errors)
    dic[i]['jacobian'] = jacobian
    weights = 1. / errors**2
    dic[i]['weights'] = weights

    # Covariance matrix.
    pcov = multifit_covar(J=jacobian, weights=weights)
    dic[i]['pcov'] = pcov
    sigma_R_p, sigma_I0_p = sqrt(diag(pcov))
    dic[i]['sigma_R_p'] = sigma_R_p
    dic[i]['sigma_I0_p'] = sigma_I0_p


# Write to pickle.
pickle.dump( dic, open( "estimate_errors.p", "wb" ) )