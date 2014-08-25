#!/usr/bin/env python

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

# Python module imports.
import cProfile
from copy import deepcopy
from os import getcwd, path, sep
from numpy import array, asarray, diag, inf, load, sqrt, sum, zeros
import pstats
import sys
import tempfile
from minfx.generic import generic_minimise
from scipy.optimize import curve_fit, leastsq
import warnings

# Python 3 support.
try:
    import __builtin__
    del __builtin__
except ImportError:
    import builtins
    builtins.xrange = builtins.range

# Add to system path, according to 
if len(sys.argv) == 1:
    path_to_base = path.join(getcwd(), '..', '..', '..', '..')
else:
    path_to_base = path.abspath(sys.argv[1])

# Reverse sys path.
sys.path.reverse()
# Add to path.
sys.path.append(path_to_base)
# Reverse sys path.
sys.path.reverse()

# relax module imports.
from status import Status; status = Status()
from target_functions.relax_fit import setup, func, dfunc, d2func, back_calc_I
from relax_fit import Exponential


# Alter setup.
def main():
    # Do verification between C code and Python code.
    if False:
        # Calculate with C code.
        # Calculate with contraints.
        v_cT_chi2_list = array(verify(constraints=True))
        # Calculate without contraints.
        v_cF_chi2_list = array(verify(constraints=False))

        # Verify C code with and without constraints.
        sum_root_squared = sum( sqrt( (v_cT_chi2_list - v_cF_chi2_list)**2 ) )
        print("The sum of the root squared differences between with and without constraints are: %.3e" % sum_root_squared)

        # Now calculate with Python code.
        # Calculate with contraints.
        v_pyt_cT_chi2_list = array(verify_pyt(constraints=True))

        # Verify against C code with constraints.
        sum_root_squared = sum( sqrt( (v_cT_chi2_list - v_pyt_cT_chi2_list)**2 ) )
        print("The sum of the root squared differences between C code and python are: %.3e" % sum_root_squared)

        # Calculate without contraints.
        v_pyt_cF_chi2_list = array(verify_pyt(constraints=False))

        # Verify python code with and without constraints.
        sum_root_squared = sum( sqrt( (v_pyt_cT_chi2_list - v_pyt_cF_chi2_list)**2 ) )
        print("The sum of the root squared differences between with and without constraints for python code are: %.3e" % sum_root_squared)

        # Print stuff.
        for i, chi_v_cT in enumerate(v_cT_chi2_list):
            chi_v_cF = v_cF_chi2_list[i]
            chi_v_pyt_cT = v_pyt_cT_chi2_list[i]
            chi_v_pyt_cF = v_pyt_cF_chi2_list[i]
            #print chi_v_cT, chi_v_cF, chi_v_pyt_cT, chi_v_pyt_cF,
            print("C_cT=%1.1e C_cF=%1.1e P_cT=%1.1e P_cF=%1.1e" % (chi_v_cT-chi_v_cT, chi_v_cF-chi_v_cT, chi_v_pyt_cT-chi_v_cT, chi_v_pyt_cF-chi_v_cT) )

    # Do verification for Python code, and difference between minfx and Scipy optimisation without constraints.
    if True:
        # Calculate with Python code.
        # Calculate without contraints.
        v_pyt_cF_chi2_list = array(verify_pyt(constraints=False))

        # With scipy.
        v_sci_cF_chi2_list = array(verify_sci(print_info=True))

        # Verify python code with and without constraints.
        sum_root_squared = sum( sqrt( (v_pyt_cF_chi2_list - v_sci_cF_chi2_list)**2 ) )
        print("The sum of the root squared differences for python code, without constraints, between minfx and scipy are: %.3e" % sum_root_squared)

        # Print stuff.
        for i, chi_v_pyt_cF in enumerate(v_pyt_cF_chi2_list):
            chi_v_sci_cF = v_sci_cF_chi2_list[i]
            print("P_cF=%1.1e Sci_cF=%1.1e" % (chi_v_pyt_cF-chi_v_pyt_cF, chi_v_pyt_cF-chi_v_sci_cF) )

    # Do profiling.

    lines_report = 15

    if False:
        #################
        print("Verify, with constraints, C code")
        constraints = True

        # Print statistics.
        verbose = True

        # Calc for verify with constraints.
        v_cT_filename = tempfile.NamedTemporaryFile(delete=False).name
        # Profile for a single spin.
        cProfile.run('verify(constraints=%s)'%constraints, v_cT_filename)

        # Read all stats files into a single object
        v_cT_stats = pstats.Stats(v_cT_filename)

        # Clean up filenames for the report
        v_cT_stats.strip_dirs()

        # Sort the statistics by the cumulative time spent in the function. cumulative, time, calls
        v_cT_stats.sort_stats('cumulative')

        # Print report for single.
        if verbose:
            v_cT_stats.print_stats(lines_report)

    if False:
        #################
        print("Verify, with constraints, Python")
        constraints = True

        # Print statistics.
        verbose = True

        # Calc for verify with constraints.
        v_pyt_cT_filename = tempfile.NamedTemporaryFile(delete=False).name
        # Profile for a single spin.
        cProfile.run('verify_pyt(constraints=%s)'%constraints, v_pyt_cT_filename)

        # Read all stats files into a single object
        v_pyt_cT_stats = pstats.Stats(v_pyt_cT_filename)

        # Clean up filenames for the report
        v_pyt_cT_stats.strip_dirs()

        # Sort the statistics by the cumulative time spent in the function. cumulative, time, calls
        v_pyt_cT_stats.sort_stats('cumulative')

        # Print report for single.
        if verbose:
            v_pyt_cT_stats.print_stats(lines_report)

    if True:
        #################
        print("Verify, without constraints, C code")
        constraints = False

        # Print statistics.
        verbose = True

        # Calc for verify with constraints.
        v_cF_filename = tempfile.NamedTemporaryFile(delete=False).name
        # Profile for a single spin.
        cProfile.run('verify(constraints=%s)'%constraints, v_cF_filename)

        # Read all stats files into a single object
        v_cF_stats = pstats.Stats(v_cF_filename)

        # Clean up filenames for the report
        v_cF_stats.strip_dirs()

        # Sort the statistics by the cumulative time spent in the function. cumulative, time, calls
        v_cF_stats.sort_stats('cumulative')

        # Print report for single.
        if verbose:
            v_cF_stats.print_stats(lines_report)

    if True:
        #################
        print("Verify, without constraints, Python")
        constraints = False

        # Print statistics.
        verbose = True

        # Calc for verify with constraints.
        v_pyt_cF_filename = tempfile.NamedTemporaryFile(delete=False).name
        # Profile for a single spin.
        cProfile.run('verify_pyt(constraints=%s)'%constraints, v_pyt_cF_filename)

        # Read all stats files into a single object
        v_pyt_cF_stats = pstats.Stats(v_pyt_cF_filename)

        # Clean up filenames for the report
        v_pyt_cF_stats.strip_dirs()

        # Sort the statistics by the cumulative time spent in the function. cumulative, time, calls
        v_pyt_cF_stats.sort_stats('cumulative')

        # Print report for single.
        if verbose:
            v_pyt_cF_stats.print_stats(lines_report)


    if True:
        #################
        print("Verify, without constraints, Python Scipy")

        # Print statistics.
        verbose = True

        # Calc for verify with constraints.
        v_sci_cF_filename = tempfile.NamedTemporaryFile(delete=False).name
        # Profile for a single spin.
        cProfile.run('verify_sci()', v_sci_cF_filename)

        # Read all stats files into a single object
        v_sci_cF_stats = pstats.Stats(v_sci_cF_filename)

        # Clean up filenames for the report
        v_sci_cF_stats.strip_dirs()

        # Sort the statistics by the cumulative time spent in the function. cumulative, time, calls
        v_sci_cF_stats.sort_stats('cumulative')

        # Print report for single.
        if verbose:
            v_sci_cF_stats.print_stats(lines_report)


class Profile:
    """
    Class Profile inherits the Dispersion container class object.
    """

    def __init__(self):

        # Define parameters
        self.param_key_list = [
            'r1rho_799.77739910_118.078_431.000',
            'r1rho_799.77739910_118.078_651.200',
            'r1rho_799.77739910_118.078_800.500',
            'r1rho_799.77739910_118.078_984.000',
            'r1rho_799.77739910_118.078_1341.110',
            'r1rho_799.77739910_118.078_1648.500',
            'r1rho_799.77739910_124.247_1341.110',
            'r1rho_799.77739910_130.416_800.500',
            'r1rho_799.77739910_130.416_1341.110',
            'r1rho_799.77739910_130.416_1648.500',
            'r1rho_799.77739910_142.754_800.500',
            'r1rho_799.77739910_142.754_1341.110',
            'r1rho_799.77739910_179.768_1341.110',
            'r1rho_799.77739910_241.459_1341.110'
        ]

        # Define maximum dimensions.
        self.NE, self.NS, self.NM, self.NO, self.ND, self.NT = 1, 1, 1, 6, 6, 5

        # Define path to data
        self.data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'curve_fitting'+sep+'profiling'+sep

        self.values_arr = load(self.data_path + "values_arr.npy")
        self.errors_arr = load(self.data_path + "errors_arr.npy")
        self.times_arr = load(self.data_path + "times_arr.npy")
        self.struct_arr = load(self.data_path + "struct_arr.npy")

        #param_vector = array([ 0.,  0.])
        self.param_vector = array([  8.800000000000001e+00,   2.000000000800000e+05])
        self.scaling_list = [1.0, 1.0]
        self.func_tol = 1e-25
        self.grad_tol = None
        #self.max_iterations = 10000000
        self.max_iterations = 10000000
        self.verbosity = 0

    def set_options(self, constraints=None):
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


    def loop_data(self):
        """Generator that yields data from array."""

        # Loop over data:
        for ei in range(self.NE):
            for si in range(self.NS):
                for mi in range(self.NM):
                    for oi in range(self.NO):
                        for di in range(self.ND):
                            # Extract values
                            values = self.values_arr[ei, si, mi, oi, di]
                            errors = self.errors_arr[ei, si, mi, oi, di]
                            times = self.times_arr[ei, si, mi, oi, di]
                            struct = self.struct_arr[ei, si, mi, oi, di]
                            num_times = int( sum(struct) )

                            if num_times == 0:
                                continue

                            yield values[:num_times], errors[:num_times], times[:num_times], struct[:num_times], num_times

def verify(constraints=None):
    # Instantiate class.
    C = Profile()

    # Set the minimising options.
    C.set_options(constraints=constraints)

    # List to store chi2.
    chi2_list = []

    for values, errors, times, struct, num_times in C.loop_data():
        # Initialise the function to minimise.
        setup(num_params=len(C.param_vector), num_times=num_times, values=values, sd=errors, relax_times=times, scaling_matrix=C.scaling_list)

        results = generic_minimise(func=func, dfunc=dfunc, d2func=d2func, args=(), x0=C.param_vector, min_algor=C.min_algor, min_options=C.min_options, func_tol=C.func_tol, grad_tol=C.grad_tol, maxiter=C.max_iterations, A=C.A, b=C.b, full_output=True, print_flag=C.verbosity)

        # Unpack
        param_vector, chi2, iter_count, f_count, g_count, h_count, warning = results

        # Add to list.
        chi2_list.append(chi2)

    return chi2_list


def verify_pyt(constraints=None):
    # Instantiate class.
    C = Profile()

    # Set the minimising options.
    C.set_options(constraints=constraints)

    # List to store chi2.
    chi2_list = []

    for values, errors, times, struct, num_times in C.loop_data():
        # Initialise the function to minimise.
        exp_class = Exponential(num_params=len(C.param_vector), num_times=num_times, values=values, sd=errors, relax_times=times, scaling_matrix=C.scaling_list)

        results = generic_minimise(func=exp_class.func_exp, args=(), x0=C.param_vector, min_algor=C.min_algor, min_options=C.min_options, func_tol=C.func_tol, grad_tol=C.grad_tol, maxiter=C.max_iterations, A=C.A, b=C.b, full_output=True, print_flag=C.verbosity)

        # Unpack the results.
        param_vector, chi2, iter_count, f_count, g_count, h_count, warning = results

        # Add to list.
        chi2_list.append(chi2)

    return chi2_list


def verify_sci(print_info=False):
    # Instantiate class.
    C = Profile()

    # List to store chi2.
    chi2_list = []

    for values, errors, times, struct, num_times in C.loop_data():
        # Initialise the function to minimise.
        exp_class = Exponential(num_params=len(C.param_vector), num_times=num_times, values=values, sd=errors, relax_times=times, scaling_matrix=C.scaling_list)

        # Do optimisation with scipy.optimize.curve_fit
        # sigma : None or M-length sequence, optional. If not None, these values are used as weights in the least-squares problem.
        # absolute_sigma : bool, optional. If False, sigma denotes relative weights of the data points.
        # The returned covariance matrix pcov is based on estimated errors in the data, and is not affected by the overall magnitude of the values in sigma. 
        # Only the relative magnitudes of the sigma values matter.
        # If True, sigma describes one standard deviation errors of the input data points. The estimated covariance in pcov is based on these values.

        #Returns:	
        # popt : array
        # Optimal values for the parameters so that the sum of the squared error of f(xdata, *popt) - ydata is minimized
        # pcov : 2d array
        # The estimated covariance of popt. The diagonals provide the variance of the parameter estimate.
        # To compute one standard deviation errors on the parameters use perr = np.sqrt(np.diag(pcov)).
        # How the sigma parameter affects the estimated covariance depends on absolute_sigma argument, as described above.

        # With curve_fit. This is just a wrapper to non-linear least squares. This function though lacks input to tolerance.
        #, sigma=None, absolute_sigma=False
        # sigma: If not None, these values are used as weights in the least-squares problem.
        #  if absolute_sigma=True, 'sigma' describes one standard deviation errors of the input data points. The estimated covariance in 'pcov' is based on these values.
        #popt, pcov, infodict, errmsg, ier = curve_fit(f=exp_class.calc_exp, xdata=times, ydata=values, p0=C.param_vector, full_output=True)

        # 'xtol': Relative error desired in the approximate solution.
        # 'ftol': Relative error desired in the sum of squares.
        #xtol = 1.49012e-08
        xtol = 1e-15
        ftol = xtol

        # 'factor': float, optional. A parameter determining the initial step bound (``factor * || diag * x||``).  Should be in the interval ``(0.1, 100)``.
        factor= 100

        # With leastsq directly.
        # Define function to minimise.
        use_weights = True
        # If 'sigma'/erros describes one standard deviation errors of the input data points. The estimated covariance in 'pcov' is based on these values.
        absolute_sigma = True

        if use_weights:
            func = exp_class.func_exp_weighted_general
            weights = 1.0 / asarray(errors)
            args=(times, values, weights )
        else:
            func = exp_class.func_exp_general
            args=(times, values)

        popt, pcov, infodict, errmsg, ier = leastsq(func=func, x0=C.param_vector, args=args, full_output=True, ftol=ftol, xtol=xtol, maxfev=C.max_iterations, factor=factor)

        ## Unpack the results.
        #param_vector, chi2, iter_count, f_count, g_count, h_count, warning = results

        param_vector = popt

        # Catch errors:
        if ier in [1, 2, 3, 4]:
            warning = None
        elif ier in [4]:
            warnings.warn(errmsg, RuntimeWarning)
            warning = errmsg
        elif ier in [0, 5, 6, 7, 8]:
            raise RuntimeWarning(errmsg)

        # 'nfev' number of function calls.
        f_count = infodict['nfev']
        g_count = 0
        h_count = 0

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
        chi2 = exp_class.chi2_rankN(data=values, back_calc_vals=back_calc, errors=errors)

        chi2_list.append(chi2)

        # 'pcov': The estimated covariance of popt.
        # The diagonals provide the variance of the parameter estimate.
        ydata = values
        p0 = C.param_vector

        if pcov is None:
            # indeterminate covariance
            pcov = zeros((len(popt), len(popt)), dtype=float)
            pcov.fill(inf)
        elif not absolute_sigma:
            if len(ydata) > len(p0):
                s_sq = sum( fvec**2 ) / (len(values) - len(p0))
                pcov = pcov * s_sq
            else:
                pcov.fill(inf)

        # To compute one standard deviation errors on the parameters, take the square root of the diagonal.
        perr = sqrt(diag(pcov))

        if print_info:
            r2eff = popt[0]
            i0 = popt[1]
            r2eff_err = perr[0]
            i0_err = perr[1]
            print("r2eff=%3.3f +/- %3.3f , i0=%3.3f +/- %3.3f" % (r2eff, r2eff_err, i0, i0_err) )


    return chi2_list


# Execute main function.
if __name__ == "__main__":
    main()
