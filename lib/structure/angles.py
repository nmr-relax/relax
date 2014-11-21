###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
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
from math import pi
from numpy import arccos, float64, zeros


def angles_regular(inc=None):
    """Determine the spherical angles for a regular sphere point distribution.

    @keyword inc:   The number of increments in the distribution.
    @type inc:      int
    @return:        The phi angle array and the theta angle array.
    @rtype:         array of float, array of float
    """

    # Generate the increment values of u.
    u = zeros(inc, float64)
    val = 1.0 / float(inc)
    for i in range(inc):
        u[i] = float(i) * val

    # Generate the increment values of v.
    v = zeros(int(inc/2.0+1.0), float64)
    val = 1.0 / float(inc/2.0)
    for i in range(int(inc/2.0+1.0)):
        v[i] = float(i) * val

    # Generate the distribution of spherical angles theta.
    theta = 2.0 * pi * u

    # Generate the distribution of spherical angles phi (from bottom to top).
    phi = zeros(len(v), float64)
    for i in range(len(v)):
        phi[len(v)-1-i] = pi * v[i]

    # Return the angle arrays.
    return phi, theta


def angles_uniform(inc=None):
    """Determine the spherical angles for a uniform sphere point distribution.

    @keyword inc:   The number of increments in the distribution.
    @type inc:      int
    @return:        The phi angle array and the theta angle array.
    @rtype:         array of float, array of float
    """

    # Generate the increment values of u.
    u = zeros(inc, float64)
    val = 1.0 / float(inc)
    for i in range(inc):
        u[i] = float(i) * val

    # Generate the increment values of v.
    v = zeros(int(inc/2.0+2.0), float64)
    val = 1.0 / float(inc/2.0)
    for i in range(1, int(inc/2.0)+1):
        v[i] = float(i-1) * val + val/2.0
    v[-1] = 1.0

    # Generate the distribution of spherical angles theta.
    theta = 2.0 * pi * u

    # Generate the distribution of spherical angles phi.
    phi = arccos(2.0 * v - 1.0)

    # Return the angle arrays.
    return phi, theta
