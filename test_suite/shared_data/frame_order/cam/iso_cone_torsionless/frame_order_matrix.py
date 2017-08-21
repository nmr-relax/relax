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

# Module docstring.
"""Script for calculating the frame order matrix from the rotation matrices."""

# Python module imports.
from numpy import float64, zeros

# relax module imports.
from lib.linear_algebra.kronecker_product import kron_prod
from lib.frame_order.format import print_frame_order_2nd_degree


# Load the matrices.
exec(compile(open('rotation_matrices.py').read(), 'rotation_matrices.py', 'exec'))

# Init the matrix.
matrix = zeros((9, 9), float64)

# Loop over the structures.
for i in range(len(R)):
    matrix += kron_prod(R[i], R[i])

# Average.
matrix = matrix / len(R)

# Print out.
print_frame_order_2nd_degree(matrix)
