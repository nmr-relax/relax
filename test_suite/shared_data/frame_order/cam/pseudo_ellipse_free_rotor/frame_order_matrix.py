###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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
from numpy import array, float64, zeros

# relax module imports.
from lib.frame_order.format import print_frame_order_2nd_degree
from lib.linear_algebra.kronecker_product import kron_prod


# Store the rotation matrices.
R = []
exec(compile(open('rotation_matrices.py').read(), 'rotation_matrices.py', 'exec'))
R = array(R)

# Init the frame order matrix.
daeg = zeros((9, 9), float64)

# Loop over the structures, and build the frame order matrix.
for i in range(len(R)):
    # Kronecker product.
    kron = kron_prod(R[i], R[i])

    # Sum
    daeg += kron

# Average.
daeg = daeg / len(R)

# The relax calculated matrix.
fo_calc = array(
        [[    0.3410,   -0.0370,    0.0333,   -0.0370,    0.3252,    0.0411,    0.0333,    0.0411,    0.3338],
         [   -0.0322,    0.3148,    0.0367,   -0.0035,    0.0343,   -0.3163,   -0.3170,   -0.0302,   -0.0021],
         [    0.0264,    0.0490,    0.3115,   -0.3046,   -0.0282,   -0.0166,   -0.0813,    0.3011,    0.0017],
         [   -0.0322,   -0.0035,   -0.3170,    0.3148,    0.0343,   -0.0302,    0.0367,   -0.3163,   -0.0021],
         [    0.3272,    0.0296,   -0.0266,    0.0296,    0.3399,   -0.0329,   -0.0266,   -0.0329,    0.3329],
         [    0.0327,   -0.3010,   -0.0166,   -0.0150,   -0.0349,    0.3044,    0.3011,    0.0474,    0.0022],
         [    0.0264,   -0.3046,   -0.0813,    0.0490,   -0.0282,    0.3011,    0.3115,   -0.0166,    0.0017],
         [    0.0327,   -0.0150,    0.3011,   -0.3010,   -0.0349,    0.0474,   -0.0166,    0.3044,    0.0022],
         [    0.3318,    0.0074,   -0.0067,    0.0074,    0.3350,   -0.0082,   -0.0067,   -0.0082,    0.3332]], float64)

# Print outs.
print_frame_order_2nd_degree(daeg)
print_frame_order_2nd_degree(fo_calc)
print_frame_order_2nd_degree(daeg - fo_calc)
