###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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

"""Script for creating a PDB representation of the distribution of XH bond vectors."""


# Python module imports.
from os import pardir, sep


# Create the data pipe.
pipe.create('vectors', 'mf')

# Load the PDB file.
structure.read_pdb('test.pdb', parser='scientific')

# Load the backbone amide nitrogen spins from the structure.
structure.load_spins(spin_id='@N')

# Select solely the NH vectors used in the analysis.
select.read(file=pardir+sep+'rates.txt', change_all=True, res_num_col=2)

# Extract the XH vectors.
structure.vectors()

# Create the PDB file representing the vector distribution.
structure.create_vector_dist(force=True)

# Display the structure and distribution in PyMOL.
pymol.view()
pymol.cartoon()
pymol.vector_dist()
