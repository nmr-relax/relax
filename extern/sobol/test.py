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
from numpy import float64, ones, zeros
from numpy.linalg import norm

# relax module imports.
from extern.sobol.sobol_lib import i4_sobol


# Some variables.
DIM = 3
OFFSET = 0.5 * ones(DIM)

# Loop over different number of points.
for exponent in range(7):
    # The number of points.
    N = int(10**exponent)

    # Initialise a vector.
    ave_pos = zeros(DIM, float64)

    # Print out.
    print("\nN = %s" % N)

    # Loop over the points.
    for i in range(N):
        # The raw point.
        point, seed = i4_sobol(DIM, i)

        # Sum the point, minus the offset.
        ave_pos += point - OFFSET

    # The average vector length.
    ave_pos = ave_pos / float(N)
    r = norm(ave_pos)
    print("Average vector length: %s" % r)
