###############################################################################
#                                                                             #
# Copyright (C) 2004-2014 Edward d'Auvergne                                   #
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
"""Collection of functions for vector operations."""

# Python module imports.
from math import acos, cos, pi, sin
from numpy import array, float64
from numpy.linalg import norm
from random import uniform


def random_unit_vector(vector):
    """Generate a random rotation axis.

    Uniform point sampling on a unit sphere is used to generate a random axis orientation.

    @param vector:  The 3D rotation axis.
    @type vector:   numpy 3D, rank-1 array
    """

    # Random azimuthal angle.
    u = uniform(0, 1)
    theta = 2*pi*u

    # Random polar angle.
    v = uniform(0, 1)
    phi = acos(2.0*v - 1)

    # Random unit vector.
    vector[0] = cos(theta) * sin(phi)
    vector[1] = sin(theta) * sin(phi)
    vector[2] = cos(phi)


def unit_vector_from_2point(point1, point2):
    """Generate the unit vector connecting point 1 to point 2.

    @param point1:  The first point.
    @type point1:   list of float or numpy array
    @param point2:  The second point.
    @type point2:   list of float or numpy array
    @return:        The unit vector.
    @rtype:         numpy float64 array
    """

    # Convert to numpy data structures.
    point1 = array(point1, float64)
    point2 = array(point2, float64)

    # The vector.
    vect = point2 - point1

    # Return the unit vector.
    return vect / norm(vect)
