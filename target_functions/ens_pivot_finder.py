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
"""Module for the target function for handling all types of structural superimpositions."""

# Python module imports.
from copy import deepcopy

# relax module import.
from pipe_control.structure.statistics import atomic_rmsd
from pipe_control.structure.superimpose import fit_to_mean


class Pivot_finder:
    """Class for finding the optimal pivot point for motions between the given models."""

    def __init__(self, models, coord):
        """Set up the class for pivot point optimisation for an ensemble of structures.

        @keyword models:    The list of models to use.  If set to None, then all models will be used.
        @type models:       list of int or None
        @keyword coord:     The array of molecular coordinates.  The first dimension corresponds to the model, the second the atom, the third the coordinate.
        @type coord:        rank-3 numpy array
        """

        # Store the args.
        self.models = models
        self.coord = coord

        # Store a copy of the coordinates for restoration.
        self.orig_coord = deepcopy(coord)


    def func(self, params):
        """Target function for the optimisation of the motional pivot point from an ensemble of structures.

        @param params:  The parameter vector from the optimisation algorithm.
        @type params:   list
        @return:        The target function value defined as the combined RMSD value.
        @rtype:         float
        """

        # The fit to mean algorithm.
        T, R, pivot = fit_to_mean(models=self.models, coord=self.coord, centroid=params, verbosity=0)

        # The RMSD.
        val = atomic_rmsd(self.coord)

        # Restore the coordinates.
        self.coord = deepcopy(self.orig_coord)

        # Return the RMSD.
        return val
