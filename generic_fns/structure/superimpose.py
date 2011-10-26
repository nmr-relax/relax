###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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
"""Module for handling all types of structural superimpositions."""

# Python module imports.
from math import pi
from numpy import diag, dot, float64, outer, sign, transpose, zeros
from numpy.linalg import det, norm, svd

# relax module import.
from maths_fns.rotation_matrix import R_to_axis_angle


def find_centroid(coords):
    """Calculate the centroid of the structural coordinates.

    @keyword coord:     The atomic coordinates.
    @type coord:        numpy rank-2, Nx3 array
    @return:            The centroid.
    @rtype:             numpy rank-1, 3D array
    """

    # The sum.
    centroid = coords.sum(0) / coords.shape[0]

    # Return.
    return centroid


def kabsch(name_from=None, name_to=None, coord_from=None, coord_to=None, centroid=None, verbosity=1):
    """Calculate the rotational and translational displacements between the two given coordinate sets.

    This uses the Kabsch algorithm (http://en.wikipedia.org/wiki/Kabsch_algorithm).


    @keyword name_from:     The name of the starting structure, used for the print outs.
    @type name_from:        str
    @keyword name_to:       The name of the ending structure, used for the print outs.
    @type name_to:          str
    @keyword coord_from:    The list of atomic coordinates for the starting structure.
    @type coord_from:       numpy rank-2, Nx3 array
    @keyword coord_to:      The list of atomic coordinates for the ending structure.
    @type coord_to:         numpy rank-2, Nx3 array
    @keyword centroid:      An alternative position of the centroid, used for studying pivoted systems.
    @type centroid:         list of float or numpy rank-1, 3D array
    @return:                The translation vector T, translation distance d, rotation matrix R, rotation axis r, and rotation angle theta.
    @rtype:                 numpy rank-1 3D array, float, numpy rank-2 3D array, numpy rank-1 3D array, float
    """

    # Calculate the centroids.
    if centroid != None:
        centroid_from = centroid
        centroid_to = centroid
    else:
        centroid_from = find_centroid(coord_from)
        centroid_to = find_centroid(coord_to)

    # The translation.
    trans_vect = centroid_to - centroid_from
    trans_dist = norm(trans_vect)

    # Calculate the rotation.
    R = kabsch_rotation(coord_from=coord_from, coord_to=coord_to, centroid_from=centroid_from, centroid_to=centroid_to)
    axis, angle = R_to_axis_angle(R)

    # Print out.
    if verbosity >= 1:
        print("\n\nCalculating the rotational and translational displacements from model %s to model %s.\n" % (name_from, name_to))
        print("Start centroid:          [%20.15f, %20.15f, %20.15f]" % (centroid_from[0], centroid_from[1], centroid_from[2]))
        print("End centroid:            [%20.15f, %20.15f, %20.15f]" % (centroid_to[0], centroid_to[1], centroid_to[2]))
        print("Translation vector:      [%20.15f, %20.15f, %20.15f]" % (trans_vect[0], trans_vect[1], trans_vect[2]))
        print("Translation distance:    %.15f" % trans_dist)
        print("Rotation matrix:")
        print("   [[%20.15f, %20.15f, %20.15f]" % (R[0, 0], R[0, 1], R[0, 2]))
        print("    [%20.15f, %20.15f, %20.15f]" % (R[1, 0], R[1, 1], R[1, 2]))
        print("    [%20.15f, %20.15f, %20.15f]]" % (R[2, 0], R[2, 1], R[2, 2]))
        print("Rotation axis:           [%20.15f, %20.15f, %20.15f]" % (axis[0], axis[1], axis[2]))
        print("Rotation angle (deg):    %.15f" % (angle / 2.0 / pi * 360.0))

    # Return the data.
    return trans_vect, trans_dist, R, axis, angle


def kabsch_rotation(coord_from=None, coord_to=None, centroid_from=None, centroid_to=None):
    """Calculate the rotation via SVD.

    @keyword coord_from:    The list of atomic coordinates for the starting structure.
    @type coord_from:       numpy rank-2, Nx3 array
    @keyword coord_to:      The list of atomic coordinates for the ending structure.
    @type coord_to:         numpy rank-2, Nx3 array
    @keyword centroid_from: The starting centroid.
    @type centroid_from:    numpy rank-1, 3D array
    @keyword centroid_to:   The ending centroid.
    @type centroid_to:      numpy rank-1, 3D array
    @return:                The rotation matrix.
    @rtype:                 numpy rank-2, 3D array
    """

    # Initialise the covariance matrix A.
    A = zeros((3, 3), float64)

    # Loop over the atoms.
    for i in range(coord_from.shape[0]):
        # The positions shifted to the origin.
        orig_from = coord_from[i] - centroid_from
        orig_to = coord_to[i] - centroid_to

        # The outer product.
        A += outer(orig_from, orig_to)

    # SVD.
    U, S, V = svd(A)

    # The handedness of the covariance matrix.
    d = sign(det(A))
    D = diag([1, 1, d])

    # The rotation.
    R = dot(transpose(V), dot(D, transpose(U)))

    # Return the rotation.
    return R
