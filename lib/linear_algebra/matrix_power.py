###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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
from numpy import diag, dot, eye
from numpy.linalg import eig, inv

# relax module imports.
from lib.errors import RelaxError


def square_matrix_power(x, y):
    """Compute x raised to the power y when x is a square matrix and y is a scalar.

    @param x:   The square matrix.
    @type x:    numpy rank-2 array
    @param y:   The power.
    @type y:    float
    @return:    The matrix power of x.
    @rtype:     numpy rank-2 array
    """

    # Sanity check.
    s = x.shape()
    if len(s) != 2 or s[0] != s[1]:
        raise RelaxError("The matrix '%s' must be square." % x)

    # Catch the zeroth power.
    if y == 0:
        return eye(s[0])

    # The eigensystem of x.
    e, v = eig(x)
    d = diag(e)

    # Return the matrix power.
    return dot(dot(v, d**y), inv(v))

