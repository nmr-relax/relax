###############################################################################
#                                                                             #
# Copyright (C) 2008,2011 Edward d'Auvergne                                   #
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
"""System test constructed from Tyler Reddy's bug report at https://web.archive.org/web/https://gna.org/bugs/?12487."""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Path of the relaxation data.
DATA_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep

# A set of user functions executed by the full_analysis.py script.
pipe.create(pipe_name='ellipsoid', pipe_type='mf') 
results.read(file='tylers_peptide_trunc', dir=DATA_PATH+'results_files')
spin.name(name='N')
model_free.remove_tm(spin_id=None)
sequence.display()
structure.read_pdb(file='tylers_peptide_trunc.pdb', dir=DATA_PATH+'structures')
structure.get_pos("@N")
structure.get_pos("@H")
interatom.unit_vectors()
diffusion_tensor.init(params=(1e-08, 0, 0, 0, 0, 0), time_scale=1.0, d_scale=1.0, angle_units='deg', param_types=0, spheroid_type=None, fixed=False)
fix(element='all_spins', fixed=True)
minimise.grid_search(lower=None, upper=None, inc=6, constraints=True, verbosity=1)
