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
# relax is distributed in the hope that it will be useful,                    #
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
"""Module containing all the different cone type classes."""

# Python module imports.
from math import cos, sqrt, sin


class Iso_cone:
    """The class for the isotropic cone."""

    def __init__(self, angle):
        """Set up the cone object.

        @param angle:   The cone angle.
        @type angle:    float
        """

        # Store the cone angle.
        self._angle = angle


    def phi_max(self, theta):
        """Return the maximum polar angle phi for the given azimuthal angle theta.

        @param theta:   The azimuthal angle.
        @type theta:    float
        @return:        The maximum polar angle phi for the value of theta.
        @rtype:         float
        """

        # The polar angle is fixed!
        return self._angle


class Pseudo_elliptic:
    """The class for the pseudo-elliptic cone.

    This is not an elliptic cone!  The pseudo-ellipse is defined by::

        phi_max^2 = phi_x^2 * cos(theta)^2  +  phi_y^2 * sin(theta)^2,

    where phi_max is the maximum polar angle for the given azimuthal angle theta, phi_x is the maximum cone angle along the x-eigenvector, and phi_y is that of the y-eigenvector.  The cone axis is assumed to be the z-axis.
    """

    def __init__(self, phi_x, phi_y):
        """Set up the cone object.

        @param phi_x:   The maximum cone angle along the x-eigenvector.
        @type phi_x:    float
        @param phi_y:   The maximum cone angle along the y-eigenvector.
        @type phi_y:    float
        """

        # Store the cone limits.
        self._phi_x = phi_x
        self._phi_y = phi_y


    def phi_max(self, theta):
        """Return the maximum polar angle phi for the given azimuthal angle theta.

        @param theta:   The azimuthal angle.
        @type theta:    float
        @return:        The maximum polar angle phi for the value of theta.
        @rtype:         float
        """

        # Determine phi_max.
        phi_max = sqrt((self._phi_x * cos(theta))**2 + (self._phi_y * sin(theta))**2)

        # Return the limit.
        return phi_max
