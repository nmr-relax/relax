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
"""Script to determine the displacements of 1J7P_1st_NH_rot_trans to the original structure."""


# Create a data pipe.
pipe.create('displacements', 'N-state')

# Load the structures as models.
structure.read_pdb('1J7P_1st_NH_rot_trans.pdb', set_mol_name='N-dom', set_model_num=1)
structure.read_pdb('1J7P_1st_NH.pdb', set_mol_name='N-dom', set_model_num=2)

# Calculate the displacements.
structure.superimpose(method='fit to first')
