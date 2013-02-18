###############################################################################
#                                                                             #
# Copyright (C) 2011-2013 Edward d'Auvergne                                   #
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
"""Module for handling all types of structural statistics."""

# Python module imports.
from numpy import float64, mean, sqrt, std, zeros
from numpy.linalg import norm


def atomic_rmsd(coord, verbosity=0):
    """Determine the RMSD for the given atomic coordinates.

    This is the per atom RMSD to the mean structure.


    @keyword coord:     The array of molecular coordinates.  The first dimension corresponds to the model, the second the atom, the third the coordinate.
    @type coord:        rank-3 numpy array
    @return:            The RMSD value.
    @rtype:             float
    """

    # Init.
    M = len(coord)
    N = len(coord[0])
    model_rmsd = zeros(M, float64)
    mean_str = zeros((N, 3), float64)

    # Calculate the mean structure.
    calc_mean_structure(coord, mean_str)

    # Loop over the models.
    for i in range(M):
        # Loop over the atoms.
        for j in range(N):
            # The vector connecting the mean to model atom.
            vect = mean_str[j] - coord[i][j]

            # The atomic RMSD.
            model_rmsd[i] += norm(vect)**2

        # Normalise, and sqrt.
        model_rmsd[i] = sqrt(model_rmsd[i] / N)

        # Print out.
        if verbosity:
            print("Model %2s RMSD:  %s" % (i, model_rmsd[i]))

    # Calculate the mean and standard deviation.
    rmsd_mean = mean(model_rmsd)
    rmsd_sd = std(model_rmsd, ddof=1)
    if verbosity:
        print("\nGlobal RMSD:  %s +/- %s" % (rmsd_mean, rmsd_sd))

    # Return the average RMSD.
    return rmsd_mean


def calc_mean_structure(coord=None, mean=None):
    """Average the coordinates.

    @keyword coord:     The list of coordinates of all models to superimpose.  The first index is the models, the second is the atomic positions, and the third is the xyz coordinates.
    @type coord:        list of numpy rank-2, Nx3 arrays
    @keyword mean:      The data storage for the mean structure.
    @type mean:         numpy rank-2, Nx3 array
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
