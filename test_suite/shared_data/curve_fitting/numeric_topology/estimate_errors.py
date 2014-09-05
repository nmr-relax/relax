# Calculate the R and I0 errors via bootstrapping.
# As this is an exact solution, bootstrapping is identical to Monte Carlo simulations.

# Python module imports.
from minfx.generic import generic_minimise
from numpy import array, arange, asarray, diag, dot, exp, eye, float64, isfinite, log, nan_to_num, multiply, ones, sqrt, sum, std, transpose, where, zeros
from numpy.linalg import inv, qr
from numpy.ma import fix_invalid
from random import gauss, sample, randint, randrange
from collections import OrderedDict

# relax module imports.
from lib.compat import pickle

# Should warnings be raised to errors?
raise_warnings = False

if raise_warnings:
    import warnings
    warnings.filterwarnings('error')

# Create and ordered dict, which can be looped over.
dic = OrderedDict()

# The real parameters.
R = 1.0
I0 = 1000.0
params = array([R, I0], float64)

# Number if R2eff points
np = 40

# Number of simulations.
sim = 2000

# Create number of timepoints. Between 3 and 10 for exponential curve fitting.
# Used in random.randint, and includes both end points.
nt_min = 3

# Loop over nt_max_list.
nt_max_list = [5, 10]

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
dic['np'] = np
dic['sim'] = sim
dic['nt_min'] = nt_min
dic['nt_max_list'] = nt_max_list
dic['all_times'] = all_times
dic['I_err_level'] = I_err_level
dic['I_err_std'] = I_err_std
dic['all_errors'] = all_errors

# Write to pickle.
pickle.dump( dic, open( "estimate_errors_data_settings.cp", "wb" ) )

# Minfx settings
#min_algor = 'simplex'
min_algor = 'BFGS'
min_options = ()

# Make global counters
global np_i
np_i = 0
global sim_j
sim_j = 0

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
    return chi2(data=I, back_calc=back_calc, errors=errors, params=params)

def func_exp_chi2_grad(params=None, times=None, I=None, errors=None):
    """Target function for the gradient (Jacobian matrix) to minfx, for exponential fit ."""

    # Get the back calc.
    back_calc = func_exp(params=params, times=times)
    # Get the Jacobian, with partial derivative, with respect to r2eff and i0.
    exp_grad = func_exp_grad(params=params, times=times)
    # Transpose back, to get rows.
    exp_grad_t = transpose(exp_grad)
    # n is number of fitted parameters.
    n = len(params)
    # Define array to update parameters in.
    jacobian_chi2_minfx = zeros([n])
    # Update value elements.
    dchi2(dchi2=jacobian_chi2_minfx, M=n, data=I, back_calc_vals=back_calc, back_calc_grad=exp_grad_t, errors=errors)
    # Return Jacobian matrix.
    return jacobian_chi2_minfx

def chi2(data=None, back_calc=None, errors=None, params=None):
    """Function to calculate the chi-squared value."""

    # Calculate the chi-squared statistic.
    if raise_warnings:
        try:
            t_chi2 = sum((1.0 / errors * (data - back_calc))**2)
        except RuntimeWarning:
            # Handle if algorithm takes wrong step.
            #print "Oppps. np=%i, sim=%i, R2=%3.2f, I0=%3.2f" % (np_i, sim_j, params[0], params[1])
            t_chi2 =  1e100
    else:
        t_chi2 = sum((1.0 / errors * (data - back_calc))**2)
        #fix_invalid(t_chi2, copy=False, fill_value=1e100)
        #t_chi2 = nan_to_num( t_chi2 )
        if not isfinite(t_chi2):
            t_chi2_2 = nan_to_num( t_chi2 )
            #print "Oppps. np=%i, sim=%i, R2=%3.2f, I0=%3.2f %s %s" % (np_i, sim_j, params[0], params[1], t_chi2, t_chi2_2)
            t_chi2 = t_chi2_2

    return t_chi2

def dchi2(dchi2, M, data, back_calc_vals, back_calc_grad, errors):
    """Calculate the full chi-squared gradient."""
    # Calculate the chi-squared gradient.
    grad = -2.0 * dot(1.0 / (errors**2) * (data - back_calc_vals), transpose(back_calc_grad))
    # Pack the elements.
    for i in range(M):
        dchi2[i] = grad[i]

def func_exp_grad(params=None, times=None):
    """The gradient (Jacobian matrix) of func_exp for Co-variance calculation."""

    # Unpack the parameter values.
    r2eff = params[0]
    i0 = params[1]
    # Make partial derivative, with respect to r2eff.
    d_exp_d_r2eff = -i0 * times * exp(-r2eff * times)
    # Make partial derivative, with respect to i0.
    d_exp_d_i0 = exp(-r2eff * times)
    # Define Jacobian as m rows with function derivatives and n columns of parameters.
    jacobian_matrix_exp = transpose(array( [d_exp_d_r2eff, d_exp_d_i0] ) )
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

def prod_I_errors(I=None, errors=None):
    I_err = []
    for j, error in enumerate(errors):
        I_error = gauss(I[j], error)
        I_err.append(I_error)
    # Convert to numpy array.
    I_err = asarray(I_err)
    return I_err


########### Do simulations ##################################

for nt_max in nt_max_list:
    # Create and ordered dict, which can be looped over.
    dic = OrderedDict()

    # Should we do random number of timepoints?
    if nt_max == 5:
        do_random_nr_time_points = False
    else:
        do_random_nr_time_points = True

    dic['do_random_nr_time_points'] = do_random_nr_time_points

    # Loop over number of R2eff points.
    for i in range(np):
        # Create index in dic.
        dic[i] = OrderedDict()
        # Assign to global counter
        np_i = i

        # Create random number of timepoints. Between 3 and 10 for exponential curve fitting.
        if do_random_nr_time_points:
            nt = randint(nt_min, nt_max)
        else:
            nt = nt_max
        dic[i]['nt'] = nt

        print("R2eff point %s with %i timepoints. Random timepoints=%s" % (i, nt, do_random_nr_time_points))

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
        I_err = prod_I_errors(I=I, errors=errors)
        dic[i]['I_err'] = I_err

        # Now estimate with no weighting.
        R_e, I0_e = est_x0_exp(times=times, I=I_err)
        dic[i]['R_e'] = R_e
        dic[i]['I0_e'] = I0_e

        # Now estimate with weighting.
        R_ew, I0_ew = est_x0_exp_weight(times=times, I=I_err, errors=errors)
        dic[i]['R_ew'] = R_ew
        dic[i]['I0_ew'] = I0_ew

        # Now estimate errors for parameters.
        sigma_R = point_r2eff_err(times=times, I=I_err, errors=errors)
        dic[i]['sigma_R'] = sigma_R

        # Minimisation.
        args = (times, I_err, errors)
        x0 = array([R_e, I0_e])

        params_minfx, chi2_minfx, iter_count, f_count, g_count, h_count, warning = generic_minimise(func=func_exp_chi2, dfunc=func_exp_chi2_grad, args=args, x0=x0, min_algor=min_algor, min_options=min_options, full_output=True, print_flag=0)
        R_m, I0_m = params_minfx
        dic[i]['R_m'] = R_m
        dic[i]['I0_m'] = I0_m

        # Estimate errors from Jacobian
        jacobian = func_exp_grad(params=params_minfx, times=times)
        dic[i]['jacobian'] = jacobian
        weights = 1. / errors**2
        dic[i]['weights'] = weights

        # Covariance matrix.
        pcov = multifit_covar(J=jacobian, weights=weights)
        dic[i]['pcov'] = pcov
        sigma_R_covar, sigma_I0_covar = sqrt(diag(pcov))
        dic[i]['sigma_R_covar'] = sigma_R_covar
        dic[i]['sigma_I0_covar'] = sigma_I0_covar

        # Now do Monte Carlo simulations.
        R_m_sim_l = []
        I0_m_sim_l = []
        for j in range(sim):
            if j in range(0, 100000, 100):
                print("Simulation %i"%j)
            # Create index in dic.
            # We dont want to store simulations, as they eat to much disk space.
            #dic[i][j] = OrderedDict()
            # Assign to global counter.
            sim_j = j

            # Now produce Simulated intensity with errors.
            I_err_sim_j = prod_I_errors(I=I_err, errors=errors)

            # Start minimisation.
            args = (times, I_err_sim_j, errors)
            x0 = params_minfx

            params_minfx_sim_j, chi2_minfx_sim_j, iter_count, f_count, g_count, h_count, warning = generic_minimise(func=func_exp_chi2, dfunc=func_exp_chi2_grad, args=args, x0=x0, min_algor=min_algor, min_options=min_options, full_output=True, print_flag=0)
            R_m_sim_j, I0_m_sim_j = params_minfx_sim_j
            R_m_sim_l.append(R_m_sim_j)
            I0_m_sim_l.append(I0_m_sim_j)
            #dic[i][j]['R_m_sim'] = R_m_sim
            #dic[i][j]['I0_m_sim'] = I0_m_sim

        # Get stats on distribution.
        sigma_R_sim = std(asarray(R_m_sim_l))
        sigma_I0_sim = std(asarray(I0_m_sim_l))
        dic[i]['sigma_R_sim'] = sigma_R_sim
        dic[i]['sigma_I0_sim'] = sigma_I0_sim

    # Write to pickle.
    pickle.dump( dic, open( "estimate_errors_data_nt%i.cp"%nt_max, "wb" ) )
