###############################################################################
#                                                                             #
# Copyright (C) 2010 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful;                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for transforming between different coordinate systems."""

# Python module imports.
from math import acos, atan2
from numpy import array, float64
from numpy.linalg import norm


def cartesian_to_spherical(vector):
    """Convert the Cartesian vector [x, y, z] to spherical coordinates [r, phi, theta].

    The parameter r is the radial distance, phi is the polar angle, and theta is the azimuth.


    @param vector:  The Cartesian vector [x, y, z].
    @type vector:   numpy rank-1, 3D array
    @return:        The spherical coordinate vector [r, phi, theta].
    @rtype:         numpy rank-1, 3D array
    """

    # The radial distance.
    r = norm(vector)

    # Unit vector.
    unit = vector / r

    # The polar angle.
    phi = acos(unit[2])

    # The azimuth.
    theta = atan2(unit[1], unit[0])

    # Return the spherical coordinate vector.
    return array([r, phi, theta], float64)
