###############################################################################
#                                                                             #
# Copyright (C) 2006-2008 Edward d'Auvergne                                   #
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

"""Script for creating a PDB representation of the Brownian rotational diffusion tensor."""


# Create the data pipe.
name = 'sims'
pipe.create(name, 'mf')

# Read the results.
results.read(dir=None)

# Display the diffusion tensor.
diffusion_tensor.display()

# Create the tensor PDB file.
tensor_file = 'tensor.pdb'
structure.create_diff_tensor_pdb(file=tensor_file, force=True)

# PyMOL.
pymol.view()
pymol.cartoon()
pymol.tensor_pdb(file=tensor_file)
