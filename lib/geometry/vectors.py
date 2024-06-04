###############################################################################
#                                                                             #
# Copyright (C) 2004-2005,2008-2010,2013-2014 Edward d'Auvergne               #
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
from math import acos, atan2, cos, pi, sin
from numpy import array, cross, dot, float64, sqrt
from numpy.linalg import norm
from random import uniform


def complex_inner_product(v1=None, v2_conj=None):
    """Calculate the inner product <v1|v2> for the two complex vectors v1 and v2.

    This is calculated as::
                   ___
                   \
        <v1|v2> =   >   v1i . v2i* ,
                   /__
                    i

    where * is the complex conjugate.


    @keyword v1:        The first vector.
    @type v1:           numpy rank-1 complex array
    @keyword v2_conj:   The conjugate of the second vector.  This is already in conjugate form to allow for non-standard definitions of the conjugate (for example Sm* = (-1)^m S-m).
    @type v2_conj:      numpy rank-1 complex array
    @return:            The value of the inner product <v1|v2>.
    @rtype:             float
    """

    # Return the inner product.
    return dot(v1, v2_conj)


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


def vector_angle_acos(vector1, vector2):
    """Calculate the angle between two N-dimensional vectors using the acos formula.

    The formula is::

        angle = acos(dot(a / norm(a), b / norm(b))).


    @param vector1:     The first vector.
    @type vector1:      numpy rank-1 array
    @param vector2:     The second vector.
    @type vector2:      numpy rank-1 array
    @return:            The angle between 0 and pi.
    @rtype:             float
    """

    # Calculate and return the angle.
    return acos(dot(vector1 / norm(vector1), vector2 / norm(vector2)))


def vector_angle_atan2(vector1, vector2):
    """Calculate the angle between two N-dimensional vectors using the atan2 formula.

    The formula is::

        angle = atan2(norm(cross(a, b)), dot(a, b)).

    This is more numerically stable for angles close to 0 or pi than the acos() formula.


    @param vector1:     The first vector.
    @type vector1:      numpy rank-1 array
    @param vector2:     The second vector.
    @type vector2:      numpy rank-1 array
    @return:            The angle between 0 and pi.
    @rtype:             float
    """

    # Calculate and return the angle.
    return atan2(norm(cross(vector1, vector2)), dot(vector1, vector2))


def vector_angle_complex_conjugate(v1=None, v2=None, v1_conj=None, v2_conj=None):
    r"""Calculate the inter-vector angle between two complex vectors using the arccos formula.

    The formula is::

        theta = arccos(Re(<v1|v2>) / (|v1|.|v2|)) ,

    where::
                   ___
                   \ 
        <v1|v2> =   >   v1i . v2i* ,
                   /__
                    i

    and::

        |v1| = Re(<v1|v1>) .


    @keyword v1:        The first vector.
    @type v1:           numpy rank-1 complex array
    @keyword v2:        The second vector.
    @type v2:           numpy rank-1 complex array
    @keyword v1_conj:   The conjugate of the first vector.  This is already in conjugate form to allow for non-standard definitions of the conjugate (for example Sm* = (-1)^m S-m).
    @type v1_conj:      numpy rank-1 complex array
    @keyword v2_conj:   The conjugate of the second vector.  This is already in conjugate form to allow for non-standard definitions of the conjugate (for example Sm* = (-1)^m S-m).
    @type v2_conj:      numpy rank-1 complex array
    @return:            The angle between 0 and pi.
    @rtype:             float
    """

    # The inner products.
    inner_v1v2 = complex_inner_product(v1=v1, v2_conj=v2_conj)
    inner_v1v1 = complex_inner_product(v1=v1, v2_conj=v1_conj)
    inner_v2v2 = complex_inner_product(v1=v2, v2_conj=v2_conj)

    # The normalised inner product, correcting for truncation errors creating ratios slightly above 1.0.
    ratio = inner_v1v2.real / (sqrt(inner_v1v1).real * sqrt(inner_v2v2).real)
    if ratio > 1.0:
        ratio = 1.0

    # Calculate and return the angle.
    return acos(ratio)


def vector_angle_normal(vector1, vector2, normal):
    """Calculate the directional angle between two N-dimensional vectors.

    @param vector1:     The first vector.
    @type vector1:      numpy rank-1 array
    @param vector2:     The second vector.
    @type vector2:      numpy rank-1 array
    @param normal:      The vector defining the plane, to determine the sign.
    @type normal:       numpy rank-1 array
    @return:            The angle between -pi and pi.
    @rtype:             float
    """

    # Normalise the vectors (without changing the original vectors).
    vector1 = vector1 / norm(vector1)
    vector2 = vector2 / norm(vector2)

    # The cross product.
    cp = cross(vector1, vector2)

    # The angle.
    angle = acos(dot(vector1, vector2))
    if dot(cp, normal) < 0.0:
        angle = -angle

    # Return the signed angle.
    return angle
