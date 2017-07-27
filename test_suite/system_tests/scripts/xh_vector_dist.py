###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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
"""System test for creating a PDB representation of the distribution of XH bond vectors."""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# The paths to the data files.
path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep

# Create the data pipe.
pipe.create('vectors', 'mf')

# Load the PDB file.
structure.read_pdb('Ap4Aase_res1-12.pdb', dir=path+'structures')

# Load the backbone amide 15N and 1H spins from the structure.
structure.load_spins(spin_id='@N')
structure.load_spins(spin_id='@H')

# Set up the XH vectors.
interatom.define(spin_id1='@N', spin_id2='@H')
interatom.unit_vectors()

# Create the PDB file.
structure.create_vector_dist(file='devnull', force=True)
