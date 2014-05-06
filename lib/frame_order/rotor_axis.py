###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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
"""Functions for creating or calculating the rotor axis for the frame order models."""

# Python module imports.
from numpy import array, cross, dot, float64, zeros
from numpy.linalg import norm

# relax module imports.
from lib.geometry.coord_transform import spherical_to_cartesian
from lib.geometry.rotations import axis_angle_to_R, euler_to_R_zyz

# Module variables.
R = zeros((3, 3), float64)    # A rotation matrix.
Z_AXIS = array([0, 0, 1], float64)


def create_rotor_axis_alpha(alpha=None, pivot=None, point=None):
    """Create the rotor axis from the axis alpha angle.

    @keyword alpha: The axis alpha angle, defined as the angle between a vector perpendicular to the pivot-CoM vector in the xy-plane and the rotor axis.
    @type alpha:    float
    @keyword pivot: The pivot point on the rotation axis.
    @type pivot:    numpy rank-1 3D array
    @keyword point: The reference point in space.
    @type point:    numpy rank-1 3D array
    @return:        The rotor axis as a unit vector.
    @rtype:         numpy rank-1 3D float64 array
    """

    # The CoM-pivot unit vector - the norm of the system (the pivot is defined as the point on the axis closest to the point).
    n = point - pivot
    n /= norm(n)

    # The vector perpendicular to the CoM-pivot vector and in the xy plane.
    mu_xy = cross(Z_AXIS, n)
    mu_xy /= norm(mu_xy)

    # Rotate the vector about the CoM-pivot axis by the angle alpha.
    axis_angle_to_R(n, alpha, R)
    axis = dot(R, mu_xy)

    # Return the new axis.
    return axis


def create_rotor_axis_euler(alpha=None, beta=None, gamma=None):
    """Create the rotor axis from the Euler angles.

    @keyword alpha: The alpha Euler angle in the zyz notation.
    @type alpha:    float
    @keyword beta:  The beta Euler angle in the zyz notation.
    @type beta:     float
    @keyword gamma: The gamma Euler angle in the zyz notation.
    @type gamma:    float
    @return:        The rotor axis as a unit vector.
    @rtype:         numpy rank-1 3D float64 array
    """

    # Initialise the 3D frame.
    frame = zeros((3, 3), float64)

    # Euler angle to rotation matrix conversion.
    euler_to_R_zyz(alpha, beta, gamma, frame)

    # Return the z-axis component.
    return frame[:, 2]


def create_rotor_axis_spherical(theta=None, phi=None):
    """Create the rotor axis from the spherical coordinates.

    @keyword theta: The polar spherical angle.
    @type theta:    float
    @keyword phi:   The azimuthal spherical angle.
    @type phi:      float
    @return:        The rotor axis as a unit vector.
    @rtype:         numpy rank-1 3D float64 array
    """

    # Initialise the axis.
    axis = zeros(3, float64)

    # Parameter conversion.
    spherical_to_cartesian([1.0, theta, phi], axis)

    # Return the new axis.
    return axis
