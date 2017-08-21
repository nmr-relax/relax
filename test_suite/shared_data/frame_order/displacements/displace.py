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
"""Rotate and translate the pseudo-molecule."""

# Python module imports.
from numpy import array, float64, transpose, zeros

# relax module imports.
from lib.geometry.rotations import euler_to_R_zyz, R_to_euler_zyz


# Create a data pipe for the data.
pipe.create('displace', 'N-state')

# Load the structure.
structure.read_pdb('fancy_mol.pdb')

# First rotate.
R = zeros((3, 3), float64)
euler_to_R_zyz(1, 2, 3, R)
origin = array([1, 1, 1], float64)
structure.rotate(R=R, origin=origin)

# Then translate.
T = array([1, 2, 3], float64)
structure.translate(T=T)

# Write out the new structure.
structure.write_pdb('displaced.pdb', force=True)

# Printout of the inverted Euler angles of rotation (the solution).
a, b, g = R_to_euler_zyz(transpose(R))
print("alpha: %s" % a)
print("beta:  %s" % b)
print("gamma: %s" % g)
