###############################################################################
#                                                                             #
# Copyright (C) 2006-2012 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
###############################################################################

"""Script for creating a PDB representation of the Brownian rotational diffusion tensor."""


# Create the data pipe.
name = 'sims'
pipe.create(pipe_name=name, pipe_type='mf')

# Read a results file containing diffusion tensor data.
results.read(file='results.bz2', dir=None)

# Display the diffusion tensor.
diffusion_tensor.display()

# Create the tensor PDB file.
tensor_file = 'tensor.pdb'
structure.create_diff_tensor_pdb(file=tensor_file, force=True)

# PyMOL visualisation.
pymol.view()
pymol.cartoon()
pymol.tensor_pdb(file=tensor_file)
