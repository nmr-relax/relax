###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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

"""This script performs a model-free analysis for the single model 'm4'."""


# Python module imports.
from os import sep
import sys

# relax imports.
from status import Status; status = Status()


# Path of the files.
path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'bug_18790_negative_error'

# Create the data pipe.
name = 'tm1'
pipe.create(name, 'mf')

# Load the sequence.
sequence.read(file='data.r1.600', dir=path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_name_col=5)

# Load the relaxation data.
relax_data.read(ri_id='R1_600',  ri_type='R1',  frq=600.484*1e6, file='data.r1.600',  dir=path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_name_col=5, data_col=6, error_col=7)
relax_data.read(ri_id='R2_600',  ri_type='R2',  frq=600.484*1e6, file='data.r2.600',  dir=path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_name_col=5, data_col=6, error_col=7)
relax_data.read(ri_id='NOE_600', ri_type='NOE', frq=600.484*1e6, file='data.noe.600', dir=path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_name_col=5, data_col=6, error_col=7)

# Name the spins and set the element type.
spin.name('N')
spin.element('N')

# Create all attached protons.
sequence.attach_protons()

# Define the magnetic dipole-dipole relaxation interaction.
dipole_pair.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
dipole_pair.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10)

# Set up the CSA value.
value.set(-172 * 1e-6, 'csa')

# Set the spin information.
spin.isotope('15N', spin_id='@N')
spin.isotope('1H', spin_id='@H')

# Select the model-free model.
model_free.select_model(model=name)

# Grid search.
grid_search(inc=11, verbosity=1)

# Minimise.
minimise('newton')
