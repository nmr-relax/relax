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
"""Create a PDB representation for the real pivot point used to generate the data."""

# relax module imports.
from lib.io import open_write_file
from lib.structure.internal.object import Internal


# Create the structural object.
structure = Internal()

# Add a molecule.
structure.add_molecule(name='piv')

# Alias the single molecule from the single model.
mol = structure.structural_data[0].mol[0]

# Add the original pivot.
mol.atom_add(atom_name='N', res_name='PIV', res_num=1, pos=[ 37.254, 0.5, 16.7465], element='N')

# Add the shifted pivot.
mol.atom_add(atom_name='N', res_name='SFT', res_num=2, pos=[ 38.968163825736738,   2.6192628972111,   13.499077238576398], element='N')

# Save as a PDB file.
file = open_write_file('pivot_point.pdb', force=True)
structure.write_pdb(file)
file.close()


