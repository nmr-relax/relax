###############################################################################
#                                                                             #
# Copyright (C) 2008-2013 Edward d'Auvergne                                   #
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

"""Script for creating a PDB representation of the distribution of XH bond vectors."""


# Python module imports.
from os import pardir, sep


# Create the data pipe.
pipe.create('vectors', 'mf')

# Load the PDB file.
structure.read_pdb('test.pdb')

# Load the backbone amide 15N and 1H spins from the structure.
structure.load_spins(spin_id='@N')
structure.load_spins(spin_id='@H')

# Select solely the NH vectors used in the analysis.
select.read(file=pardir+sep+'rates.txt', change_all=True, res_num_col=2)

# Set up the NH vectors.
interatom.define(spin_id1='@N', spin_id2='@H')
interatom.unit_vectors()

# Create the PDB file representing the vector distribution.
structure.create_vector_dist(file='vect_dist.pdb', force=True)

# Display the structure and distribution in PyMOL.
pymol.view()
pymol.cartoon()
pymol.vector_dist()
