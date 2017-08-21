###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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
"""Create a PDB file with a symmetric 'molecule' with CoM at [1, 1, 1]."""

# Python module imports.
from numpy import array, float64, ones, zeros
from numpy.linalg import norm


# Create the data pipe.
pipe.create('fancy mol', 'N-state')

# Initialise some variables.
com = ones(3, float64)
radius = 5.0
r = 1.02

# Add some 15N and 1H atoms.
index = 0
for i in range(3):
    # Loop over the positive and negative directions.
    for j in [-1, 1]:
        # The positions.
        posN = zeros(3, float64)
        posN[i] = j * radius
        posN += com
        posH = zeros(3, float64)
        posH[i] = j * (radius + r)
        posH += com

        # Add the 15N.
        structure.add_atom(atom_name='N', res_name='GLY', res_num=index, pos=posN, element='N')

        # Add the 1H.
        structure.add_atom(atom_name='H', res_name='GLY', res_num=index, pos=posH, element='H')

        # Increment the atom index.
        index += 1

# Diagonals.
pos = array([
    [ 1,  1,  1],
    [-1, -1, -1],
    [-1,  1,  1],
    [ 1, -1, -1],
    [ 1, -1,  1],
    [-1,  1, -1],
    [ 1,  1, -1],
    [-1, -1,  1]
], float64)
for i in range(len(pos)):
    # Normalise.
    pos[i] = pos[i] / norm(pos[i])

    # The positions.
    posN = pos[i] * radius + r*pos[i] + com
    posH = pos[i] * radius + com

    # Add the 15N.
    structure.add_atom(atom_name='N', res_name='GLY', res_num=i+6, pos=posN, element='N')

    # Add the 1H.
    structure.add_atom(atom_name='H', res_name='GLY', res_num=i+6, pos=posH, element='H')

    # Increment the atom index.
    index += 1

# Write out the PDB file.
structure.write_pdb('fancy_mol.pdb', force=True)
