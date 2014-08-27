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
from specific_analyses.relax_disp.estimate_r2eff import minimise_leastsq, Exp
from target_functions.relax_fit import setup, func, dfunc, d2func, back_calc_I
from target_functions.chi2 import chi2_rankN

## Set the min_algor.
## simplex is algorithms without gradient. It is quite slow, since it needs to take many steps.
#min_algor='simplex'

## Steepest descent uses only the gradient. This works, but it is not totally precise.
##min_algor = 'Steepest descent'
##max_iterations = 1000

## Quasi-Newton BFGS. Uses only the gradient.
## This gets the same results as 2000 Monte-Carlo with simplex.
## This is one of the best optimisation techniques when only the function and gradient are present, as it tries to numerically approximate the Hessian matrix, updating it as the algorithm moves along. 
#min_algor = 'BFGS'

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

        # Calculate without contraints, BFGS.
        #v_BFGS_cF_chi2_list = array(verify(min_algor='BFGS', constraints=False))

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

    if True:
        #################
        print("Verify, with constraints, C code")
        constraints = True

        # Print statistics.
        verbose = True

        # Calc for verify with constraints.
        filename = tempfile.NamedTemporaryFile(delete=False).name
        # Profile for a single spin.
        cProfile.run('verify(constraints=%s)'%constraints, filename)

        print_report(filename=filename, verbose=verbose)

    if True:
        #################
        print("Verify, without constraints, C code")
        constraints = False

        # Print statistics.
        verbose = True

        # Calc for verify with constraints.
        filename = tempfile.NamedTemporaryFile(delete=False).name
        # Profile for a single spin.
        cProfile.run('verify(constraints=%s)'%constraints, filename)

        print_report(filename=filename, verbose=verbose)

    if True:
        #################
        print("Verify, without constraints, C code BFGS")
        constraints = False

        # Print statistics.
        verbose = True

        # Calc for verify with constraints.
        filename = tempfile.NamedTemporaryFile(delete=False).name
        # Profile for a single spin.
        cProfile.run('verify(min_algor="BFGS", constraints=%s)'%(constraints), filename)

        print_report(filename=filename, verbose=verbose)

    if False:
        #################
        print("Verify, with constraints, Python")
        constraints = True

        # Print statistics.
        verbose = True

        # Calc for verify with constraints.
        filename = tempfile.NamedTemporaryFile(delete=False).name
        # Profile for a single spin.
        cProfile.run('verify_pyt(constraints=%s)'%constraints, filename)

        print_report(filename=filename, verbose=verbose)

    if False:
        #################
        print("Verify, without constraints, Python")
        constraints = False

        # Print statistics.
        verbose = True

        # Calc for verify with constraints.
        filename = tempfile.NamedTemporaryFile(delete=False).name
        # Profile for a single spin.
        cProfile.run('verify_pyt(constraints=%s)'%constraints, filename)

        print_report(filename=filename, verbose=verbose)

    if True:
        #################
        print("Verify, without constraints, Python Scipy")

        # Print statistics.
        verbose = True

        # Calc for verify with constraints.
        filename = tempfile.NamedTemporaryFile(delete=False).name
        # Profile for a single spin.
        cProfile.run('verify_sci()', filename)

        print_report(filename=filename, verbose=verbose)


def print_report(filename=None, verbose=True):
    lines_report = 1

    # Read all stats files into a single object
    stats = pstats.Stats(filename)

    # Clean up filenames for the report
    stats.strip_dirs()

    # Sort the statistics by the cumulative time spent in the function. cumulative, time, calls
    stats.sort_stats('cumulative')

    # Print report for single.
    if verbose:
        stats.print_stats(lines_report)


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

def verify(min_algor='simplex', constraints=None):
    # Instantiate class.
    C = Profile()

    # Instantiate class.
    E = Exp(verbosity=0)

    # List to store chi2.
    chi2_list = []

    for values, errors, times, struct, num_times in C.loop_data():
        # Initialise the function to minimise.
        E.setup_data(values=values, errors=errors, times=times)

        # Initial guess for minimisation. Solved by linear least squares.
        x0 = asarray( E.estimate_x0_exp() )

        E.set_settings_minfx(min_algor=min_algor, constraints=constraints)

        # Initialise the function to minimise.
        scaling_list = [1.0, 1.0]
        setup(num_params=len(x0), num_times=len(E.times), values=E.values, sd=E.errors, relax_times=E.times, scaling_matrix=scaling_list)

        results = generic_minimise(func=func, dfunc=dfunc, d2func=d2func, args=(), x0=x0, min_algor=E.min_algor, min_options=E.min_options, func_tol=E.func_tol, grad_tol=E.grad_tol, maxiter=E.max_iterations, A=E.A, b=E.b, full_output=True, print_flag=E.verbosity)

        # Unpack
        param_vector, chi2, iter_count, f_count, g_count, h_count, warning = results

        # Add to list.
        chi2_list.append(chi2)

    return chi2_list


def verify_pyt(min_algor='simplex', constraints=None):
    # Instantiate class.
    C = Profile()

    # Instantiate class.
    E = Exp(verbosity=0)

    # List to store chi2.
    chi2_list = []

    for values, errors, times, struct, num_times in C.loop_data():
        # Initialise the function to minimise.
        E.setup_data(values=values, errors=errors, times=times)

        # Initial guess for minimisation. Solved by linear least squares.
        x0 = asarray( E.estimate_x0_exp() )

        E.set_settings_minfx(min_algor=min_algor, constraints=constraints)

        # Define func.
        func = E.func_exp
        dfunc = E.func_exp_grad

        results = generic_minimise(func=func, dfunc=dfunc, d2func=d2func, args=(), x0=x0, min_algor=E.min_algor, min_options=E.min_options, func_tol=E.func_tol, grad_tol=E.grad_tol, maxiter=E.max_iterations, A=E.A, b=E.b, full_output=True, print_flag=E.verbosity)

        # Unpack the results.
        param_vector, chi2, iter_count, f_count, g_count, h_count, warning = results

        # Add to list.
        chi2_list.append(chi2)

    return chi2_list


def verify_sci(print_info=False):
    # Instantiate class.
    C = Profile()

    # Instantiate class.
    E = Exp(verbosity=0)

    # List to store chi2.
    chi2_list = []

    for values, errors, times, struct, num_times in C.loop_data():
        # Initialise the function to minimise.
        E.setup_data(values=values, errors=errors, times=times)

        results = minimise_leastsq(E=E)

        # Unpack results
        param_vector, param_vector_error, chi2, iter_count, f_count, g_count, h_count, warning = results

        if print_info:
            r2eff = param_vector[0]
            i0 = param_vector[1]
            r2eff_err = param_vector_error[0]
            i0_err = param_vector_error[1]
            print("r2eff=%3.3f +/- %3.3f , i0=%3.3f +/- %3.3f" % (r2eff, r2eff_err, i0, i0_err) )

        chi2_list.append(chi2)

    return chi2_list


# Execute main function.
if __name__ == "__main__":
    main()
