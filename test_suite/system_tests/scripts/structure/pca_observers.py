###############################################################################
#                                                                             #
# Copyright (C) 2015 Edward d'Auvergne                                        #
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

# Python module imports.
from os import sep

# relax imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Missing temp directory (allow this script to run outside of the system test framework).
if not hasattr(ds, 'tmpdir'):
    ds.tmpdir = 'temp_script'

# Create a data pipe.
pipe.create('pca test', 'N-state')

# Load the structures.
path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'pca'
structure.read_pdb('distribution.pdb', dir=path, read_mol=1, set_mol_name='CaM A')
structure.read_pdb('distribution.pdb', dir=path, read_mol=4, set_mol_name='CaM A', merge=True)

# Create a reference structure.
pipe.create('ref', 'N-state')
structure.read_pdb('distribution.pdb', dir=path, read_mol=1, read_model=1, set_mol_name='CaM A')
structure.translate([10.0, 10.0, 10.0])
pipe.switch('pca test')

# PCA analysis.
structure.pca(pipes=['pca test', 'ref'], obs_pipes=['ref'], dir=ds.tmpdir)

# Save the program state.
state.save(force=True, dir=ds.tmpdir)
