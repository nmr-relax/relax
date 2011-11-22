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
from copy import deepcopy
from math import pi
from numpy import diag, dot, eye, float64, outer, sign, transpose, zeros
from numpy.linalg import det, norm, svd

# relax module import.
from maths_fns.rotation_matrix import R_to_axis_angle


def calc_mean_structure(coord=None, mean=None):
    """Average the coordinates.

    @keyword coord:     The list of coordinates of all models to superimpose.  The first index is the models, the second is the atomic positions, and the third is the xyz coordinates.
    @type coord:        list of numpy rank-2, Nx3 arrays
    @keyword mean:      The data storage for the mean structure.
    @type coord:        numpy rank-2, Nx3 array
    """

    # The number of atoms.
    N = len(coord[0])
    M = len(coord)

    # Clear the mean data structure.
    for i in range(N):
        mean[i] = [0.0, 0.0, 0.0]

    # Loop over the atoms.
    for i in range(N):
        # Loop over the models.
        for j in range(M):
            mean[i] += coord[j][i]

        # Average.
        mean[i] = mean[i] / M


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


def fit_to_first(models=None, coord=None, centroid=None):
    """Superimpose a set of structural models using the fit to first algorithm.

    @keyword models:    The list of models to superimpose.
    @type models:       list of int
    @keyword coord:     The list of coordinates of all models to superimpose.  The first index is the models, the second is the atomic positions, and the third is the xyz coordinates.
    @type coord:        list of numpy rank-2, Nx3 arrays
    @keyword centroid:  An alternative position of the centroid to allow for different superpositions, for example of pivot point motions.
    @type centroid:     list of float or numpy rank-1, 3D array
    @return:            The lists of translation vectors, rotation matrices, and rotation pivots.
    @rtype:             list of numpy rank-1 3D arrays, list of numpy rank-2 3D arrays, list of numpy rank-1 3D arrays
    """

    # Print out.
    print("\nSuperimposition of structural models %s using the 'fit to first' algorithm." % models)

    # Init (there is no transformation for the first model).
    T_list = [zeros(3, float64)]
    R_list = [eye(3, dtype=float64)]
    pivot_list = [zeros(3, float64)]

    # Loop over the ending models.
    for i in range(1, len(models)):
        # Calculate the displacements (Kabsch algorithm).
        trans_vect, trans_dist, R, axis, angle, pivot = kabsch(name_from='model %s'%models[0], name_to='model %s'%models[i], coord_from=coord[i], coord_to=coord[0], centroid=centroid)

        # Store the transforms.
        T_list.append(trans_vect)
        R_list.append(R)
        pivot_list.append(pivot)

    # Return the transform data.
    return T_list, R_list, pivot_list


def fit_to_mean(models=None, coord=None, centroid=None):
    """Superimpose a set of structural models using the fit to first algorithm.

    @keyword models:    The list of models to superimpose.
    @type models:       list of int
    @keyword coord:     The list of coordinates of all models to superimpose.  The first index is the models, the second is the atomic positions, and the third is the xyz coordinates.
    @type coord:        list of numpy rank-2, Nx3 arrays
    @keyword centroid:  An alternative position of the centroid to allow for different superpositions, for example of pivot point motions.
    @type centroid:     list of float or numpy rank-1, 3D array
    @return:            The lists of translation vectors, rotation matrices, and rotation pivots.
    @rtype:             list of numpy rank-1 3D arrays, list of numpy rank-2 3D arrays, list of numpy rank-1 3D arrays
    """

    # Print out.
    print("\nSuperimposition of structural models %s using the 'fit to mean' algorithm." % models)

    # Duplicate the coordinates.
    orig_coord = deepcopy(coord)

    # Initialise the displacement lists.
    T_list = []
    R_list = []
    pivot_list = []

    # Initialise the mean structure.
    N = len(coord[0])
    mean = zeros((N, 3), float64)

    # Iterative fitting to mean.
    converged = False
    iter = 0
    while not converged:
        # Print out.
        print("\nIteration %i of the algorithm." % iter)
        print("%-10s%-25s%-25s" % ("Model", "Translation (Angstrom)", "Rotation (deg)"))

        # Calculate the mean structure.
        calc_mean_structure(coord, mean)

        # Fit each model to the mean.
        converged = True
        for i in range(len(models)):
            # Calculate the displacements (Kabsch algorithm).
            trans_vect, trans_dist, R, axis, angle, pivot = kabsch(name_from='model %s'%models[0], name_to='mean', coord_from=coord[i], coord_to=mean, centroid=centroid, verbosity=0)

            # Table print out.
            print("%-10i%25.3g%25.3g" % (i, trans_dist, (angle / 2.0 / pi * 360.0)))

            # Shift the coordinates.
            print coord[i][0]
            for j in range(N):
                # Translate.
                coord[i][j] += trans_vect

                # The pivot to atom vector.
                coord[i][j] -= pivot

                # Rotation.
                coord[i][j] = dot(R, coord[i][j])

                # The new position.
                coord[i][j] += pivot
            print coord[i][0]

            # Convergence test.
            if trans_dist > 1e-10 or angle > 1e-10:
                converged = False

        # Increment the iteration number.
        iter += 1

    # Perform the fit once from the original coordinates to obtain the full transforms.
    for i in range(len(models)):
        # Calculate the displacements (Kabsch algorithm).
        trans_vect, trans_dist, R, axis, angle, pivot = kabsch(name_from='model %s'%models[i], name_to='the mean structure', coord_from=orig_coord[i], coord_to=mean, centroid=centroid)

        # Store the transforms.
        T_list.append(trans_vect)
        R_list.append(R)
        pivot_list.append(pivot)

    # Return the transform data.
    return T_list, R_list, pivot_list


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
    @return:                The translation vector T, translation distance d, rotation matrix R, rotation axis r, rotation angle theta, and the rotational pivot defined as the centroid of the ending structure.
    @rtype:                 numpy rank-1 3D array, float, numpy rank-2 3D array, numpy rank-1 3D array, float, numpy rank-1 3D array
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
        print("\n\nCalculating the rotational and translational displacements from %s to %s using the Kabsch algorithm.\n" % (name_from, name_to))
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
    return trans_vect, trans_dist, R, axis, angle, centroid_to


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
