###############################################################################
#                                                                             #
# Copyright (C) 2014 Troels E. Linnet                                         #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Target functions for relaxation exponential curve fitting with both minfx and scipy.optimize.leastsq."""

# Python module imports.
from copy import deepcopy
from numpy import asarray, diag, dot, exp, inf, log, sqrt, sum, zeros
from minfx.generic import generic_minimise
import sys
from warnings import warn

# relax module imports.
from dep_check import scipy_module
from lib.text.sectioning import section, subsection
from pipe_control.mol_res_spin import generate_spin_string, spin_loop
from pipe_control.spectrum import error_analysis
from specific_analyses.relax_disp.checks import check_model_type
from specific_analyses.relax_disp.data import average_intensity, loop_exp_frq_offset_point, loop_frq, loop_time, return_param_key_from_data
from specific_analyses.relax_disp.parameters import disassemble_param_vector
from specific_analyses.relax_disp.variables import MODEL_R2EFF
from target_functions.chi2 import chi2_rankN

# Scipy installed.
if scipy_module:
    # Import leastsq.
    from scipy.optimize import leastsq


class Exponential:
    def __init__(self, num_params=2, num_times=None, values=None, sd=None, relax_times=None, scaling_matrix=None, constraints=None):
        """Relaxation dispersion target functions for minimisation.

        This class contains minimisation functions for both minfx and scipy.optimize.leastsq.
        """

    def setup(self, num_params=2, num_times=None, values=None, sd=None, relax_times=None, scaling_matrix=None, constraints=False, func_tol=1e-25, grad_tol=None, max_iterations=10000000, verbosity=1):
        """Setup for minimisation with minfx.

        @keyword num_param:         The number of parameters in the model.
        @type num_param:            int
        @keyword num_times:         The number of time points.
        @type num_times:            int
        @keyword values:            The measured intensity values per time point.
        @type values:               numpy array
        @keyword sd:                The standard deviation of the measured intensity values per time point.
        @type sd:                   numpy array
        @keyword relax_times:       The time points.
        @type relax_times:          numpy array
        @keyword scaling_matrix:    The square and diagonal scaling matrix.
        @type scaling_matrix:       numpy rank-2 float array
        @keyword constraints:       If constraints should be used.
        @type constraints:          bool
        @keyword func_tol:          The function tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
        @type func_tol:             None or float
        @keyword grad_tol:          The gradient tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
        @type grad_tol:             None or float
        @keyword max_iterations:    The maximum number of iterations for the algorithm.
        @type max_iterations:       int
        @keyword verbosity:         The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:            int
        """

        # Store variables.
        self.num_params = num_params
        self.num_times = num_times

        self.values = values
        self.errors = sd
        self.relax_times = relax_times
        self.scaling_matrix = scaling_matrix

        # Scaling initialisation.
        self.scaling_flag = False
        if self.scaling_matrix != None:
            self.scaling_flag = True

        # Settings to minfx.
        self.func_tol = func_tol
        self.grad_tol = grad_tol
        self.max_iterations = max_iterations
        self.verbosity = verbosity

        # Define which constraints should be used.
        self.constraints = constraints

        if self.constraints:
            self.min_algor = 'Log barrier'
            self.min_options = ('simplex',)
            self.A = array([ [ 1.,  0.],
                        [-1.,  0.],
                        [ 0.,  1.]] )
            self.b = array([   0., -200.,    0.])

        else:
            self.min_algor = 'simplex'
            self.min_options = ()
            self.A = None
            self.b = None

        # Create the structure for holding the back-calculated R2eff values (matching the dimensions of the values structure).
        self.back_calc = deepcopy(self.values)

        # Define function to minimise for minfx.
        self.func = self.func_exp


    def calc_exp(self, times=None, r2eff=None, i0=None):
        """Calculate the function values of exponential function.

        @keyword times: The time points.
        @type times:    numpy array
        @keyword r2eff: The effective transversal relaxation rate.
        @type r2eff:    float
        @keyword i0:    The initial intensity.
        @type i0:       float
        @return:        The function values.
        @rtype:         float
        """

        # Calculate.
        return i0 * exp( -times * r2eff)


    def estimate_x0_exp(self, intensities=None, times=None):
        """Estimate starting parameter x0 = [r2eff_est, i0_est], by converting the exponential curve to a linear problem.
         Then solving by linear least squares of: ln(Intensity[j]) = ln(i0) - time[j]* r2eff.

        @keyword intensities:   The measured intensity values per time point.
        @type intensities:      numpy array
        @keyword times:         The time points.
        @type times:            numpy array
        @return:                The list with estimated r2eff and i0 parameter for optimisation, [r2eff_est, i0_est]
        @rtype:                 list
        """

        # Convert to linear problem.
        w = log(intensities)
        x = - 1. * times
        n = len(times)

        # Solve by linear least squares.
        b = (sum(x*w) - 1./n * sum(x) * sum(w) ) / ( sum(x**2) - 1./n * (sum(x))**2 )
        a = 1./n * sum(w) - b * 1./n * sum(x)

        # Convert back from linear to exp function. Best estimate for parameter.
        r2eff_est = b
        i0_est = exp(a)

        # Return.
        return [r2eff_est, i0_est]


    def calc_exp_chi2(self, r2eff=None, i0=None):
        """Calculate the chi-squared value of exponential function.


        @keyword r2eff: The effective transversal relaxation rate.
        @type r2eff:    float
        @keyword i0:    The initial intensity.
        @type i0:       float
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Calculate.
        self.back_calc[:] = self.calc_exp(times=self.relax_times, r2eff=r2eff, i0=i0)

        # Return the total chi-squared value.
        return chi2_rankN(data=self.values, back_calc_vals=self.back_calc, errors=self.errors)


    def func_exp(self, params):
        """Target function for exponential fit in minfx.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        r2eff = params[0]
        i0 = params[1]

        # Calculate and return the chi-squared value.
        return self.calc_exp_chi2(r2eff=r2eff, i0=i0)


    def func_exp_general(self, params, times, intensities):
        """Target function for minimisation with scipy.optimize.leastsq.

        @param params:          The vector of parameter values.
        @type params:           numpy rank-1 float array
        @keyword times:         The time points.
        @type times:            numpy array
        @keyword intensities:   The measured intensity values per time point.
        @type intensities:      numpy array
        @return:                The difference between function evaluation with fitted parameters and measured values.
        @rtype:                 numpy array
        """

        # Return
        return self.calc_exp(times, *params) - intensities


    def func_exp_weighted_general(self, params, times, intensities, weights):
        """Target function for weighted minimisation with scipy.optimize.leastsq.

        @param params:          The vector of parameter values.
        @type params:           numpy rank-1 float array
        @keyword times:         The time points.
        @type times:            numpy array
        @keyword intensities:   The measured intensity values per time point.
        @type intensities:      numpy array
        @keyword weights:       The weights to multiply the function evaluation.  Should be supplied as '1/sd', where sd is the standard deviation of the measured intensity values.
        @type weights:          numpy array
        @return:                The weighted difference between function evaluation with fitted parameters and measured values.
        @rtype:                 numpy array
        """

        # Return
        return weights * (self.calc_exp(times, *params) - intensities)

#scipy.optimize.leastsq
def estimate_r2eff(spin_id=None, ftol=1e-15, xtol=1e-15, maxfev=10000000, factor=100.0, method='minfx', verbosity=1):
    """Estimate r2eff and errors by exponential curve fitting with scipy.optimize.leastsq.

    scipy.optimize.leastsq is a wrapper around MINPACK's lmdif and lmder algorithms.

    MINPACK is a FORTRAN90 library which solves systems of nonlinear equations, or carries out the least squares minimization of the residual of a set of linear or nonlinear equations.

    Errors are calculated by taking the square root of the reported co-variance.

    This can be an huge time saving step, when performing model fitting in R1rho.
    Errors of R2eff values, are normally estimated by time-consuming Monte-Carlo simulations.

    Initial guess for the starting parameter x0 = [r2eff_est, i0_est], is by converting the exponential curve to a linear problem.
    Then solving initial guess by linear least squares of: ln(Intensity[j]) = ln(i0) - time[j]* r2eff.


    @keyword spin_id:           The spin identification string.
    @type spin_id:              str
    @keyword ftol:              The function tolerance for the relative error desired in the sum of squares, parsed to leastsq.
    @type ftol:                 float
    @keyword xtol:              The error tolerance for the relative error desired in the approximate solution, parsed to leastsq.
    @type xtol:                 float
    @keyword maxfev:            The maximum number of function evaluations, parsed to leastsq.  If zero, then 100*(N+1) is the maximum function calls.  N is the number of elements in x0=[r2eff, i0].
    @type maxfev:               int
    @keyword factor:            The initial step bound, parsed to leastsq.  It determines the initial step bound (''factor * || diag * x||'').  Should be in the interval (0.1, 100).
    @type factor:               float
    @keyword method:            The method to minimise and estimate errors.  Options are: 'scipy.optimize.leastsq' or 'minfx'.
    @type method:               string
    @keyword verbosity:         The amount of information to print.  The higher the value, the greater the verbosity.
    @type verbosity:            int
    """

    # Perform checks.
    check_model_type(model=MODEL_R2EFF)

    # Set list with scipy setting.
    scipy_settings = [ftol, xtol, maxfev, factor]

    # Initialise target function class, to access functions.
    exp_class = Exponential()

    # Check if intensity errors have already been calculated by the user.
    precalc = True
    for cur_spin, mol_name, resi, resn, cur_spin_id in spin_loop(selection=spin_id, full_info=True, return_id=True, skip_desel=True):
        # No structure.
        if not hasattr(cur_spin, 'peak_intensity_err'):
            precalc = False
            break

        # Determine if a spectrum ID is missing from the list.
        for id in cdp.spectrum_ids:
            if id not in cur_spin.peak_intensity_err:
                precalc = False
                break

    # If no error analysis of peak heights exists.
    if not precalc:
        # Printout.
        section(file=sys.stdout, text="Error analysis", prespace=2)

        # Loop over the spectrometer frequencies.
        for frq in loop_frq():
            # Generate a list of spectrum IDs matching the frequency.
            ids = []
            for id in cdp.spectrum_ids:
                # Check that the spectrometer frequency matches.
                match_frq = True
                if frq != None and cdp.spectrometer_frq[id] != frq:
                    match_frq = False

                # Add the ID.
                if match_frq:
                    ids.append(id)

            # Run the error analysis on the subset.
            error_analysis(subset=ids)

    # Loop over the spins.
    for cur_spin, mol_name, resi, resn, cur_spin_id in spin_loop(selection=spin_id, full_info=True, return_id=True, skip_desel=True):
        # Generate spin string.
        spin_string = generate_spin_string(spin=cur_spin, mol_name=mol_name, res_num=resi, res_name=resn)

        # Print information.
        if verbosity >= 1:
            # Individual spin block section.
            top = 2
            if verbosity >= 2:
                top += 2
            subsection(file=sys.stdout, text="Fitting with scipy.optimize.leastsq to: %s"%spin_string, prespace=top)

        # Loop over each spectrometer frequency and dispersion point.
        for exp_type, frq, offset, point, ei, mi, oi, di in loop_exp_frq_offset_point(return_indices=True):
            # The parameter key.
            param_key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

            # The peak intensities, errors and times.
            values = []
            errors = []
            times = []
            for time in loop_time(exp_type=exp_type, frq=frq, offset=offset, point=point):
                values.append(average_intensity(spin=cur_spin, exp_type=exp_type, frq=frq, offset=offset, point=point, time=time))
                errors.append(average_intensity(spin=cur_spin, exp_type=exp_type, frq=frq, offset=offset, point=point, time=time, error=True))
                times.append(time)

            # Convert to numpy array.
            values = asarray(values)
            errors = asarray(errors)
            times = asarray(times)

            # Get the result based on method.
            if method == 'scipy.optimize.leastsq':
                results = minimise_leastsq(exp_class=exp_class, scipy_settings=scipy_settings, values=values, errors=errors, times=times)
            elif method == 'minfx':
                # Initialise the function to minimise.
                exp_class.setup(num_params=2, num_times=len(times), values=values, sd=errors, relax_times=times, func_tol=ftol, max_iterations=maxfev, verbosity=verbosity)

                # Acquire results.
                results = minimise_minfx(exp_class=exp_class, values=values, errors=errors, times=times)
            else:
                raise RelaxError("Method for minimisation not known. Try setting: method='scipy.optimize.leastsq'.")

            # Unpack results
            param_vector, param_vector_error, chi2, iter_count, f_count, g_count, h_count, warning = results

            # Extract values.
            r2eff = param_vector[0]
            i0 = param_vector[1]
            r2eff_err = param_vector_error[0]
            i0_err = param_vector_error[1]

            # Disassemble the parameter vector.
            disassemble_param_vector(param_vector=param_vector, spins=[cur_spin], key=param_key)

            # Errors.
            if not hasattr(cur_spin, 'r2eff_err'):
                setattr(cur_spin, 'r2eff_err', deepcopy(getattr(cur_spin, 'r2eff')))
            if not hasattr(cur_spin, 'i0_err'):
                setattr(cur_spin, 'i0_err', deepcopy(getattr(cur_spin, 'i0')))

            # Set error.
            cur_spin.r2eff_err[param_key] = r2eff_err
            cur_spin.i0_err[param_key] = i0_err

            # Chi-squared statistic.
            cur_spin.chi2 = chi2

            # Iterations.
            cur_spin.f_count = f_count

            # Warning.
            cur_spin.warning = warning

            # Print information.
            print_strings = []
            if verbosity >= 1:
                # Add print strings.
                point_info = "%s at %3.1f MHz, for offset=%3.3f ppm and dispersion point %-5.1f, with %i time points." % (exp_type, frq/1E6, offset, point, len(times))
                print_strings.append(point_info)

                par_info = "r2eff=%3.3f r2eff_err=%3.3f, i0=%6.1f, i0_err=%3.3f, chi2=%3.3f.\n" % ( r2eff, r2eff_err, i0, i0_err, chi2)
                print_strings.append(par_info)

                if verbosity >= 2:
                    time_info = ', '.join(map(str, times))
                    print_strings.append('For time array: '+time_info+'.\n\n')

            # Print info
            if len(print_strings) > 0:
                for print_string in print_strings:
                    print(print_string),


def minimise_leastsq(exp_class=None, scipy_settings=None, values=None, errors=None, times=None):
    """Estimate r2eff and errors by exponential curve fitting with scipy.optimize.leastsq.

    @keyword exp_class:         The class instance object, which contains functions to calculate with.
    @type exp_class:            class
    @keyword scipy_settings:    The parsed setting to leastsq.  scipy_settings = [ftol, xtol, maxfev, factor]
    @type scipy_settings:       list of float, float, int, float
    @keyword values:            The measured intensity values per time point.
    @type values:               numpy array
    @keyword errors:            The standard deviation of the measured intensity values per time point.
    @type errors:               numpy array
    @keyword times:             The time points.
    @type times:                numpy array
    @return:                    Packed list with optimised parameter, estimated parameter error, chi2, iter_count, f_count, g_count, h_count, warning
    @rtype:                     list
    """

    # Check that scipy.optimize.leastsq is available.
    if not scipy_module:
        raise RelaxError("scipy module is not available.")

    # Unpack settings:
    ftol, xtol, maxfev, factor = scipy_settings

    # Initial guess for minimisation. Solved by linear least squares.
    x0 = exp_class.estimate_x0_exp(intensities=values, times=times)

    # Define function to minimise. Use errors as weights in the minimisation.
    use_weights = True

    # If 'sigma'/erros describes one standard deviation errors of the input data points. The estimated covariance in 'pcov' is based on these values.
    absolute_sigma = True

    if use_weights:
        func = exp_class.func_exp_weighted_general
        weights = 1.0 / asarray(errors)
        args=(times, values, weights)
    else:
        func = exp_class.func_exp_general
        args=(times, values)

    # Call scipy.optimize.leastsq.
    popt, pcov, infodict, errmsg, ier = leastsq(func=func, x0=x0, args=args, full_output=True, ftol=ftol, xtol=xtol, maxfev=maxfev, factor=factor)

    # Catch errors:
    if ier in [1, 2, 3, 4]:
        warning = None
    elif ier in [9]:
        warn(RelaxWarning("%s." % errmsg))
        warning = errmsg
    elif ier in [0, 5, 6, 7, 8]:
        raise RelaxError("scipy.optimize.leastsq raises following error: '%s'." % errmsg)

    # 'nfev' number of function calls.
    f_count = infodict['nfev']

    # 'fvec': function evaluated at the output.
    fvec = infodict['fvec']
    #fvec_test = func(popt, times, values)

    # 'fjac': A permutation of the R matrix of a QR factorization of the final approximate Jacobian matrix, stored column wise. Together with ipvt, the covariance of the estimate can be approximated.
    # fjac = infodict['fjac']

    # 'qtf': The vector (transpose(q) * fvec).
    # qtf = infodict['qtf']

    # 'ipvt'  An integer array of length N which defines a permutation matrix, p, such that fjac*p = q*r, where r is upper triangular
    # with diagonal elements of nonincreasing magnitude. Column j of p is column ipvt(j) of the identity matrix.

    # Back calc fitted curve.
    back_calc = exp_class.calc_exp(times=times, r2eff=popt[0], i0=popt[1])

    # Calculate chi2.
    chi2 = chi2_rankN(data=values, back_calc_vals=back_calc, errors=errors)

    # 'pcov': The estimated covariance of popt.
    # The diagonals provide the variance of the parameter estimate.

    if pcov is None:
        # indeterminate covariance
        pcov = zeros((len(popt), len(popt)), dtype=float)
        pcov.fill(inf)
    elif not absolute_sigma:
        if len(values) > len(x0):
            s_sq = sum( fvec**2 ) / (len(values) - len(x0))
            pcov = pcov * s_sq
        else:
            pcov.fill(inf)

    # To compute one standard deviation errors on the parameters, take the square root of the diagonal covariance.
    perr = sqrt(diag(pcov))

    # Return as standard from minfx.
    param_vector = popt
    param_vector_error = perr

    iter_count = 0
    g_count = 0
    h_count = 0

    # Pack to list.
    results = [param_vector, param_vector_error, chi2, iter_count, f_count, g_count, h_count, warning]

    # Return, including errors.
    return results


def minimise_minfx(exp_class=None, values=None, errors=None, times=None):
    """Estimate r2eff and errors by minimising with minfx.

    @keyword exp_class:         The class instance object, which contains functions to calculate with.
    @type exp_class:            class
    @keyword values:            The measured intensity values per time point.
    @type values:               numpy array
    @keyword errors:            The standard deviation of the measured intensity values per time point.
    @type errors:               numpy array
    @keyword times:             The time points.
    @type times:                numpy array
    @return:                    Packed list with optimised parameter, estimated parameter error, chi2, iter_count, f_count, g_count, h_count, warning
    @rtype:                     list
    """

    # Initial guess for minimisation. Solved by linear least squares.
    x0 = asarray(exp_class.estimate_x0_exp(intensities=values, times=times))

    # Minimise with minfx.
    results_minfx = generic_minimise(func=exp_class.func, args=(), x0=x0, min_algor=exp_class.min_algor, min_options=exp_class.min_options, func_tol=exp_class.func_tol, grad_tol=exp_class.grad_tol, maxiter=exp_class.max_iterations, A=exp_class.A, b=exp_class.b, full_output=True, print_flag=exp_class.verbosity)

    # Unpack
    param_vector, chi2, iter_count, f_count, g_count, h_count, warning = results_minfx

    # Set error to inf.
    param_vector_error = [inf, inf]

    # Pack to list.
    results = [param_vector, param_vector_error, chi2, iter_count, f_count, g_count, h_count, warning]

    # Return, including errors.
    return results
