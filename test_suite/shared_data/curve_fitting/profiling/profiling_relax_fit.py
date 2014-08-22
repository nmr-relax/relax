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
from os import getcwd, path, sep
from numpy import array, arange, int32, float64, pi, load, sqrt, sum
import pstats
import sys
import tempfile
from minfx.generic import generic_minimise

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


# Alter setup.
def main():
    v_cT_chi2_list = array(verify(constraints=True))
    v_cF_chi2_list = array(verify(constraints=False))

    sum_root_squared = sum( sqrt( (v_cT_chi2_list - v_cF_chi2_list)**2 ) )
    print("The sum of the root squared differences are: %.3e" % sum_root_squared)

    lines_report = 15

    if True:
        #################
        #  Verify, with constraints
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

    if True:
        #################
        #  Verify, without constraints
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


def verify(constraints=None):
    # Instantiate class.
    C = Profile()

    # Set the minimising options.
    C.set_options(constraints=constraints)

    chi2_list = []

    # Print arrays.
    for ei in range(C.NE):
        for si in range(C.NS):
            for mi in range(C.NM):
                for oi in range(C.NO):
                    for di in range(C.ND):
                        # Extract values
                        values = C.values_arr[ei, si, mi, oi, di]
                        errors = C.errors_arr[ei, si, mi, oi, di]
                        times = C.times_arr[ei, si, mi, oi, di]
                        struct = C.struct_arr[ei, si, mi, oi, di]
                        num_times = int( sum(struct) )

                        if num_times == 0:
                            continue

                        # Initialise the function to minimise.
                        setup(num_params=len(C.param_vector), num_times=num_times, values=values, sd=errors, relax_times=times, scaling_matrix=C.scaling_list)

                        results = generic_minimise(func=func, dfunc=dfunc, d2func=d2func, args=(), x0=C.param_vector, min_algor=C.min_algor, min_options=C.min_options, func_tol=C.func_tol, grad_tol=C.grad_tol, maxiter=C.max_iterations, A=C.A, b=C.b, full_output=True, print_flag=C.verbosity)

                        # Unpack
                        param_vector, chi2, iter_count, f_count, g_count, h_count, warning = results

                        chi2_list.append(chi2)

    return chi2_list

# Execute main function.
if __name__ == "__main__":
    main()
