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
from numpy import array, arange, int32, float64, pi, load
import pstats
import sys
import tempfile

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


# Alter setup.
def main():
    param_key_list = [
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
    NE, NS, NM, NO, ND, NT = 1, 1, 1, 6, 6, 5

    # Define path to data
    data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'curve_fitting'+sep+'profiling'+sep

    values_arr = load(data_path + "values_arr.npy")
    errors_arr = load(data_path + "errors_arr.npy")
    times_arr = load(data_path + "times_arr.npy")
    struct_arr = load(data_path + "struct_arr.npy")

    # Print arrays.
    for ei in range(NE):
        for si in range(NS):
            for mi in range(NM):
                for oi in range(NO):
                    for di in range(ND):
                        print(ei, si, mi, oi, di, values_arr[ei, si, mi, oi, di], struct_arr[ei, si, mi, oi, di])


# Execute main function.
if __name__ == "__main__":
    main()
