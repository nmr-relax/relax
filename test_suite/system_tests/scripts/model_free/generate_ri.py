###############################################################################
#                                                                             #
# Copyright (C) 2004-2012 Edward d'Auvergne                                   #
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

"""Script for back-calculating the relaxation data."""

# Python module imports.
from os import sep
import sys

# relax module imports.
from generic_fns.mol_res_spin import spin_loop
from status import Status; status = Status()


# Create the data pipe.
pipe.create('test', 'mf')

# Load a PDB file.
structure.read_pdb('Ap4Aase_res1-12.pdb', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures')

# Load the spins from the structure.
structure.load_spins(spin_id='@N')
structure.load_spins(spin_id='@H')

# Define the magnetic dipole-dipole relaxation interaction.
dipole_pair.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
dipole_pair.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10)
dipole_pair.unit_vectors()

# Define the CSA relaxation interaction.
value.set(val=-172e-6, param='csa')

# Set the diffusion tensor in the PDB frame (Dxx, Dyy, Dzz, Dxy, Dxz, Dyz).
diffusion_tensor.init((1.340e7, 1.516e7, 1.691e7, 0.000e7, 0.000e7, 0.000e7), param_types=3)

# Set the spin information.
spin.isotope('15N', spin_id='@N')
spin.isotope('1H', spin_id='@H')

# Set the required values.
value.set(val=0.8, param='s2')
value.set(val=20e-12, param='te')

# Select model-free model m2.
model_free.select_model(model='m2')

# Back calculate some relaxation data.
relax_data.back_calc(ri_id='NOE_600', ri_type='NOE', frq=600e6)

# Write the data.
relax_data.write(ri_id='NOE_600', file='devnull', force=True)
