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
"""Module for functions relating to the paramagnetic centre."""

# Python imports.
from numpy.linalg import norm


def paramag_data(atomic_pos, paramag_centre, unit_vector, r):
    """Calculate the electron spin to nuclear spin unit vectors and distances.

    @param atomic_pos:      The atomic positions.  The first index is the spins, the second is the structures, and the third is the atomic coordinates.
    @type atomic_pos:       numpy rank-3 array
    @param paramag_centre:  The paramagnetic centre position.
    @type paramag_centre:   numpy rank-1, 3D array
    @param unit_vector:     The structure to fill with the electron spin to nuclear spin unit vectors.
    @type unit_vector:      numpy rank-3 array
    @param r:               The structure to fill with the electron spin to nuclear spin distances.
    @type r:                numpy rank-2 array
    """

    # Loop over the spins.
    for i in range(len(atomic_pos)):
        # Loop over the states.
        for c in range(len(atomic_pos[i])):
            # The vector.
            vect = atomic_pos[i, c] - paramag_centre

            # The length.
            r[i, c] = norm(vect)

            # The unit vector.
            unit_vector[i, c] = vect / r[i, c]

            # Convert the distances from Angstrom to meters.
            r[i, c] = r[i, c] * 1e-10
