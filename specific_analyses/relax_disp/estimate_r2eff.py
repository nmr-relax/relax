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
from numpy import absolute, any, array, asarray, diag, dot, exp, eye, inf, log, multiply, spacing, sqrt, sum, transpose, zeros
from numpy.linalg import cond, inv, qr
from minfx.generic import generic_minimise
from re import match, search
import sys
from warnings import warn

# relax module imports.
from dep_check import C_module_exp_fn, scipy_module
from lib.errors import RelaxError
from lib.text.sectioning import section, subsection
from lib.warnings import RelaxWarning
from pipe_control.mol_res_spin import generate_spin_string, spin_loop
from pipe_control.spectrum import error_analysis
from specific_analyses.relax_disp.checks import check_model_type
from specific_analyses.relax_disp.data import average_intensity, loop_exp_frq_offset_point, loop_frq, loop_time, return_param_key_from_data
from specific_analyses.relax_disp.parameters import disassemble_param_vector
from specific_analyses.relax_disp.variables import MODEL_R2EFF
from target_functions.chi2 import chi2_rankN

# C modules.
if C_module_exp_fn:
    from specific_analyses.relax_fit.optimisation import func_wrapper, dfunc_wrapper, d2func_wrapper
    from target_functions.relax_fit import jacobian, setup
    # Call the python wrapper function to help with list to numpy array conversion.
    func = func_wrapper
    dfunc = dfunc_wrapper
    d2func = d2func_wrapper

# Scipy installed.
if scipy_module:
    # Import leastsq.
    from scipy.optimize import leastsq


def estimate_r2eff_err(spin_id=None, epsrel=0.0, verbosity=1):
    """This will estimate the R2eff and i0 errors from the covariance matrix Qxx.  Qxx is calculated from the Jacobian matrix and the optimised parameters.

    @keyword spin_id:       The spin identification string.
    @type spin_id:          str
    @param epsrel:          Any columns of R which satisfy |R_{kk}| <= epsrel |R_{11}| are considered linearly-dependent and are excluded from the covariance matrix, where the corresponding rows and columns of the covariance matrix are set to zero.
    @type epsrel:           float
    @keyword verbosity:     The amount of information to print.  The higher the value, the greater the verbosity.
    @type verbosity:        int
    """

    # Perform checks.
    check_model_type(model=MODEL_R2EFF)

    # Initialise class.
    E = Exp(verbosity=verbosity)

    # Loop over the spins.
    for cur_spin, mol_name, resi, resn, cur_spin_id in spin_loop(selection=spin_id, full_info=True, return_id=True, skip_desel=True):
        # Generate spin string.
        spin_string = generate_spin_string(spin=cur_spin, mol_name=mol_name, res_num=resi, res_name=resn)

        # Raise Error, if not optimised.
        if not (hasattr(cur_spin, 'r2eff') and hasattr(cur_spin, 'i0')):
            raise RelaxError("Spin %s does not contain optimised 'r2eff' and 'i0' values.  Try execute: minimise.execute(min_algor='Newton', constraints=False)"%(spin_string))

        # Raise warning, if gradient count is 0.  This could point to a lack of minimisation first.
        if hasattr(cur_spin, 'g_count'):
            if getattr(cur_spin, 'g_count') == 0.0:
                text = "Spin %s contains a gradient count of 0.0.  Is the R2eff parameter optimised?  Try execute: minimise.execute(min_algor='Newton', constraints=False)" %(spin_string)
                warn(RelaxWarning("%s." % text))

        # Print information.
        if verbosity >= 1:
            # Individual spin block section.
            top = 2
            if verbosity >= 2:
                top += 2
            subsection(file=sys.stdout, text="Estimating R2eff error for spin: %s"%spin_string, prespace=top)

        # Loop over each spectrometer frequency and dispersion point.
        for exp_type, frq, offset, point, ei, mi, oi, di in loop_exp_frq_offset_point(return_indices=True):
            # The parameter key.
            param_key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

            # Extract values.
            r2eff = getattr(cur_spin, 'r2eff')[param_key]
            i0 = getattr(cur_spin, 'i0')[param_key]

            # Pack data
            param_vector = [r2eff, i0]

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

            # Initialise data in Class.
            E.setup_data(values=values, errors=errors, times=times)

            # Initialise data in C code.
            scaling_list = [1.0, 1.0]
            setup(num_params=len(param_vector), num_times=len(times), values=values, sd=errors, relax_times=times, scaling_matrix=scaling_list)

            # Calculate the direct exponential Jacobian matrix from C code.
            jacobian_matrix_exp = transpose(asarray( jacobian(param_vector) ) )

            # Get the co-variance
            pcov = multifit_covar(J=jacobian_matrix_exp, errors=errors)

            # To compute one standard deviation errors on the parameters, take the square root of the diagonal covariance.
            param_vector_error = sqrt(diag(pcov))

            # Extract values.
            r2eff_err, i0_err = param_vector_error

            # Errors.
            if not hasattr(cur_spin, 'r2eff_err'):
                setattr(cur_spin, 'r2eff_err', deepcopy(getattr(cur_spin, 'r2eff')))
            if not hasattr(cur_spin, 'i0_err'):
                setattr(cur_spin, 'i0_err', deepcopy(getattr(cur_spin, 'i0')))

            # Set error.
            cur_spin.r2eff_err[param_key] = r2eff_err
            cur_spin.i0_err[param_key] = i0_err

            # Get other relevant information.
            chi2 = getattr(cur_spin, 'chi2')

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


def multifit_covar(J=None, epsrel=0.0, errors=None):
    """This is the implementation of the multifit covariance.

    This is inspired from GNU Scientific Library (GSL).

    This function uses the Jacobian matrix J to compute the covariance matrix of the best-fit parameters, covar.

    The parameter 'epsrel' is used to remove linear-dependent columns when J is rank deficient.

    The covariance matrix is given by,

        covar = (J^T J)^{-1}

    and is computed by QR decomposition of J with column-pivoting. Any columns of R which satisfy

        |R_{kk}| <= epsrel |R_{11}|

    are considered linearly-dependent and are excluded from the covariance matrix
    (the corresponding rows and columns of the covariance matrix are set to zero).

    If the minimisation uses the weighted least-squares function:

        f_i = (Y(x, t_i) - y_i) / \sigma_i

    then the covariance matrix above gives the statistical error on the best-fit parameters resulting from the Gaussian errors \sigma_i on the underlying data y_i.

    This can be verified from the relation \delta f = J \delta c and the fact that the fluctuations in f from the data y_i are normalised by \sigma_i
    and so satisfy <\delta f \delta f^T> = I.

    For an unweighted least-squares function f_i = (Y(x, t_i) - y_i) the covariance matrix above should be multiplied by
    the variance of the residuals about the best-fit

        \sigma^2 = \sum (y_i - Y(x, t_i))^2 / (n-p)

    to give the variance-covariance matrix \sigma^2 C.
    This estimates the statistical error on the best-fit parameters from the scatter of the underlying data.

    See:
    U{GSL - GNU Scientific Library<http://www.gnu.org/software/gsl/>}
    U{Manual: Overview<http://www.gnu.org/software/gsl/manual/gsl-ref_37.html#SEC510>}
    U{Manual: Computing the covariance matrix of best fit parameters<http://www.gnu.org/software/gsl/manual/gsl-ref_38.html#SEC528>}
    U{Other reference<http://www.orbitals.com/self/least/least.htm>}

    @param J:               The Jacobian matrix.
    @type J:                numpy array
    @param epsrel:          Any columns of R which satisfy |R_{kk}| <= epsrel |R_{11}| are considered linearly-dependent and are excluded from the covariance matrix, where the corresponding rows and columns of the covariance matrix are set to zero.
    @type epsrel:           float
    @keyword errors:        The standard deviation of the measured intensity values per time point.
    @type errors:           numpy array
    @return:                The co-variance matrix
    @rtype:                 square numpy array
    """

    # Weighting matrix. This is a square symmetric matrix.
    # For independent measurements, this is a diagonal matrix. Larger values indicate greater significance.

    # Make a square diagonal matrix.
    eye_mat = eye(errors.shape[0])

    # Now form the error matrix, with errors down the diagonal.
    weights = 1. / errors**2

    W = multiply(weights, eye_mat)

    # The covariance matrix (sometimes referred to as the variance-covariance matrix), Qxx, is defined as:
    # Qxx = (J^t W J)^(-1)

    # Calculate step by step, by matrix multiplication.
    Jt = transpose(J)
    Jt_W = dot(Jt, W)
    Jt_W_J = dot(Jt_W, J)

    # Invert matrix by QR decomposition, to check columns of R which satisfy: |R_{kk}| <= epsrel |R_{11}|
    Q, R = qr(Jt_W_J)

    # Make the state ment matrix.
    abs_epsrel_R11 = absolute( multiply(epsrel, R[0, 0]) )

    # Make and array of True/False statements.
    # These are considered linearly-dependent and are excluded from the covariance matrix.
    # The corresponding rows and columns of the covariance matrix are set to zero
    epsrel_check = absolute(R) <= abs_epsrel_R11

    # Form the covariance matrix.
    Qxx = dot(inv(R), transpose(Q) )
    #Qxx2 = dot(inv(R), inv(Q) )
    #print(Qxx - Qxx2)

    # Test direct invert matrix of matrix.
    #Qxx_test = inv(Jt_W_J)

    # Replace values in Covariance matrix with inf.
    Qxx[epsrel_check] = 0.0

    # Throw a warning, that some colums are considered linearly-dependent and are excluded from the covariance matrix.
    # Only check for the diagonal, since the that holds the variance.
    diag_epsrel_check = diag(epsrel_check)

    # If any of the diagonals does not meet the epsrel condition.
    if any(diag_epsrel_check):
        for i in range(diag_epsrel_check.shape[0]):
            abs_Rkk = absolute(R[i, i])
            if abs_Rkk <= abs_epsrel_R11:
                warn(RelaxWarning("Co-Variance element k,k=%i was found to meet |R_{kk}| <= epsrel |R_{11}|, meaning %1.1f <= %1.3f * %1.1f , and is therefore determined to be linearly-dependent and are excluded from the covariance matrix by setting the value to 0.0." % (i+1, abs_Rkk, epsrel, abs_epsrel_R11/epsrel) ))
                #print(cond(Jt_W_J) < 1./spacing(1.) )

    return Qxx


#### This class is only for testing.

class Exp:
    def __init__(self, verbosity=1):
        """Class for to set settings for minimisation and dispersion target functions for minimisation.

        This class contains minimisation functions for both minfx and scipy.optimize.leastsq.

        @keyword verbosity:         The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:            int
        """

        # Store.
        self.verbosity = verbosity

        # Initialize standard settings.
        self.set_settings_leastsq()
        self.set_settings_minfx()


    def setup_data(self, values=None, errors=None, times=None):
        """Setup for minimisation with minfx.

        @keyword values:            The measured intensity values per time point.
        @type values:               numpy array
        @keyword errors:            The standard deviation of the measured intensity values per time point.
        @type errors:               numpy array
        @keyword times:             The time points.
        @type times:                numpy array
        """

        # Store variables.
        self.values = values
        self.errors = errors
        self.times = times

        # Create the structure for holding the back-calculated R2eff values (matching the dimensions of the values structure).
        self.back_calc = deepcopy(self.values)


    def set_settings_leastsq(self, ftol=1e-15, xtol=1e-15, maxfev=10000000, factor=100.0):
        """Setup options to scipy.optimize.leastsq.

        @keyword ftol:              The function tolerance for the relative error desired in the sum of squares, parsed to leastsq.
        @type ftol:                 float
        @keyword xtol:              The error tolerance for the relative error desired in the approximate solution, parsed to leastsq.
        @type xtol:                 float
        @keyword maxfev:            The maximum number of function evaluations, parsed to leastsq.  If zero, then 100*(N+1) is the maximum function calls.  N is the number of elements in x0=[r2eff, i0].
        @type maxfev:               int
        @keyword factor:            The initial step bound, parsed to leastsq.  It determines the initial step bound (''factor * || diag * x||'').  Should be in the interval (0.1, 100).
        @type factor:               float
        """

        # Store settings.
        self.ftol = ftol
        self.xtol = xtol
        self.maxfev = maxfev
        self.factor = factor


    def set_settings_minfx(self, scaling_matrix=None, min_algor='simplex', c_code=True, constraints=False, func_tol=1e-25, grad_tol=None, max_iterations=10000000):
        """Setup options to minfx.

        @keyword scaling_matrix:    The square and diagonal scaling matrix.
        @type scaling_matrix:       numpy rank-2 float array
        @keyword min_algor:         The minimisation algorithm
        @type min_algor:            string
        @keyword c_code:            If optimise with C code.
        @type c_code:               bool
        @keyword constraints:       If constraints should be used.
        @type constraints:          bool
        @keyword func_tol:          The function tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
        @type func_tol:             None or float
        @keyword grad_tol:          The gradient tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
        @type grad_tol:             None or float
        @keyword max_iterations:    The maximum number of iterations for the algorithm.
        @type max_iterations:       int
        """

        # Store variables.
        self.scaling_matrix = scaling_matrix
        self.c_code = c_code

        # Scaling initialisation.
        self.scaling_flag = False
        if self.scaling_matrix != None:
            self.scaling_flag = True

        # Set algorithm.
        self.min_algor = min_algor

        # Define if constraints should be used.
        self.constraints = constraints

        # Settings to minfx.
        self.func_tol = func_tol
        self.grad_tol = grad_tol
        self.max_iterations = max_iterations

        # Options to minfx depends if contraints is set.
        if self.constraints:
            self.min_options = ('%s'%(self.min_algor),)
            self.min_algor = 'Log barrier'
            self.A = array([ [ 1.,  0.],
                        [-1.,  0.],
                        [ 0.,  1.]] )
            self.b = array([   0., -200.,    0.])

        else:
            self.min_options = ()
            self.A = None
            self.b = None


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

        # Get data.
        intensities = self.values
        times = self.times

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


    def func_exp(self, times=None, r2eff=None, i0=None):
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


    def func_exp_grad(self, params):
        """Target function for the gradient (Jacobian matrix) of func_exp to minfx, for exponential fit .

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The Jacobian matrix with 'm' rows of function derivatives per 'n' columns of parameters.
        @rtype:         numpy array
        """

        # Unpack the parameter values.
        r2eff = params[0]
        i0 = params[1]

        # Make partial derivative, with respect to r2eff.
        d_exp_d_r2eff = -i0 * self.times * exp(-r2eff * self.times)

        # Make partial derivative, with respect to i0.
        d_exp_d_i0 = exp(-r2eff * self.times)

        # Define Jacobian as m rows with function derivatives and n columns of parameters.
        self.jacobian_matrix_exp = transpose(array( [d_exp_d_r2eff , d_exp_d_i0] ) )

        # Take the sum, to send to minfx.
        sum_d_exp_d_r2eff = sum( d_exp_d_r2eff )
        sum_d_exp_d_i0 = sum( d_exp_d_i0 )

        # Define Jacobian as m rows with function derivatives and n columns of parameters.
        sum_jacobian_matrix_exp = transpose(array( [sum_d_exp_d_r2eff , sum_d_exp_d_i0] ) )

        # Return Jacobian matrix.
        return sum_jacobian_matrix_exp


    def func_exp_chi2(self, params):
        """Target function for minimising chi2 in minfx, for exponential fit.

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

        # Calculate.
        self.back_calc[:] = self.func_exp(times=self.times, r2eff=r2eff, i0=i0)

        # Return the total chi-squared value.
        chi2 = chi2_rankN(data=self.values, back_calc_vals=self.back_calc, errors=self.errors)

        # Calculate and return the chi-squared value.
        return chi2


    def func_exp_chi2_grad(self, params):
        """Target function for the gradient (Jacobian matrix) of func_exp_chi2() to minfx, for exponential fit .

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The Jacobian matrix with 'm' rows of function derivatives per 'n' columns of parameters.
        @rtype:         numpy array
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        r2eff = params[0]
        i0 = params[1]

        # Calculate gradient according to chi2.
        # See: http://wiki.nmr-relax.com/Calculate_jacobian_hessian_matrix_in_sympy_exponential_decay

        # Make partial derivative, with respect to r2eff.
        d_chi2_d_r2eff = 2.0 * i0 * self.times * ( -i0 * exp( -r2eff * self.times) + self.values) * exp( -r2eff * self.times ) / self.errors**2

        # Make partial derivative, with respect to i0.
        d_chi2_d_i0 = - 2.0 * ( -i0 * exp( -r2eff * self.times) + self.values) * exp( -r2eff * self.times) / self.errors**2

        # Define Jacobian as m rows with function derivatives and n columns of parameters.
        self.jacobian_matrix_exp_chi2 = transpose(array( [d_chi2_d_r2eff , d_chi2_d_i0] ) )

        # Take the sum, to send to minfx.
        sum_d_chi2_d_r2eff = sum( d_chi2_d_r2eff )
        sum_d_chi2_d_i0 = sum( d_chi2_d_i0 )

        # Define Jacobian as m rows with function derivatives and n columns of parameters.
        sum_jacobian_matrix_exp_chi2 = transpose(array( [sum_d_chi2_d_r2eff , sum_d_chi2_d_i0] ) )

        # Return Jacobian matrix.
        return sum_jacobian_matrix_exp_chi2


    def func_exp_weighted_general(self, params):
        """Target function for weighted minimisation with scipy.optimize.

        @param params:          The vector of parameter values.
        @type params:           numpy rank-1 float array
        @return:                The weighted difference between function evaluation with fitted parameters and measured values.
        @rtype:                 numpy array
        """

        # Return
        return 1. / self.errors * (self.func_exp(self.times, *params) - self.values)


def estimate_r2eff(method='minfx', min_algor='simplex', c_code=True, constraints=False, spin_id=None, ftol=1e-15, xtol=1e-15, maxfev=10000000, factor=100.0, verbosity=1):
    """Estimate r2eff and errors by exponential curve fitting with scipy.optimize.leastsq or minfx.

    THIS IS ONLY FOR TESTING.

    scipy.optimize.leastsq is a wrapper around MINPACK's lmdif and lmder algorithms.

    MINPACK is a FORTRAN90 library which solves systems of nonlinear equations, or carries out the least squares minimization of the residual of a set of linear or nonlinear equations.

    Errors are calculated by taking the square root of the reported co-variance.

    This can be an huge time saving step, when performing model fitting in R1rho.
    Errors of R2eff values, are normally estimated by time-consuming Monte-Carlo simulations.

    Initial guess for the starting parameter x0 = [r2eff_est, i0_est], is by converting the exponential curve to a linear problem.
    Then solving initial guess by linear least squares of: ln(Intensity[j]) = ln(i0) - time[j]* r2eff.


    @keyword method:            The method to minimise and estimate errors.  Options are: 'minfx' or 'scipy.optimize.leastsq'.
    @type method:               string
    @keyword min_algor:         The minimisation algorithm
    @type min_algor:            string
    @keyword constraints:       If constraints should be used.
    @type constraints:          bool
    @keyword c_code:            If optimise with C code.
    @type c_code:               bool
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
    @keyword verbosity:         The amount of information to print.  The higher the value, the greater the verbosity.
    @type verbosity:            int
    """

    # Perform checks.
    check_model_type(model=MODEL_R2EFF)

    # Set class scipy setting.
    E = Exp(verbosity=verbosity)
    E.set_settings_leastsq(ftol=ftol, xtol=xtol, maxfev=maxfev, factor=factor)

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
        if E.verbosity >= 1:
            # Individual spin block section.
            top = 2
            if E.verbosity >= 2:
                top += 2
            subsection(file=sys.stdout, text="Fitting with %s to: %s"%(method, spin_string), prespace=top)
            if method == 'minfx':
                subsection(file=sys.stdout, text="min_algor='%s', c_code=%s, constraints=%s"%(min_algor, c_code, constraints), prespace=0)

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

            # Initialise data.
            E.setup_data(values=values, errors=errors, times=times)

            # Get the result based on method.
            if method == 'scipy.optimize.leastsq':
                # Acquire results.
                results = minimise_leastsq(E=E)

            elif method == 'minfx':
                # Set settings.
                E.set_settings_minfx(min_algor=min_algor, c_code=c_code, constraints=constraints)

                # Acquire results.
                results = minimise_minfx(E=E)
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
            if E.verbosity >= 1:
                # Add print strings.
                point_info = "%s at %3.1f MHz, for offset=%3.3f ppm and dispersion point %-5.1f, with %i time points." % (exp_type, frq/1E6, offset, point, len(times))
                print_strings.append(point_info)

                par_info = "r2eff=%3.3f r2eff_err=%3.3f, i0=%6.1f, i0_err=%3.3f, chi2=%3.3f.\n" % ( r2eff, r2eff_err, i0, i0_err, chi2)
                print_strings.append(par_info)

                if E.verbosity >= 2:
                    time_info = ', '.join(map(str, times))
                    print_strings.append('For time array: '+time_info+'.\n\n')

            # Print info
            if len(print_strings) > 0:
                for print_string in print_strings:
                    print(print_string),


def minimise_leastsq(E=None):
    """Estimate r2eff and errors by exponential curve fitting with scipy.optimize.leastsq.

    @keyword E:     The Exponential function class, which contain data and functions.
    @type E:        class
    @return:        Packed list with optimised parameter, estimated parameter error, chi2, iter_count, f_count, g_count, h_count, warning
    @rtype:         list
    """

    # Check that scipy.optimize.leastsq is available.
    if not scipy_module:
        raise RelaxError("scipy module is not available.")

    # Initial guess for minimisation. Solved by linear least squares.
    x0 = E.estimate_x0_exp()

    # Define function to minimise. Use errors as weights in the minimisation.
    use_weights = True

    if use_weights:
        func = E.func_exp_weighted_general
        # If 'sigma'/erros describes one standard deviation errors of the input data points. The estimated covariance in 'pcov' is based on these values.
        absolute_sigma = True
    else:
        func = E.func_exp_general
        absolute_sigma = False

    # There are no args to the function, since values and times are stored in the class.
    args=()

    # Call scipy.optimize.leastsq.
    popt, pcov, infodict, errmsg, ier = leastsq(func=func, x0=x0, args=args, full_output=True, ftol=E.ftol, xtol=E.xtol, maxfev=E.maxfev, factor=E.factor)

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

    # 'pcov': The estimated covariance matrix of popt.
    # The diagonals provide the variance of the parameter estimate.
    # pcov is here, the reduced cov(x) or fractional cov(x). It is rescaling which is useful in numerical computations.
    # It is not the true covariance matrix.
    # An issue arises when errors in the y data points are given.
    # Only the relative errors are used as weights, so the fit parameter errors, determined from the covariance do not depended on the magnitude of the errors in the individual data points.
    # See: http://stackoverflow.com/questions/14581358/getting-standard-errors-on-fitted-parameters-using-the-optimize-leastsq-method-i
    # See: http://stackoverflow.com/questions/14854339/in-scipy-how-and-why-does-curve-fit-calculate-the-covariance-of-the-parameter-es/14857441#14857441

    # The reduced chi square: Take each "difference element, which could have been weighted" (O - E) and put to order 2. Sum them, and divide by number of degrees of freedom.
    # Calculated the (weighted) chi2 value.
    chi2 = sum( fvec**2 )

    # N is number of observations.
    N = len(E.values)
    # n is number of fitted parameters.
    n = len(x0)
    #  number of degrees of freedom
    v = N - n - 1

    # The reduced chi square.
    chi2_red = chi2 / v

    # chi2_red >> 1 : indicates a poor model fit.
    # chi2_red >  1 : indicates that the fit has not fully captured the data (or that the error variance has been underestimated)
    # chi2_red = 1  : indicates that the extent of the match between observations and estimates is in accord with the error variance.
    # chi2_red <  1 : indicates that the model is 'over-fitting' the data: either the model is improperly fitting noise, or the error variance has been overestimated.

    if pcov is None:
        # indeterminate covariance
        pcov = zeros((len(popt), len(popt)), dtype=float)
        pcov.fill(inf)
    elif not absolute_sigma:
        if N > n:
            pcov = pcov * chi2_red
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


def minimise_minfx(E=None):
    """Estimate r2eff and errors by minimising with minfx.

    @keyword E:     The Exponential function class, which contain data and functions.
    @type E:        class
    @return:        Packed list with optimised parameter, parameter error set to 'inf', chi2, iter_count, f_count, g_count, h_count, warning
    @rtype:         list
    """

    # Initial guess for minimisation. Solved by linear least squares.
    x0 = asarray( E.estimate_x0_exp() )

    if E.c_code:
        # Initialise the function to minimise.
        scaling_list = [1.0, 1.0]
        setup(num_params=len(x0), num_times=len(E.times), values=E.values, sd=E.errors, relax_times=E.times, scaling_matrix=scaling_list)

        t_func = func_wrapper
        t_dfunc = dfunc_wrapper
        t_d2func = d2func_wrapper

    else:
        # Minimise with minfx.
        # Define function to minimise for minfx.
        t_func = E.func_exp_chi2
        t_dfunc = E.func_exp_chi2_grad
        t_d2func = None

    # Minimise.
    results_minfx = generic_minimise(func=t_func, dfunc=t_dfunc, d2func=t_d2func, args=(), x0=x0, min_algor=E.min_algor, min_options=E.min_options, func_tol=E.func_tol, grad_tol=E.grad_tol, maxiter=E.max_iterations, A=E.A, b=E.b, full_output=True, print_flag=0)

    # Unpack
    param_vector, chi2, iter_count, f_count, g_count, h_count, warning = results_minfx

    # Get the Jacobian.
    if E.c_code:
        # Calculate the direct exponential Jacobian matrix from C code.
        jacobian_matrix_exp = transpose(asarray( jacobian(param_vector) ) )

        # Compare with python code.
        #E.func_exp_grad(param_vector)
        #jacobian_matrix_exp2 = E.jacobian_matrix_exp
        #print jacobian_matrix_exp - jacobian_matrix_exp2
    else:
        # Call class, to store value.
        E.func_exp_grad(param_vector)
        jacobian_matrix_exp = E.jacobian_matrix_exp
        #E.func_exp_chi2_grad(param_vector)
        #jacobian_matrix_exp = E.jacobian_matrix_exp_chi2

    # Get the co-variance
    pcov = multifit_covar(J=jacobian_matrix_exp, errors=E.errors)

    # To compute one standard deviation errors on the parameters, take the square root of the diagonal covariance.
    param_vector_error = sqrt(diag(pcov))
    # Set error to inf.
    #param_vector_error = [inf, inf]

    # Pack to list.
    results = [param_vector, param_vector_error, chi2, iter_count, f_count, g_count, h_count, warning]

    # Return, including errors.
    return results
