###############################################################################
#                                                                             #
# Copyright (C) 2011-2012 Edward d'Auvergne                                   #
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
"""Script for determining the centre of mass of the reference structures.

The CoM is not the real one as only the N, H, and Ca2+ atoms are used.
"""

# relax module imports.
from pipe_control.structure.mass import centre_of_mass


# The PDB files.
files = [
    '1J7O_1st_NH.pdb',
    '1J7P_1st_NH.pdb',
    '1J7P_1st_NH_rot.pdb'
]

# Loop over each PDB file.
for name in files:
    # Create a separate data pipe for each.
    pipe.create(name, 'N-state')

    # Load the file.
    structure.read_pdb(name)

    # Calculate the CoM.
    centre_of_mass()
